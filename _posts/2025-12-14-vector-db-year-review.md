---
title: "Vector Databases in 2025: What Actually Made it to Production"
categories:
    - Tech
tags:
    - ai
    - vector-database
    - rag
    - learning
toc: true
---

Back in October 2024 I wrote a comparison of the vector database landscape — Pinecone, Weaviate, Qdrant, Chroma, pgvector, and the rest. A year and change later, I've seen several of those choices play out in real systems. Some of what I predicted held, some of it didn't. Here's what actually happened.

## How the Landscape Shifted

**Serverless became the default starting point.** Pinecone's serverless tier and Qdrant Cloud's free tier lowered the activation energy for new projects dramatically. Most teams I've talked to started there and only revisited the decision when they hit a pricing cliff or a latency wall. The "just give me a managed vector store" crowd is larger than the infrastructure-minded crowd, and the serverless offerings got genuinely good in 2025.

**pgvector absorbed a huge chunk of the market, quietly.** If your data already lives in Postgres, the operational argument for a separate vector DB is weak. `pgvector` with `pgvecto.rs` or the native HNSW index (added in 0.6) handles most RAG workloads fine up to a few million vectors. The pitch "one less service" won a lot of internal arguments.

```sql
-- Create a table with a vector column
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    metadata JSONB
);

CREATE INDEX ON documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Retrieval
SELECT id, content, 1 - (embedding <=> $1::vector) AS similarity
FROM documents
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

The operational simplicity is real. Backups, access control, migrations — all using tooling your team already knows.

**Qdrant became the go-to for self-hosted production workloads.** Teams that needed performance, didn't want to pay cloud markups, and wanted a dedicated vector store landed on Qdrant more often than not. The Rust-based internals gave it a performance edge that showed up in benchmarks, and the team shipped fast — named vectors, sparse vector support, and better filtering all landed in 2025.

## What Didn't Work Out as Expected

**Weaviate lost ground.** The GraphQL-heavy API was a friction point, and the pricing model for Weaviate Cloud got complicated. Teams that had bet on it weren't necessarily unhappy, but I saw fewer new adoptions.

**Chroma stayed in prototypeland.** It's still the easiest thing to spin up for a demo. It's still not what I'd put in production. The persistence story and query performance at scale never quite matured.

**Hybrid search hype outpaced implementation.** Everyone talked about combining dense and sparse vectors (BM25 + embeddings). In practice, getting the weighting right was tricky, and for many workloads the improvement over pure dense retrieval wasn't worth the added complexity. I'm more selective about recommending it now.

## The Embedding Drift Problem

This one snuck up on people. Your RAG system works great at launch. Six months later, you switch embedding models — maybe because a better one released, or your provider deprecated the old one. Now your stored embeddings are from `text-embedding-ada-002` and your query embeddings are from `text-embedding-3-large`. Similarity scores are meaningless across that boundary.

The fix is straightforward but operationally annoying:

```python
# Tag every embedding with its model at index time
{
    "id": "doc_123",
    "embedding": [...],
    "embedding_model": "text-embedding-3-large",
    "embedding_model_version": "2024-10",
    "indexed_at": "2025-03-14T10:00:00Z"
}

# At query time, check for model mismatch
def retrieve(query: str, collection):
    query_model = "text-embedding-3-large"
    # Filter to only points indexed with the same model
    results = collection.search(
        query_vector=embed(query, model=query_model),
        query_filter={"must": [{"key": "embedding_model", "match": {"value": query_model}}]},
        limit=10,
    )
    return results
```

When you migrate models, you need a re-indexing pipeline. Build that assumption in from day one.

## Updated Pick for 2026

- **New project, don't want to think about infrastructure**: Pinecone serverless or Qdrant Cloud free tier. Get building.
- **Already on Postgres, RAG is one feature not the whole product**: pgvector. Don't add a service you don't need.
- **Self-hosted, performance matters, team has ops capacity**: Qdrant. It's the most actively developed self-hosted option.
- **Multitenancy at scale with complex access control**: Weaviate still has the best story here, despite the other headwinds.

The "right" answer depends on your scale and constraints more than it did in 2024. The landscape matured enough that the differences are real now, not just marketing.
