---
title: "Haystack 2.0: A Better Way to Build Production RAG Pipelines"
categories:
    - Tech
tags:
    - ai
    - rag
    - haystack
    - python
    - learning
toc: true
---

I picked up Haystack when I was building a document Q&A system and didn't want to write retrieval boilerplate from scratch. Haystack 1.x was fine, but it had a pipeline model that felt rigid — changing one component often meant rewiring things in ways the framework didn't make obvious. Haystack 2.0 shipped in early 2024 and the architecture change is substantial enough to be worth a proper look.

## What Changed from 1.x to 2.x

The short version: everything is a component now, and components are explicit about their inputs and outputs.

In 1.x, pipelines were built from "Nodes" that communicated through a fixed routing protocol. Swapping an embedder or retriever was possible but the abstractions leaked — you had to understand internals to customize behavior.

In 2.x, every component declares typed `@component` inputs and outputs. The `Pipeline` class is a dataflow graph — it connects components by wiring named outputs to named inputs. There's no magic routing. If a component produces `documents: List[Document]`, you wire that to the next component's `documents` input explicitly.

This makes pipelines debuggable. You can inspect what's flowing between components, and adding a logging component in the middle of a pipeline is trivial.

## How Pipelines Are Composed

The composition model is clean. You add components to a pipeline, then connect them:

```python
from haystack import Pipeline
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator

pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=store))
pipeline.add_component("prompt_builder", PromptBuilder(template=prompt_template))
pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))

pipeline.connect("retriever.documents", "prompt_builder.documents")
pipeline.connect("prompt_builder.prompt", "llm.prompt")
```

The explicit `connect()` calls feel verbose compared to LangChain's pipe operator, but that verbosity pays off when you need to debug a pipeline that's misbehaving at step 3 of 7.

## A Working RAG Pipeline Example

Here's a full minimal RAG pipeline using Haystack 2.0 with an in-memory document store:

```python
from haystack import Document, Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator

# Indexing pipeline
doc_store = InMemoryDocumentStore()
docs = [Document(content="Paris is the capital of France."),
        Document(content="Berlin is the capital of Germany.")]

indexing = Pipeline()
indexing.add_component("embedder", OpenAIDocumentEmbedder())
indexing.add_component("writer", DocumentWriter(document_store=doc_store))
indexing.connect("embedder.documents", "writer.documents")
indexing.run({"embedder": {"documents": docs}})

# Query pipeline
template = """
Given the following context, answer the question.
Context: {% for doc in documents %}{{ doc.content }}{% endfor %}
Question: {{ question }}
"""

query_pipeline = Pipeline()
query_pipeline.add_component("embedder", OpenAITextEmbedder())
query_pipeline.add_component("retriever", InMemoryEmbeddingRetriever(document_store=doc_store))
query_pipeline.add_component("prompt_builder", PromptBuilder(template=template))
query_pipeline.add_component("llm", OpenAIGenerator(model="gpt-4o-mini"))

query_pipeline.connect("embedder.embedding", "retriever.query_embedding")
query_pipeline.connect("retriever.documents", "prompt_builder.documents")
query_pipeline.connect("prompt_builder.prompt", "llm.prompt")

result = query_pipeline.run({
    "embedder": {"text": "What is the capital of France?"},
    "prompt_builder": {"question": "What is the capital of France?"}
})
print(result["llm"]["replies"][0])
```

One quirk: inputs that feed multiple components (like the question string) need to be passed explicitly to each component that consumes them. It feels redundant at first but it's honest about data flow.

## Haystack vs LangChain for Production

This is genuinely context-dependent. My honest take after using both:

**Use Haystack when**: You're building document retrieval systems specifically, you want a more structured abstraction layer, or you've been burned by LangChain's abstraction leaks before. Haystack's components are simpler to test in isolation — a `PromptBuilder` is just a Jinja renderer and you can unit test it without mocking an LLM.

**Use LangChain when**: You need the ecosystem. LangChain has integrations with more tools, more vector stores, and the agent tooling (especially via LangGraph) is more mature. If you're building something that's more agent-y than pipeline-y, LangChain/LangGraph is ahead.

The honest caveat: both frameworks move fast and both have breaking changes. In production, I'd recommend pinning versions tightly and writing integration tests for any pipeline that goes to users.
