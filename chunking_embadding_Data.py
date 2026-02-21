from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import extract_data
from google import genai
from dotenv import load_dotenv
from google.genai import types
from uuid import uuid4
import os
import time
import db


load_dotenv()

ai = genai.Client()


def splitter_embadding(file_path, document_id) -> int:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(extract_data.extract_text(file_path))

    embeddings = GoogleGenerativeAIEmbeddings(
        api_key=os.getenv("GEMINI_API_KEY"),
        model="models/gemini-embedding-001"
    )

    batch_size = 50
    client = db.create_collection()
    collection = client.collections.use("DocumentChunk")

    for i in range(0, len(texts), batch_size):
        prepared_objects = []
        batch_docs = texts[i:i+batch_size]
        vector = embeddings.embed_documents(
            [doc.page_content for doc in batch_docs])

        for j, doc in enumerate(batch_docs):

            prepared_objects.append({
                "content": doc.page_content,
                "source_type": "pdf",
                "page_number": doc.metadata.get("page"),
                "document_id": document_id,
                "chunk_index": i + j,
                "embedding": vector[j]
            }
            )

            print(len(vector))
            print(len(vector[0]))

        with collection.batch.fixed_size(batch_size=200) as batch:
            for obj in prepared_objects:
                batch.add_object(
                    properties={
                        "content": obj["content"],
                        "source_type": obj["source_type"],
                        "document_id": obj["document_id"],
                        "page_number": obj["page_number"],
                        "chunk_index": obj["chunk_index"],
                    },
                    # required because vector_config=self_provided
                    vector=obj["embedding"],
                )
                if batch.number_errors > 10:
                    print("Batch import stopped due to excessive errors.")
                    break

                failed_objects = collection.batch.failed_objects
                if failed_objects:
                    print(
                        f"Number of failed imports: {len(failed_objects)}")
                    print(f"First failed object: {failed_objects[0]}")
        if len(texts) > 50:
            time.sleep(60)
    client.close()
    return len(texts)

