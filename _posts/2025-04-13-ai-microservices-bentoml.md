---
title: "Deploying AI Models as Microservices with BentoML"
categories:
    - Tech
tags:
    - ai
    - bentoml
    - mlops
    - kubernetes
    - python
    - learning
toc: true
---

The default path for deploying an ML model is: wrap it in FastAPI, write a Dockerfile, add a health endpoint, figure out batching, handle model loading at startup, and pray the memory estimates are right. I've done this several times and it's not terrible, but it's 80% boilerplate. BentoML is an attempt to make that boilerplate someone else's problem.

## What BentoML Provides Over Raw FastAPI

The honest answer is: a lot of conventions and some useful built-ins, plus a packaging format.

Specifically, BentoML gives you:
- **Adaptive batching** — it can collect requests arriving in a short window and batch them before inference, which matters a lot for GPU utilization
- **Runner abstraction** — model inference runs in a separate process from the serving logic, which unblocks the HTTP server during inference and lets you scale them independently
- **Bento packaging** — a self-contained artifact with model weights, dependencies, and service code that can be rebuilt anywhere
- **Built-in metrics** — Prometheus metrics on request count, latency, and batch sizes with zero extra code

If you're serving a stateless model and don't need batching, FastAPI might genuinely be simpler. BentoML earns its keep when batching and consistent packaging matter.

## Defining a Service

Here's a minimal BentoML service for a sentence embedding model:

```python
# service.py
import bentoml
import numpy as np
from sentence_transformers import SentenceTransformer

@bentoml.service(
    resources={"memory": "2Gi"},
    traffic={"timeout": 30},
)
class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    @bentoml.api(batchable=True, batch_dim=0, max_batch_size=64)
    def embed(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)
```

The `@bentoml.api(batchable=True)` decorator is the key line — it tells BentoML to collect incoming requests and batch them before calling `embed`. Under load, this turns 64 individual HTTP requests into one model call, which is a meaningful throughput gain on GPU.

## Running Locally

```bash
pip install bentoml sentence-transformers

# Run the service in development mode (auto-reloads on save)
bentoml serve service:EmbeddingService --reload
```

The service starts at `http://localhost:3000`. There's a built-in Swagger UI at `/docs` and a Prometheus metrics endpoint at `/metrics`. Both work without any extra code.

Test it:

```bash
curl -X POST http://localhost:3000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["hello world", "goodbye world"]}'
```

## Building a Bento and Kubernetes Deployment

Package the service into a Bento (a versioned, self-contained artifact):

```bash
bentoml build
# Outputs: EmbeddingService:a1b2c3d4e5f6
```

Build a Docker image from the Bento:

```bash
bentoml containerize EmbeddingService:a1b2c3d4e5f6
# Produces: embedding-service:a1b2c3d4e5f6
```

Deploy to Kubernetes with a standard Deployment — BentoML containers expose the same HTTP interface, so there's no special Kubernetes operator required:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: embedding-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: embedding-service
  template:
    spec:
      containers:
        - name: service
          image: embedding-service:a1b2c3d4e5f6
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "2Gi"
            limits:
              memory: "3Gi"
```

The Bento tag in the image name is useful for traceability — you know exactly what model version and code is running in any deployment.

## Honest Tradeoffs vs Rolling Your Own

**BentoML wins**: Adaptive batching without writing queue logic, consistent packaging across environments, built-in observability. If you're deploying multiple models across a team, the standardization pays off.

**Rolling your own wins**: Full control, no abstraction layer to debug when things go wrong, and simpler mental model for developers who don't know BentoML. A FastAPI service with `lifespan` for model loading and `asyncio` for batching is maybe 100 lines and zero framework magic.

My rule: if it's one model, one team, and batching isn't a bottleneck, FastAPI is fine. If you're managing a model catalog or need production-grade batching, BentoML's conventions are worth the learning curve.
