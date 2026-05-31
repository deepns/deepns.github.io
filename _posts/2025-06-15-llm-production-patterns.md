---
title: "5 Production Patterns for LLM APIs That Don't Break Under Load"
categories:
    - Tech
tags:
    - ai
    - llmops
    - python
    - learning
toc: true
---

Running an LLM in a prototype is easy. Running one in production — where it has to handle real users, cost constraints, and provider outages — is a different problem. After shipping a few LLM-backed features to production, I've settled on five patterns that pay for their implementation complexity in reliability and maintainability.

## 1. Prompt Versioning with a Simple Registry

Prompts are code. Changing a prompt without tracking the change means you can't roll back when it starts producing bad outputs.

A simple registry doesn't need to be fancy — a dictionary with versioned prompt templates and a deployment pointer is enough:

```python
# prompts.py
from dataclasses import dataclass
from typing import Literal

@dataclass
class PromptVersion:
    version: str
    template: str
    model: str

PROMPT_REGISTRY: dict[str, list[PromptVersion]] = {
    "summarize": [
        PromptVersion(
            version="v1",
            template="Summarize the following text in 3 sentences:\n\n{text}",
            model="gpt-4o-mini",
        ),
        PromptVersion(
            version="v2",
            template="You are a concise summarizer. Summarize in 3 sentences, focusing on key facts:\n\n{text}",
            model="gpt-4o-mini",
        ),
    ]
}

# Points to active version; change this to roll back
ACTIVE_PROMPTS: dict[str, str] = {"summarize": "v2"}

def get_prompt(name: str) -> PromptVersion:
    active = ACTIVE_PROMPTS[name]
    return next(p for p in PROMPT_REGISTRY[name] if p.version == active)
```

Log the prompt version with every LLM call so you can correlate output quality with prompt changes in your analytics.

## 2. LLM Gateway Routing by Cost and Latency

Not every request needs GPT-4o. A gateway that routes based on task complexity saves significant cost:

```python
from enum import Enum

class TaskComplexity(Enum):
    SIMPLE = "simple"    # classification, extraction
    MEDIUM = "medium"    # summarization, Q&A
    COMPLEX = "complex"  # reasoning, synthesis

MODEL_ROUTING = {
    TaskComplexity.SIMPLE: "gpt-4o-mini",
    TaskComplexity.MEDIUM: "gpt-4o-mini",
    TaskComplexity.COMPLEX: "gpt-4o",
}

async def routed_completion(
    prompt: str,
    complexity: TaskComplexity,
    fallback: bool = True
) -> str:
    model = MODEL_ROUTING[complexity]
    try:
        return await call_llm(prompt, model=model)
    except RateLimitError:
        if fallback and model != "gpt-4o-mini":
            return await call_llm(prompt, model="gpt-4o-mini")
        raise
```

Track cost per task type in your metrics. You'll almost always find that 60-70% of calls can run on the cheaper model with acceptable quality.

## 3. Response Caching for Identical Prompts

LLM calls are expensive and slow. For inputs that repeat (FAQ-style questions, classification prompts with fixed templates, document summaries), caching the response is a legitimate optimization:

```python
import hashlib
import json
import redis

cache = redis.Redis(host="localhost", port=6379)
CACHE_TTL = 3600  # 1 hour

def cache_key(prompt: str, model: str) -> str:
    payload = json.dumps({"prompt": prompt, "model": model}, sort_keys=True)
    return f"llm:response:{hashlib.sha256(payload.encode()).hexdigest()}"

async def cached_completion(prompt: str, model: str) -> str:
    key = cache_key(prompt, model)
    cached = cache.get(key)
    if cached:
        return cached.decode()

    response = await call_llm(prompt, model=model)
    cache.setex(key, CACHE_TTL, response)
    return response
```

Add cache hit/miss metrics and review them. In one API I maintained, 40% of classification calls were cache hits after the first week of production traffic.

## 4. Circuit Breaker for LLM API Failures

LLM APIs fail — rate limits, timeouts, model degradations. Without a circuit breaker, a slow or failing LLM call blocks your request threads and cascades into full service failure:

```python
import time
from dataclasses import dataclass, field

@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    _failures: int = 0
    _last_failure_time: float = 0.0
    _open: bool = False

    def call(self, fn, *args, **kwargs):
        if self._open:
            if time.time() - self._last_failure_time > self.recovery_timeout:
                self._open = False  # half-open: try again
            else:
                raise Exception("Circuit open: LLM API unavailable")
        try:
            result = fn(*args, **kwargs)
            self._failures = 0
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure_time = time.time()
            if self._failures >= self.failure_threshold:
                self._open = True
            raise

llm_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30.0)

def resilient_completion(prompt: str) -> str:
    return llm_breaker.call(call_llm, prompt)
```

When the circuit is open, fail fast with a user-visible error rather than hanging. Users prefer a "service temporarily unavailable" message to a 30-second timeout.

## 5. Evaluation Gates Before Deploying Prompt Changes

Shipping a new prompt version without evaluation is like shipping code without tests. An evaluation gate runs the new prompt against a fixed benchmark set and blocks deployment if quality drops:

```python
EVAL_CASES = [
    {"input": "The quick brown fox...", "expected_contains": ["fox", "jumps"]},
    # 20-50 representative cases for your task
]

def evaluate_prompt(prompt_version: PromptVersion, threshold: float = 0.85) -> bool:
    passed = 0
    for case in EVAL_CASES:
        prompt = prompt_version.template.format(text=case["input"])
        response = call_llm_sync(prompt, model=prompt_version.model)
        if all(kw.lower() in response.lower() for kw in case["expected_contains"]):
            passed += 1
    score = passed / len(EVAL_CASES)
    print(f"Prompt {prompt_version.version} score: {score:.2%}")
    return score >= threshold

# In CI/CD:
new_version = get_prompt_candidate("summarize", "v3")
assert evaluate_prompt(new_version), "Prompt evaluation failed — block deployment"
```

This won't catch everything, but it catches regressions. Keep the eval set small enough to run in CI (under 2 minutes) and representative enough to matter. LLM-as-judge scoring (using another LLM to grade responses) works well for open-ended tasks where `expected_contains` is too brittle.
