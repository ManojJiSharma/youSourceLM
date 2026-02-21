import requests
from fastapi import FastAPI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from weaviate.classes.query import MetadataQuery
from weaviate.classes.query import Filter
from google.genai.types import GenerateContentConfig
from google import genai
from dotenv import load_dotenv
import db
import os
load_dotenv()

app = FastAPI()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
History = []


def rerank(query, documents):
    url = "https://api.jina.ai/v1/rerank"

    headers = {
        "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "jina-reranker-v3",
        "query": query,
        "documents": documents,
        "top_n": 5
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def chatting(user_req, dbClient, document_id="") -> str:
    # Embadding configuration
    embeddings = GoogleGenerativeAIEmbeddings(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="models/gemini-embedding-001"
    )

    print("Embadding configuration Done ")

    # Embadding user request
    embedding_query = embeddings.embed_query(user_req)

    # request near vector in weaviate
    collection = dbClient.collections.use("DocumentChunk")
    response_vector = ""
    if document_id == "":
        response_vector = collection.query.near_vector(
            near_vector=embedding_query,
            limit=10,
            return_metadata=MetadataQuery(distance=True)
        )
    else:
        response_vector = collection.query.near_vector(
            near_vector=embedding_query,
            limit=10,
            filters=Filter.by_property("document_id").equal(document_id),
            return_metadata=MetadataQuery(distance=True)
        )

    retrieved_objects = response_vector.objects

    print("retrieved_objects Done ")

    # 1️⃣ Filter by distance
    filtered_objects = [
        obj for obj in retrieved_objects
        if obj.metadata.distance < 0.35
    ]
    if not filtered_objects:
        return {
            "answer": "I could not find relevant information in the provided documents."
        }

    documents = [
        obj.properties["content"]
        for obj in filtered_objects
    ]
    rerank_result = rerank(user_req, documents)


    print("Re-renking done ", len(rerank_result))

    # intrect llm
    History.append({
        'role': 'user',
        'parts': [{user_req}]
    })
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""Answer the question using the provided context.

        Question:
        {user_query}

        Context:
        {rerank_result}

        Chat History
        {History}
        """,
        config=GenerateContentConfig(
            system_instruction="You must answer only using the provided context. If the answer is not in context, say you don't know."
        )
    )
    History.append({
        'role': 'model',
        'parts': [{response.text}]
    })

    return response.text


def user_query(user_req, document_id=""):

    dbClient = db.get_connection()
    respone = ""
    if document_id != "":
        respone = chatting(user_req, dbClient)
    else:
        respone = chatting(user_req, dbClient, document_id)

    dbClient.close()
    return respone
