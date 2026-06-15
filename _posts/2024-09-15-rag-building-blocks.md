---
title: "Building Blocks of a RAG Pipeline"
categories:
    - Tech
tags:
    - ai
    - rag
    - python
    - langchain
    - learning
toc: true
header:
  teaser: /assets/images/teasers/rag-building-blocks.jpg
---

Over the past year I've watched "RAG" go from a niche research acronym to something that comes up in every engineering discussion involving LLMs. If you've been meaning to understand what it actually is — not the hand-wavy version, but the mechanics — this post is for you.

I want to use this as a foundation post for a series I'm planning on AI Pipelines and applied LLM work. A lot of what I'll write going forward builds on these ideas, so it's worth getting the basics right.

---

## Why RAG Exists

Large language models have a knowledge cutoff. Ask GPT-4 about something that happened last month and it either hallucinates or tells you it doesn't know. More practically, ask it about your company's internal documentation and it definitely doesn't know.

The naive fix is fine-tuning — train the model on your data. The problems: fine-tuning is expensive, slow, and static. Every time your data changes you need to re-train.

**Retrieval-Augmented Generation** (RAG) is the other approach. Instead of baking knowledge into the model weights, you retrieve relevant context at query time and feed it to the model as part of the prompt. The model's job becomes: "given this context, answer this question."

This is powerful because:
- Your knowledge base can be updated without touching the model
- You can trace where the answer came from (the retrieved chunks)
- It works with any LLM — even smaller, cheaper models improve dramatically with good context

---

## The Five Components

A RAG pipeline has five logical pieces. Let me walk through each one.

### 1. Document Ingestion

Before you can retrieve anything, you need to get your documents into a format the pipeline can use. This typically means:

- **Loading**: Reading PDFs, web pages, markdown files, database exports, etc.
- **Chunking**: Splitting long documents into smaller pieces
- **Metadata extraction**: Keeping track of source, date, author

The chunking step is more art than science. Too small and individual chunks lose context. Too large and you're paying for tokens you don't need and diluting relevance.

A simple recursive character splitter is a reasonable starting point:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=64,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_documents(docs)
```

The `chunk_overlap` matters — it ensures that ideas that span chunk boundaries aren't silently cut off.

### 2. Embedding

Each chunk gets converted into a dense vector — a list of floating point numbers that represents the semantic meaning of the text. Semantically similar text ends up close together in this vector space.

The embedding model does this translation. Common choices in late 2024:

- **OpenAI `text-embedding-3-small`** — cheap, good quality, 1536 dimensions
- **OpenAI `text-embedding-3-large`** — higher quality, 3072 dimensions
- **`sentence-transformers/all-MiniLM-L6-v2`** — local, fast, smaller (384 dims)
- **Cohere embed-v3** — strong multilingual support

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Embed a single string
vector = embeddings.embed_query("What is a transformer architecture?")
print(len(vector))  # 1536
```

### 3. Vector Store

The vectors need to live somewhere searchable. A vector store indexes embeddings so you can find the nearest neighbors to a query vector quickly — usually using HNSW (Hierarchical Navigable Small World) or FAISS under the hood.

Options range from in-memory (good for prototyping) to fully managed cloud databases:

| Store | Good for |
|-------|----------|
| ChromaDB | Local development, small datasets |
| FAISS | In-process, large-scale offline search |
| Qdrant | Self-hosted or cloud, production use |
| Pinecone | Fully managed, serverless option |
| pgvector | You already have Postgres |

For a quick local setup with ChromaDB:

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./chroma_db"
)
```

### 4. Retrieval

At query time, the user's question gets embedded using the same model, and you find the `k` most similar chunks in the vector store.

```python
query = "How does attention mechanism work in transformers?"
results = vectorstore.similarity_search(query, k=4)

for doc in results:
    print(doc.metadata)
    print(doc.page_content[:200])
    print("---")
```

This is where a lot of the tuning happens in practice. Raw cosine similarity isn't always what you want. You might want:
- **MMR (Maximal Marginal Relevance)** — balance relevance with diversity so you don't retrieve 4 chunks that all say the same thing
- **Hybrid search** — combine dense (semantic) with sparse (keyword/BM25) retrieval
- **Reranking** — use a second model to re-score the retrieved chunks

### 5. Generation

The retrieved chunks get assembled into a prompt along with the user's question, and sent to an LLM:

```python
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

template = """Use the following context to answer the question.
If you don't know the answer based on the context, say so — don't make things up.

Context:
{context}

Question: {question}

Answer:"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    chain_type_kwargs={"prompt": prompt}
)

response = qa_chain.invoke({"query": "How does attention work?"})
print(response["result"])
```

---

## Putting It All Together

Here's a minimal end-to-end pipeline — load some documents, embed them, store them, and query:

```python
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 1. Load documents
loader = DirectoryLoader("./docs", glob="**/*.md", loader_cls=TextLoader)
docs = loader.load()
print(f"Loaded {len(docs)} documents")

# 2. Chunk
splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
chunks = splitter.split_documents(docs)
print(f"Split into {len(chunks)} chunks")

# 3. Embed + store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 4. Build retrieval chain
template = """Answer based on the context below. Say "I don't know" if the context
doesn't contain the answer.

Context: {context}
Question: {question}
Answer:"""

qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
    chain_type_kwargs={
        "prompt": PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    }
)

# 5. Query
while True:
    question = input("\nAsk a question (or 'quit'): ")
    if question.lower() == "quit":
        break
    result = qa.invoke({"query": question})
    print(f"\n{result['result']}")
```

---

## What This Doesn't Cover (Yet)

This is the happy path. Production RAG introduces a lot of complexity I want to address in separate posts:

- **Evaluation** — how do you know if your RAG is actually good? RAGAS, LlamaIndex eval frameworks
- **Chunking strategies** — semantic chunking, parent-child chunking, document hierarchy
- **Hybrid search** — combining dense and sparse retrieval
- **Reranking** — Cohere Rerank, cross-encoder models
- **Agentic retrieval** — query decomposition, iterative retrieval

The pipeline I've shown here is functional but naive. It works well enough to prototype on. The gap between this prototype and a production system is where most of the interesting engineering lives, and that's what I'll be exploring in upcoming posts.

---

## Prerequisites

If you want to run the code above:

```bash
pip install langchain langchain-openai langchain-chroma chromadb
export OPENAI_API_KEY="your-key-here"
```

Put some markdown or text files in a `./docs` directory and you're off.
