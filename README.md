# 📚 YourSourceLM

YourSourceLM is a document-grounded Retrieval-Augmented Generation (RAG)
system built with:

-   Python
-   Weaviate (Vector Database)
-   Google Gemini (Embeddings + LLM)
-   Jina AI (Reranking)

It allows users to upload documents and query them intelligently using
semantic search and reranking.

------------------------------------------------------------------------

## 🚀 Features

-   📄 Upload PDF documents
-   ✂️ Smart chunking (1000 size, 100 overlap)
-   🔎 Semantic embedding using Gemini (3072-dim)
-   🗄 Store vectors in Weaviate (manual vectors)
-   🎯 Distance threshold filtering
-   🧠 Jina reranking for improved relevance
-   🤖 Grounded response generation with Gemini
-   🗑 Delete documents by `document_id`
-   🔒 Optional document-level filtering during queries

------------------------------------------------------------------------

## 🏗 Architecture

Upload Document\
→ Chunking\
→ Gemini Embeddings\
→ Weaviate Storage\
→ Query → Embed\
→ Vector Search (Top 15)\
→ Distance Threshold Filtering\
→ Jina Reranking (Top 5)\
→ Top 3 Context Selection\
→ Gemini LLM Response

------------------------------------------------------------------------

## 📂 API Endpoints

### 📥 Upload Document

POST /documents

Returns:

{ "document_id": "uuid", "chunks_inserted": 85 }

------------------------------------------------------------------------

### ❓ Ask Question

GET /query

Request:

{ "query": "Your question here", "document_id": "optional-uuid" }

Behavior: - If `document_id` provided → filtered search - If not
provided → global search across all documents

------------------------------------------------------------------------

### 🗑 Delete Document

DELETE /documents/{document_id}

Deletes all chunks associated with the document.

------------------------------------------------------------------------

## 🧠 Retrieval Safety Mechanisms

### Distance Threshold Filtering

Cosine distance threshold: 0.35

-   \< 0.35 → Relevant\

-   0.35 → Rejected

Prevents hallucination for unrelated queries.

------------------------------------------------------------------------

### Reranking

Model used:

jina-reranker-v3

Improves precision before sending context to LLM.

------------------------------------------------------------------------

## 🛠 Tech Stack

-   FastAPI
-   Weaviate Cloud
-   Google Gemini API
-   Jina AI API
-   PyMuPDF
-   LangChain Text Splitter

------------------------------------------------------------------------

## 📦 Environment Variables

Create `.env` file:

GEMINI_API_KEY=your_key\
WEAVIATE_URL=your_cluster_url\
WEAVIATE_API_KEY=your_key\
JINA_API_KEY=your_key

------------------------------------------------------------------------

## 📊 Embedding Configuration

-   Model: models/gemini-embedding-001
-   Dimension: 3072
-   Distance metric: cosine

------------------------------------------------------------------------

## 🔮 Roadmap (v2)

-   Image support (OCR / multimodal)
-   Website ingestion
-   Table extraction
-   Background ingestion
-   Evaluation & confidence scoring
-   Multi-user support

------------------------------------------------------------------------

## 📌 Current Status

Stable text-based RAG\
Threshold filtering enabled\
Reranking integrated\
Document lifecycle management complete

------------------------------------------------------------------------

## 📜 License

Internal / Project Use
