from fastapi import FastAPI, File, UploadFile
from weaviate.classes.query import Filter
import os
import db
import chunking_embadding_Data
import retrieval
from uuid import uuid4
app = FastAPI()


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    document_id = str(uuid4())
    file_path = os.path.join("data/", f"{document_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    chunk_size = chunking_embadding_Data.splitter_embadding(
        file_path, document_id)

    return {"filename": file.filename, "document_id": document_id, "chunk_size": chunk_size}


@app.get("/query/")
async def user_query(user_req: str, document_id=""):
    result = retrieval.user_query(user_req, document_id)
    return result


@app.delete("/document/{document_id}")
async def delete_document(document_id: str):
    dbClient = db.get_connection()

    collection = dbClient.collections.use("DocumentChunk")
    
    return collection.data.delete_many(
        where= Filter.by_property("document_id").equal(document_id)
    )