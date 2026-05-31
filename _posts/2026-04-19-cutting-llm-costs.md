---
title: "Cutting LLM Costs in Half: Caching, Prompt Routing, and Smaller Models"
categories:
    - Tech
tags:
    - ai
    - llmops
    - cost-optimization
    - python
    - learning
toc: true
---

My LLM API bill hit an uncomfortable number a few months ago. Not "time to shut down" territory, but "time to actually think about this" territory. After a few weeks of profiling and experimenting, I got it down by about 55% without meaningfully changing user-facing quality. Here's what worked.

## 1. Semantic Caching

Exact-match caching (cache the response if the prompt string is identical) has terrible hit rates in practice. Users rephrase. Semantic caching fixes this by checking whether an incoming query is semantically similar to a cached query, and returning the cached response if similarity is above a threshold.

```python
import hashlib
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, SearchRequest

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.95):
        self.client = QdrantClient(":memory:")
        self.threshold = similarity_threshold
        self.embed_fn = None  # inject your embedding function
        self.client.create_collection(
            "cache",
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        self._next_id = 0

    def get(self, query: str) -> str | None:
        vector = self.embed_fn(query)
        results = self.client.search("cache", query_vector=vector, limit=1, score_threshold=self.threshold)
        if results:
            return results[0].payload["response"]
        return None

    def set(self, query: str, response: str):
        vector = self.embed_fn(query)
        self.client.upsert("cache", points=[
            PointStruct(
                id=self._next_id,
                vector=vector,
                payload={"query": query, "response": response},
            )
        ])
        self._next_id += 1

cache = SemanticCache(similarity_threshold=0.95)

def cached_completion(query: str, llm_fn) -> str:
    cached = cache.get(query)
    if cached:
        return cached  # free
    response = llm_fn(query)
    cache.set(query, response)
    return response
```

In my workload (a documentation Q&A assistant), the cache hit rate settled around 30% after a week of warming. That's 30% of queries served at embedding cost (~$0.0001) instead of completion cost (~$0.01). At scale that compounds fast.

## 2. Prompt Routing

Not every query needs GPT-4o. A question like "what's the capital of France?" costs the same as a complex multi-step reasoning task if you send both to the same model. Routing based on query complexity routes cheap queries to cheap models.

```python
from openai import OpenAI

client = OpenAI()

def classify_query(query: str) -> str:
    """Returns 'simple' or 'complex'."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # use the cheap model to classify
        messages=[{
            "role": "user",
            "content": f"""Classify this query as 'simple' (factual, one-step, short answer) 
or 'complex' (multi-step reasoning, analysis, code generation, or long-form content).
Reply with only the word 'simple' or 'complex'.

Query: {query}"""
        }],
        max_tokens=5,
    )
    return response.choices[0].message.content.strip().lower()

def routed_completion(query: str, system_prompt: str) -> str:
    complexity = classify_query(query)
    model = "gpt-4o-mini" if complexity == "simple" else "gpt-4o"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
    )
    return response.choices[0].message.content
```

Classification itself costs tokens, so this only pays off if your complex/simple split is skewed. In my case ~70% of queries were simple. The classification call at `gpt-4o-mini` prices added negligible cost, and routing 70% of traffic away from `gpt-4o` cut completion costs substantially.

## 3. Prompt Compression

Longer prompts cost more. LLMLingua and similar tools compress prompts by removing tokens that contribute little to the model's attention, preserving semantic content with 2-4x token reduction.

For RAG specifically, you often retrieve more context than needed. A simple selectiveness pass before sending to the LLM:

```python
def compress_context(query: str, chunks: list[str], target_tokens: int = 1000) -> str:
    """Keep only chunks most relevant to the query, up to token budget."""
    from openai import OpenAI
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    
    # Score each chunk by simple keyword overlap (or use embedding similarity)
    query_words = set(query.lower().split())
    scored = []
    for chunk in chunks:
        overlap = len(query_words & set(chunk.lower().split()))
        scored.append((overlap, chunk))
    scored.sort(reverse=True)

    selected, token_count = [], 0
    for _, chunk in scored:
        chunk_tokens = len(enc.encode(chunk))
        if token_count + chunk_tokens > target_tokens:
            break
        selected.append(chunk)
        token_count += chunk_tokens

    return "\n\n".join(selected)
```

## 4. Local Models for Low-Stakes Tasks

Classification, summarization for internal tools, and content moderation are good candidates for a local quantized model. The quality bar is lower, latency is acceptable, and cost is effectively zero after hardware.

With Ollama, swapping in a local model for classification is one line:

```python
import ollama

def local_classify(query: str) -> str:
    response = ollama.chat(
        model="llama3.2:3b",  # 3B model, runs on CPU
        messages=[{"role": "user", "content": f"Is this query simple or complex? Reply only 'simple' or 'complex'.\n\n{query}"}]
    )
    return response["message"]["content"].strip().lower()
```

## 5. Batching and Async for Non-Interactive Workloads

Nightly jobs, report generation, document processing — anything not user-facing should be batched and run async. OpenAI's Batch API offers 50% cost reduction on batch jobs with up to 24-hour turnaround. For offline workloads, this is a straightforward win.

```python
import asyncio
from openai import AsyncOpenAI

async_client = AsyncOpenAI()

async def process_batch(prompts: list[str], concurrency: int = 20) -> list[str]:
    semaphore = asyncio.Semaphore(concurrency)

    async def process_one(prompt: str) -> str:
        async with semaphore:
            response = await async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content

    return await asyncio.gather(*[process_one(p) for p in prompts])

# Process 1000 documents with controlled concurrency
results = asyncio.run(process_batch(documents, concurrency=20))
```

## What Actually Moved the Needle

Ranked by impact in my specific workload:

1. **Semantic caching**: ~30% reduction — biggest win, especially for repetitive use patterns.
2. **Prompt routing**: ~25% reduction — high leverage if your traffic skews simple.
3. **Prompt compression / context trimming**: ~10% reduction — meaningful but requires tuning.
4. **Local models for classification**: ~5% reduction — small but compound with other optimizations.

None of these required changing the core application logic. They're all layers you add around existing LLM calls.
