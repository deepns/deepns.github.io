---
title: "Storing Embeddings in PostgreSQL with pgvector"
categories:
    - Tech
tags:
    - ai
    - postgresql
    - pgvector
    - embeddings
    - python
    - learning
toc: true
---

The pitch for pgvector is simple: you probably already have PostgreSQL running, so why add another database to your stack just for vectors? It sounds too convenient to be true, but after running pgvector in production for a few months with HNSW indexing, I can say it holds up for workloads in the low millions of vectors. Here's a practical walkthrough of setting it up correctly.

## Setup with Docker

The easiest way to get started is with the official pgvector Docker image, which ships PostgreSQL with the extension pre-compiled:

```bash
docker run -d \
  --name pgvector-db \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=embeddings \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Connect with `psql` and enable the extension in your database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

That's it for setup. No configuration files, no separate index server. It's just a Postgres extension.

## Creating the Table

Define a table with a `vector` column. You specify the dimension at column definition time — this must match the dimension of your embeddings:

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source TEXT,
    embedding vector(1536),  -- dimension matches text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

The `vector(1536)` type is what pgvector adds. Postgres enforces dimension consistency — trying to insert a 768-dimensional vector into a `vector(1536)` column raises an error, which is actually useful for catching mismatches early.

## Inserting Embeddings with Python

Using `psycopg2` with pgvector's adapter:

```python
import psycopg2
from pgvector.psycopg2 import register_vector
from openai import OpenAI

conn = psycopg2.connect(
    host="localhost", port=5432,
    dbname="embeddings", user="postgres", password="mysecretpassword"
)
register_vector(conn)  # teaches psycopg2 about the vector type

client = OpenAI()
cursor = conn.cursor()

def embed_and_store(content: str, source: str) -> None:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=content
    )
    embedding = response.data[0].embedding

    cursor.execute(
        "INSERT INTO documents (content, source, embedding) VALUES (%s, %s, %s)",
        (content, source, embedding)
    )
    conn.commit()

embed_and_store("Paris is the capital of France.", "wiki")
embed_and_store("Berlin is the capital of Germany.", "wiki")
```

The `register_vector(conn)` call is important — without it, psycopg2 treats the vector as an opaque string and the insert fails or silently stores garbage.

## Creating an HNSW Index

Before querying at scale, create an HNSW index. Without an index, pgvector falls back to exact sequential scan, which is O(n) and gets slow fast:

```sql
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

The parameters:
- `m`: Number of connections per layer (16 is a good default; higher improves recall at memory cost)
- `ef_construction`: Size of the candidate list during index build (64-128 is typical)

Index build is the expensive step — it's CPU-bound and can take minutes to hours for large tables. Do it before going to production, not after.

## Performing Similarity Search

The `<=>` operator computes cosine distance. Lower is more similar:

```python
def search(query: str, top_k: int = 5) -> list[dict]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding

    cursor.execute("""
        SELECT id, content, source, 1 - (embedding <=> %s) AS similarity
        FROM documents
        ORDER BY embedding <=> %s
        LIMIT %s
    """, (query_embedding, query_embedding, top_k))

    return [
        {"id": row[0], "content": row[1], "source": row[2], "similarity": row[3]}
        for row in cursor.fetchall()
    ]

results = search("What is the capital of France?")
for r in results:
    print(f"[{r['similarity']:.3f}] {r['content']}")
```

The three distance operators: `<=>` (cosine), `<->` (L2/Euclidean), `<#>` (negative inner product). Use cosine for normalized embeddings from OpenAI or similar models.

## When pgvector Beats a Dedicated Vector DB

pgvector wins when:
- Your embedding count is under 2-3M and query latency under 50ms is acceptable
- You need SQL joins between vectors and relational data (filter by user ID, date range, category — all in one query)
- You want ACID transactions covering both metadata and vectors
- You're already paying for managed Postgres (RDS, Supabase, Neon all support pgvector)

A dedicated vector DB (Qdrant, Pinecone) wins when you need sub-10ms queries at 10M+ scale, hybrid search, or real-time ingestion at very high throughput. For everything else, pgvector's "just Postgres" advantage is real and often underestimated.
