---
title: "Hybrid Search with Qdrant: Combining Dense and Sparse Vectors"
categories:
    - Tech
tags:
    - ai
    - qdrant
    - vector-database
    - search
    - python
    - learning
toc: true
---

Pure semantic search sounds like the obvious upgrade from keyword search. You embed the query, you embed the documents, you find the nearest neighbors — and you get results that are semantically related even when the words don't match. That's real and useful. But there's a failure mode that bites you in production: if a user searches for "GPT-4o pricing," the semantic search might return documents about model capabilities rather than pricing pages, because "pricing" is a common concept that gets diluted in the embedding. The keyword hit would have nailed it.

Hybrid search — combining dense (semantic) vectors with sparse (keyword) vectors — handles both cases. Qdrant's hybrid search support is among the best available right now.

## The Problem with Pure Dense Search

Dense embeddings capture meaning well but are weak on:
- **Rare or specific terms** — model names, product codes, version numbers, person names
- **Exact keyword requirements** — users who type a specific term usually mean that specific term
- **Domain jargon** — terms that are uncommon in training data but critical in your domain

BM25-style keyword search has the opposite profile: it's precise on exact terms but misses synonyms, related concepts, and paraphrases.

Hybrid search fuses both signals. The standard fusion algorithm is **Reciprocal Rank Fusion (RRF)**, which combines ranked lists from both searches without needing to normalize their scores onto a common scale.

## Sparse Vector Setup in Qdrant

Qdrant supports sparse vectors natively via a separate vector field. You need a sparse encoder — FastEmbed includes `prithvida/Splade_PP_en_v1` which is a good SPLADE model:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, SparseVectorParams, Distance,
    SparseIndexParams
)

client = QdrantClient("localhost", port=6333)

client.create_collection(
    collection_name="hybrid-docs",
    vectors_config={
        "dense": VectorParams(size=384, distance=Distance.COSINE),
    },
    sparse_vectors_config={
        "sparse": SparseVectorParams(
            index=SparseIndexParams(on_disk=False)
        )
    }
)
```

The collection has two vector fields: `dense` for embeddings and `sparse` for SPLADE/BM25 sparse vectors.

## Inserting Documents with Both Vector Types

```python
from qdrant_client.models import PointStruct, SparseVector
from fastembed import TextEmbedding, SparseTextEmbedding

dense_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
sparse_model = SparseTextEmbedding("prithvida/Splade_PP_en_v1")

def embed_document(text: str) -> PointStruct:
    dense_vec = list(dense_model.embed([text]))[0].tolist()
    sparse_result = list(sparse_model.embed([text]))[0]

    return PointStruct(
        id=...,
        payload={"content": text},
        vector={
            "dense": dense_vec,
            "sparse": SparseVector(
                indices=sparse_result.indices.tolist(),
                values=sparse_result.values.tolist()
            )
        }
    )
```

SPLADE sparse vectors are very sparse — typically only 100-300 non-zero entries out of a 30K+ vocabulary — so storage is efficient.

## Hybrid Search with RRF Fusion

Qdrant's Query API handles fusion server-side:

```python
from qdrant_client.models import (
    Query, NearestQuery, FusionQuery, Fusion, Prefetch
)

def hybrid_search(query_text: str, top_k: int = 5) -> list:
    dense_vec = list(dense_model.embed([query_text]))[0].tolist()
    sparse_result = list(sparse_model.embed([query_text]))[0]
    sparse_vec = SparseVector(
        indices=sparse_result.indices.tolist(),
        values=sparse_result.values.tolist()
    )

    results = client.query_points(
        collection_name="hybrid-docs",
        prefetch=[
            Prefetch(query=dense_vec, using="dense", limit=20),
            Prefetch(
                query=sparse_vec,
                using="sparse",
                limit=20
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
        with_payload=True,
    )
    return results.points
```

The `prefetch` step runs both searches and retrieves the top 20 candidates from each. The `FusionQuery(fusion=Fusion.RRF)` then merges and re-ranks them. The final `limit=top_k` returns the top results after fusion.

## When Hybrid Actually Helps

Hybrid search is genuinely better when:
- Your documents contain specific identifiers — version numbers, product SKUs, error codes
- Users tend to use exact search terms (enterprise search, technical docs, code search)
- You have a mix of queries — some conceptual ("how does authentication work") and some exact ("OAuth 2.0 PKCE error 400")

Dense-only search is fine when:
- Queries are always conceptual and paraphrastic
- Your vocabulary is consistent and well-represented in the embedding model's training data
- You want to minimize operational complexity (sparse models add another inference step)

In practice, adding hybrid search to an existing dense retrieval system improves results for a meaningful chunk of queries without hurting the rest. The RRF fusion means there's no hyperparameter to tune for the blend — it's a safe default for most workloads.
