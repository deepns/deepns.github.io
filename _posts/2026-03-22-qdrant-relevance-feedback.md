---
title: "Relevance Feedback in Vector Search: Qdrant 1.17's New Query Model"
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

Relevance feedback is an old idea from information retrieval research — roughly: let users indicate which results were useful, then use that signal to refine the query and retrieve better results. It works really well in practice and it's always been a bit awkward to implement in vector databases. Qdrant 1.17's updated query model makes it a first-class operation. Here's what changed and why it matters.

## The Classic IR Concept

In traditional search, Rocchio's algorithm (1971) reformulates a query by moving it toward relevant documents and away from non-relevant ones in vector space:

```
q_new = α * q_original + β * mean(relevant_docs) - γ * mean(non_relevant_docs)
```

The same intuition applies to dense vector search. If a user searches for "minimalist running shoes" and clicks on two results but explicitly skips a third, you can use those three signals to improve the query vector before the next retrieval step. Before Qdrant 1.17, you'd have to implement this yourself: fetch the embeddings of positive and negative examples, do the arithmetic, submit a new search. Manageable but boilerplate-heavy.

## Qdrant 1.17's Query Model

The new `Query` API in Qdrant 1.17 lets you specify positive and negative examples directly as point IDs or raw vectors in a single request. The server handles the vector arithmetic internally.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    QueryRequest,
    RecommendQuery,
    ScoredPoint,
)

client = QdrantClient("localhost", port=6333)

# "More like point 42 and 87, less like point 15"
results: list[ScoredPoint] = client.query_points(
    collection_name="products",
    query=RecommendQuery(
        recommend={
            "positive": [42, 87],   # point IDs of liked items
            "negative": [15],       # point ID of disliked item
        }
    ),
    limit=10,
).points

for point in results:
    print(f"ID: {point.id}, Score: {point.score:.4f}, Payload: {point.payload}")
```

You can also pass raw vectors instead of IDs, which is useful when the positive/negative examples aren't already in the collection:

```python
from qdrant_client.models import VectorInput

results = client.query_points(
    collection_name="products",
    query=RecommendQuery(
        recommend={
            "positive": [VectorInput(vector=[0.1, 0.2, ...])],
            "negative": [42],  # mix of raw vectors and point IDs
        }
    ),
    limit=10,
).points
```

## A Complete Relevance Feedback Loop

Here's a pattern for a search UI that collects implicit feedback and refines results:

```python
from qdrant_client.models import RecommendQuery, Filter, FieldCondition, MatchValue

def initial_search(query_vector: list[float], collection: str, limit: int = 20):
    """First pass: standard vector search."""
    return client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=limit,
    ).points

def refined_search(
    positive_ids: list[int],
    negative_ids: list[int],
    collection: str,
    exclude_seen: bool = True,
    limit: int = 10,
):
    """Second pass: relevance feedback search."""
    seen_ids = positive_ids + negative_ids
    search_filter = None
    if exclude_seen:
        # Don't re-surface results the user already saw
        search_filter = Filter(
            must_not=[FieldCondition(key="id", match=MatchValue(value=id)) 
                      for id in seen_ids]
        )

    return client.query_points(
        collection_name=collection,
        query=RecommendQuery(
            recommend={
                "positive": positive_ids,
                "negative": negative_ids,
            }
        ),
        query_filter=search_filter,
        limit=limit,
    ).points
```

## Use Cases

**Content-based image retrieval.** The canonical case. User uploads a reference image (or clicks a product image), system finds visually similar items. Thumbs-down on a result to filter out that style. This is how reverse image search with taste filtering works.

**"More like this but not like that."** A document management system where users can mark a result as "similar to what I want" or "not this direction." After two or three signals, retrieval converges on what they're actually looking for. Works remarkably well even with sparse feedback.

**Playlist/recommendation refinement.** Initial results are cold-start recommendations. User listens to tracks, skips others. The skip pattern becomes negative examples, plays become positive. Each skip tightens the query.

**Iterative research assistance.** A researcher marks papers as relevant or irrelevant in a literature review tool. The system converges on their specific angle of inquiry without requiring them to write a better query.

## How This Changes Search UX

The practical impact is that you can build search interfaces that improve within a session without any backend state beyond the current set of positive/negative IDs. No separate ML training loop, no user profile storage — just a list of IDs the client sends with each request.

The Qdrant server handles the vector arithmetic, so the latency overhead compared to a standard query is minimal. In my testing, recommendation queries with 3-5 examples ran at roughly the same speed as a single-vector search on the same collection.

The UX pattern I find most natural is thumbs up/down on each result card, with the search automatically refining after every interaction. Users don't need to understand what's happening — they just notice that results get better as they engage.
