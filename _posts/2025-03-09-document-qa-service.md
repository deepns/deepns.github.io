---
title: "Building a Document Q&A Service: From Prototype to Production"
categories:
    - Tech
tags:
    - ai
    - rag
    - fastapi
    - python
    - learning
toc: true
header:
  teaser: /assets/images/teasers/document-qa-service.jpg
---

This is the post I wish I had six months ago when I was trying to take my first RAG prototype and turn it into something I could actually deploy and share with others. The gap between "it works in a Jupyter notebook" and "it works as a service" is where a lot of engineering time disappears.

I'll walk through building a document Q&A service end to end — ingestion, retrieval, FastAPI serving, and the parts that bit me along the way.

---

## What We're Building

A service that:
1. Accepts document uploads (PDF, text, markdown)
2. Chunks and embeds them into a vector store
3. Exposes an API endpoint where you can ask questions about uploaded documents
4. Returns answers with source citations

The architecture is straightforward:

```
Client → FastAPI → RAG Pipeline → LLM
                       ↑
                 Vector Store (Qdrant)
                       ↑
              Document Ingestion Worker
```

The stack: **FastAPI** for the API, **Qdrant** for the vector store (running locally via Docker), **LangChain** for orchestration, **OpenAI** for embeddings and generation.

---

## Project Structure

```
doc-qa-service/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── ingest.py        # Document ingestion pipeline
│   ├── retrieval.py     # Query + generation
│   ├── config.py        # Settings
│   └── models.py        # Pydantic models
├── docker-compose.yml   # Qdrant + service
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Step 1: Configuration

Using Pydantic's `BaseSettings` to manage config — this makes switching between dev and prod environments clean.

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "documents"
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    chunk_size: int = 512
    chunk_overlap: int = 64
    retrieval_k: int = 4

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Step 2: Document Ingestion

The ingestion module handles loading, chunking, and storing documents. I wanted this to be callable both directly and via the API endpoint.

```python
# app/ingest.py
import hashlib
import uuid
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from .config import settings


def get_loader(file_path: str):
    ext = Path(file_path).suffix.lower()
    loaders = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
    }
    loader_class = loaders.get(ext)
    if not loader_class:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader_class(file_path)


def ensure_collection(client: QdrantClient, dimension: int = 1536):
    """Create collection if it doesn't exist."""
    existing = [c.name for c in client.get_collections().collections]
    if settings.collection_name not in existing:
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )


def ingest_document(file_path: str, doc_id: Optional[str] = None) -> dict:
    """
    Load, chunk, embed, and store a document.
    Returns metadata about the ingestion.
    """
    if doc_id is None:
        # Deterministic ID based on file content
        content_hash = hashlib.sha256(
            Path(file_path).read_bytes()
        ).hexdigest()[:16]
        doc_id = content_hash

    loader = get_loader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(docs)

    # Tag each chunk with the doc_id for later filtering
    for chunk in chunks:
        chunk.metadata["doc_id"] = doc_id
        chunk.metadata["source_file"] = Path(file_path).name

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )

    client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    ensure_collection(client)

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=settings.collection_name,
        embedding=embeddings,
    )
    vectorstore.add_documents(chunks)

    return {
        "doc_id": doc_id,
        "chunks_stored": len(chunks),
        "source_file": Path(file_path).name,
    }
```

A few decisions worth noting:
- The deterministic doc_id means re-ingesting the same file is idempotent in terms of tracking, though you'd want deduplication logic in the vector store for production use
- Tagging chunks with `doc_id` allows scoped queries later ("only search within this document")

---

## Step 3: Retrieval and Generation

```python
# app/retrieval.py
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from .config import settings


SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on provided document context.

Rules:
- Answer only based on the context provided
- If the context doesn't contain the answer, say "I don't have enough information in the provided documents to answer this"
- Cite the source document and page number when available
- Be concise but complete

Context:
{context}

Question: {question}

Answer:"""


def get_vectorstore(doc_id: Optional[str] = None) -> QdrantVectorStore:
    client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=settings.collection_name,
        embedding=embeddings,
    )
    return vectorstore


def answer_question(question: str, doc_id: Optional[str] = None) -> dict:
    vectorstore = get_vectorstore()

    retriever_kwargs = {"k": settings.retrieval_k}

    # Optionally scope to a specific document
    if doc_id:
        retriever_kwargs["filter"] = Filter(
            must=[
                FieldCondition(
                    key="metadata.doc_id",
                    match=MatchValue(value=doc_id),
                )
            ]
        )

    retriever = vectorstore.as_retriever(search_kwargs=retriever_kwargs)

    prompt = PromptTemplate(
        template=SYSTEM_PROMPT,
        input_variables=["context", "question"],
    )

    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    result = qa_chain.invoke({"query": question})

    # Extract source citations
    sources = []
    for doc in result.get("source_documents", []):
        sources.append({
            "file": doc.metadata.get("source_file", "unknown"),
            "page": doc.metadata.get("page", None),
            "doc_id": doc.metadata.get("doc_id"),
        })

    # Deduplicate sources
    seen = set()
    unique_sources = []
    for s in sources:
        key = (s["file"], s["page"])
        if key not in seen:
            seen.add(key)
            unique_sources.append(s)

    return {
        "answer": result["result"],
        "sources": unique_sources,
    }
```

---

## Step 4: FastAPI Application

```python
# app/main.py
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .ingest import ingest_document
from .models import QuestionRequest, QuestionResponse, IngestResponse
from .retrieval import answer_question

app = FastAPI(
    title="Document Q&A Service",
    description="Upload documents and ask questions about them",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    """Upload and ingest a document (PDF, TXT, or MD)."""
    allowed = {".pdf", ".txt", ".md"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {allowed}"
        )

    # Write to temp file — the loaders need a file path
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = ingest_document(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return IngestResponse(**result)


@app.post("/ask", response_model=QuestionResponse)
async def ask(request: QuestionRequest):
    """Ask a question about ingested documents."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = answer_question(
        question=request.question,
        doc_id=request.doc_id,
    )
    return QuestionResponse(**result)
```

```python
# app/models.py
from typing import List, Optional
from pydantic import BaseModel


class IngestResponse(BaseModel):
    doc_id: str
    chunks_stored: int
    source_file: str


class QuestionRequest(BaseModel):
    question: str
    doc_id: Optional[str] = None  # Scope to a specific document


class Source(BaseModel):
    file: str
    page: Optional[int] = None
    doc_id: Optional[str] = None


class QuestionResponse(BaseModel):
    answer: str
    sources: List[Source]
```

---

## Step 5: Running It

**docker-compose.yml:**

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_HOST=qdrant
    depends_on:
      - qdrant

volumes:
  qdrant_storage:
```

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**requirements.txt:**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
langchain==0.1.0
langchain-openai==0.0.5
langchain-qdrant==0.0.1
langchain-community==0.0.15
qdrant-client==1.7.0
pypdf==4.0.1
unstructured==0.12.0
pydantic-settings==2.1.0
python-multipart==0.0.6
```

Start everything with:

```bash
export OPENAI_API_KEY="your-key"
docker-compose up
```

---

## Testing the Service

```bash
# Upload a document
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@/path/to/your/document.pdf"

# Response:
# {"doc_id": "a3f2b1c4", "chunks_stored": 47, "source_file": "document.pdf"}

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main conclusions?", "doc_id": "a3f2b1c4"}'

# Response:
# {
#   "answer": "The main conclusions are...",
#   "sources": [{"file": "document.pdf", "page": 12, "doc_id": "a3f2b1c4"}]
# }
```

Interactive API docs at `http://localhost:8000/docs` (FastAPI's built-in Swagger UI).

---

## Lessons from Making This Production-Ready

**Mistake 1: Not handling Qdrant connection failures gracefully.**
The Qdrant client will throw on connection refused. Wrap your vectorstore operations in try/except and return appropriate HTTP status codes.

**Mistake 2: Blocking the event loop during ingestion.**
`ingest_document` is CPU and I/O heavy. For production, move it to a background task or a queue (Celery, ARQ, etc.) and return a job ID immediately.

```python
@app.post("/ingest")
async def ingest(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # ... save file ...
    job_id = str(uuid.uuid4())
    background_tasks.add_task(ingest_document, tmp_path, job_id)
    return {"job_id": job_id, "status": "processing"}
```

**Mistake 3: Not deduplicating on re-upload.**
If someone uploads the same document twice, you get duplicate chunks in the vector store which inflate your results. Use the content hash as doc_id and check if it already exists before re-ingesting.

**Mistake 4: Trusting the LLM to cite correctly.**
The LLM will sometimes fabricate citations. Don't ask the LLM to produce source references — collect them from the retrieved chunks yourself (as shown in the `retrieval.py` above) and append them to the response separately.

---

The service above is functional but the path from here to something truly production-ready involves proper auth, rate limiting, background job processing, observability, and evaluation. I'll cover those in subsequent posts.
