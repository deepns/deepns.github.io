---
title: "Choosing a Vector Database in 2024: Pinecone, Qdrant, Chroma, and pgvector"
categories:
    - Tech
tags:
    - ai
    - vector-database
    - rag
    - learning
toc: true
---

Every RAG tutorial starts with "just use Chroma for now." That's fine for a weekend prototype, but at some point you have to make a real choice. I spent a few weeks evaluating Pinecone, Qdrant, Chroma, and pgvector for a production workload — roughly 5M embeddings, mixed metadata filtering, and latency requirements under 100ms at p95. Here's what I found.

## Why This Comparison Matters

The vector database market moved fast in 2023-2024. Options that were immature a year ago now have production-grade features. The wrong choice early costs you a migration later, and migrating 5M embeddings is not a fun afternoon. The dimensions that matter most in practice are: operational overhead, filtering capability, and whether you can afford a managed service.

## Pinecone

Pinecone is the "just works" option. Fully managed, zero infrastructure to operate, and the SDK is genuinely pleasant. Serverless pods spun up in 2024 made the free tier actually useful for real workloads.

**Strengths**: Zero ops, fast time-to-production, good documentation, solid filtering via metadata.

**Weaknesses**: Vendor lock-in is real — there's no self-hosted option. Pricing can surprise you at scale; egress and query costs add up. No BM25/sparse vector support without their own sparse encoding.

**Best for**: Teams that want to ship fast and don't want to run infrastructure.

```python
from pinecone import Pinecone

pc = Pinecone(api_key="YOUR_API_KEY")
index = pc.create_index(
    name="my-docs",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

index.upsert(vectors=[
    {"id": "doc-1", "values": embedding, "metadata": {"source": "wiki"}}
])
```

## Qdrant

Qdrant is my personal favorite for self-hosted deployments. Written in Rust, it's fast and memory-efficient. The filtering system is the best in class — you can filter on nested JSON fields without pre-declaring a schema. Hybrid search (dense + sparse) shipped in 2024 and it's genuinely good.

**Strengths**: HNSW with on-disk indexing, best-in-class payload filtering, hybrid search via sparse vectors, active development, Docker-friendly.

**Weaknesses**: The managed cloud tier is newer and less battle-tested than Pinecone. Documentation can lag behind features.

**Best for**: Self-hosted production workloads where you need rich filtering and don't want to pay managed pricing.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient("localhost", port=6333)
client.create_collection(
    collection_name="my-docs",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

client.upsert(
    collection_name="my-docs",
    points=[PointStruct(id=1, vector=embedding, payload={"source": "wiki"})]
)
```

## Chroma

Chroma is the developer experience champion. Local-first, embedded mode works with no server, and the Python API is the friendliest of any option here. It's the right choice for prototyping and small datasets.

**Strengths**: Zero setup for local use, great DX, built-in embedding functions so you don't have to wire things yourself.

**Weaknesses**: Performance degrades past ~500K records. Filtering is limited compared to Qdrant. Production deployment is underspecified. The hosted cloud product is still maturing.

**Best for**: Prototypes, notebooks, datasets under 500K vectors.

## pgvector

pgvector is the "use what you have" option. If you're already running PostgreSQL, adding a vector column is a legitimate production strategy. HNSW indexing landed in 0.5.0 and it's fast enough for most workloads.

**Strengths**: No new infrastructure, full SQL joins with your existing data, ACID transactions, you already know how to operate Postgres.

**Weaknesses**: Not as fast as purpose-built vector DBs at scale. HNSW index build time is slower. No hybrid search without rolling your own.

**Best for**: Existing Postgres shops with moderate vector workloads (under 1M rows where query latency isn't sub-10ms critical).

## Comparison Table

| Dimension | Pinecone | Qdrant | Chroma | pgvector |
|---|---|---|---|---|
| Managed option | Yes (only) | Yes + self-hosted | Limited | Via managed PG |
| Self-hosted | No | Yes | Yes | Yes |
| Free tier | Yes (serverless) | Yes (cloud) | Yes (local) | Yes |
| HNSW support | Yes | Yes | Yes | Yes (0.5.0+) |
| Hybrid search | Sparse (limited) | Yes (dense+sparse) | No | No |
| Metadata filtering | Good | Excellent | Basic | SQL |
| Pricing at 5M vecs | $$$ | $ (self-hosted) | Free (self-hosted) | $ (compute) |

## Which One I'd Pick

For a new production deployment with serious filtering requirements and a team that can run Docker: **Qdrant**. The operational overhead is low if you're already running containers, and the filtering and hybrid search capabilities are best in class.

For a team that has zero ops bandwidth: **Pinecone**. The managed experience is real and it does ship fast.

If you're already on PostgreSQL and your embedding count is under 1-2M: **pgvector**. The operational simplicity of not running a second database is underrated.

Chroma is great for what it is — a prototyping tool — but I wouldn't bet a production system on it yet.
