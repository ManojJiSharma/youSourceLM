import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Property, DataType, Configure, VectorDistances

load_dotenv()


weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

def get_connection() -> weaviate.WeaviateClient:
    return weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key),
    )
    

def create_collection() -> weaviate.WeaviateClient:

    client = get_connection()

    if "DocumentChunk" not in client.collections.list_all():
        client.collections.create(
            name="DocumentChunk",

            vector_config=Configure.Vectors.self_provided(
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=VectorDistances.COSINE,
                    # vector_dimension=3072
                ),
            ),

            properties=[
                Property(name="content", data_type=DataType.TEXT),
                Property(name="source_type", data_type=DataType.TEXT),
                Property(name="document_id", data_type=DataType.TEXT),
                Property(name="page_number", data_type=DataType.INT),
                Property(name="chunk_index", data_type=DataType.INT),
            ]
        )

    return client
