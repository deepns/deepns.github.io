---
title: "Building an LLM Gateway: Rate Limiting, Routing, and Cost Control"
categories:
    - Tech
tags:
    - ai
    - llmops
    - python
    - architecture
    - learning
toc: true
---

If you're running LLMs in production with more than one application or team, you'll eventually want a layer between your apps and the provider APIs. I kept running into the same problems — scattered API keys, no visibility into which service was burning budget, no way to enforce rate limits per team. A lightweight gateway solves all of these without adding much operational complexity.

## Why a Gateway at All

The problems it addresses are pretty concrete:

- **Centralized auth**: One API key per provider, managed in one place. Rotate it once, everywhere updates.
- **Cost visibility**: Which application spent what this week? Without a proxy, you're guessing from provider dashboards.
- **Rate limiting**: Prevent one runaway job from exhausting your quota.
- **Model routing**: Automatically use a cheap model for simple queries, expensive model for complex ones.
- **Fallback handling**: If OpenAI returns a 429, retry with Anthropic automatically.

## Core Design: FastAPI Proxy

The basic structure is a FastAPI app that accepts requests in OpenAI's API format, applies gateway logic, then forwards to the appropriate backend:

```python
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()

BACKENDS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "local": "http://localhost:11434/v1",  # Ollama
}

@app.post("/v1/chat/completions")
async def proxy_chat(request: Request):
    body = await request.json()
    
    model = body.get("model", "gpt-4o-mini")
    backend_url, headers, body = await route_request(model, body, request.headers)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{backend_url}/chat/completions",
            json=body,
            headers=headers,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
```

## Token Bucket Rate Limiting

A token bucket per API key (or per team identifier in your auth header) prevents abuse without being overly rigid:

```python
import time
from collections import defaultdict
from dataclasses import dataclass, field

@dataclass
class TokenBucket:
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self):
        self.tokens = float(self.capacity)
        self.last_refill = time.monotonic()

    def consume(self, amount: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False

buckets: dict[str, TokenBucket] = defaultdict(
    lambda: TokenBucket(capacity=100, refill_rate=10.0)  # 10 req/s, burst 100
)

def check_rate_limit(client_id: str, cost: int = 1) -> bool:
    return buckets[client_id].consume(cost)
```

## Routing Logic

The router maps incoming model aliases to actual backend models. A simple complexity classifier drives cost-based routing:

```python
COMPLEXITY_INDICATORS = [
    "analyze", "compare", "explain in detail", "write a", "implement",
    "debug", "review", "summarize the following", "translate"
]

def classify_complexity(prompt: str) -> str:
    prompt_lower = prompt.lower()
    # Simple heuristic: long prompts or complex keywords → heavy model
    if len(prompt) > 500 or any(k in prompt_lower for k in COMPLEXITY_INDICATORS):
        return "heavy"
    return "light"

ROUTING_TABLE = {
    "light": {"model": "gpt-4o-mini", "backend": "openai"},
    "heavy": {"model": "gpt-4o",      "backend": "openai"},
    "private": {"model": "llama4:scout", "backend": "local"},
}

async def route_request(model: str, body: dict, headers) -> tuple:
    client_id = headers.get("x-client-id", "default")

    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    if model == "auto":
        user_message = next(
            (m["content"] for m in body.get("messages", []) if m["role"] == "user"), ""
        )
        complexity = classify_complexity(user_message)
        route = ROUTING_TABLE[complexity]
    else:
        route = {"model": model, "backend": "openai"}

    body["model"] = route["model"]
    backend_url = BACKENDS[route["backend"]]
    auth_headers = {"Authorization": f"Bearer {get_api_key(route['backend'])}"}
    return backend_url, auth_headers, body
```

## Cost Tracking with Redis

Track spend per client in Redis with daily key rollover:

```python
import redis
from datetime import date

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Pricing per 1M tokens (input/output)
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o":      {"input": 2.50, "output": 10.00},
}

def record_usage(client_id: str, model: str, usage: dict):
    pricing = PRICING.get(model, {"input": 0, "output": 0})
    cost = (
        usage.get("prompt_tokens", 0) / 1_000_000 * pricing["input"]
        + usage.get("completion_tokens", 0) / 1_000_000 * pricing["output"]
    )
    key = f"cost:{client_id}:{date.today().isoformat()}"
    r.incrbyfloat(key, cost)
    r.expire(key, 86400 * 30)  # 30 day retention
```

## Docker Compose Setup

```yaml
services:
  gateway:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

Applications point to `http://gateway:8000/v1` instead of the provider directly. The gateway is stateless (Redis holds state), so you can run multiple instances behind a load balancer without coordination issues.

The whole thing is maybe 300 lines of Python. I was surprised how much you get for that investment.
