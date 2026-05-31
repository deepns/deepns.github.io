---
title: "Llama 4 vs API: When It Actually Makes Sense to Self-Host"
categories:
    - Tech
tags:
    - ai
    - llm
    - self-hosting
    - learning
toc: true
---

I've been going back and forth on this for months. Every time I spin up an Ollama instance and run a few queries, I think "why am I paying for the API?" And then I hit some edge case or need a capability jump and I'm back to Claude or GPT-4o. Here's the framework I've landed on after actually running both in production contexts.

## The Real Cost Math

The naive comparison is tokens-per-dollar, and on that metric, self-hosting wins at scale — but it ignores the full cost picture.

For a typical developer setup, you need at minimum an NVIDIA RTX 4090 (24GB VRAM) to run Llama 4 Scout at full precision. That's ~$2,000 hardware cost. At $0.30/1M output tokens (rough API pricing), you'd need to generate ~6.7 billion tokens to break even on hardware alone — before accounting for power (~$50/month), your time, and opportunity cost.

The math flips if you're running high volume. A team processing 50M tokens/day is spending ~$15,000/month on API calls. A single A100 server can handle that workload for ~$3,000/month fully loaded.

## Hardware Reality for Llama 4

Llama 4 Scout (17B active params, MoE) is actually friendlier than it looks:

```bash
# Pull and run Llama 4 Scout with Ollama
ollama pull llama4:scout

# Check what's actually loaded into VRAM
ollama ps

# Run with llama.cpp at 4-bit quantization
./llama-cli \
  -m llama-4-scout-Q4_K_M.gguf \
  -n 512 \
  --ctx-size 8192 \
  --n-gpu-layers 35 \
  -p "Explain token embeddings in one paragraph"
```

With Q4_K_M quantization, Scout fits comfortably in 16GB VRAM. Quality degradation vs full precision is noticeable but acceptable for most tasks — summarization and classification hold up better than complex reasoning.

Llama 4 Maverick (128B active) is a different story. You're looking at multi-GPU setups or CPU offloading, which tanks throughput to the point where API latency is competitive again.

## When Self-Hosting Actually Wins

**Data privacy is non-negotiable.** Healthcare, legal, finance — if your data can't leave your network, you don't have a choice. Llama 4 running on-prem is the answer. API providers' DPA agreements often have carve-outs that don't satisfy real compliance requirements.

**High-volume, repetitive tasks.** Batch jobs — document classification, structured extraction, embedding generation — are perfect for self-hosted. No rate limits, no per-token billing anxiety.

**Latency SLAs under 100ms.** API round trips have a floor around 200-400ms from cold token to first response. A local model with enough VRAM can hit 50ms time-to-first-token for short prompts.

**Fine-tuned models.** If you've invested in fine-tuning on domain data, you own that model. Running it yourself makes sense — you've already sunk the training cost.

## When APIs Still Win

Cold start problems are real. A self-hosted setup that sits idle 90% of the day is wasteful. APIs scale to zero effortlessly.

The ops burden is underrated. Model updates, GPU driver compatibility, inference server versioning (vLLM, llama.cpp, Ollama all move fast) — someone has to own this. For a solo developer or small team, that overhead is brutal.

Frontier capability gaps close slowly. Llama 4 Maverick is genuinely competitive with GPT-4o on many tasks, but there are still edge cases — complex multi-step reasoning, tool use reliability — where the hosted frontier models have an edge.

## A Simple Benchmark Framework

Before committing, I test three things on my actual workload:

```python
import time, statistics

def benchmark_endpoint(fn, prompts, runs=3):
    latencies, tokens = [], []
    for prompt in prompts:
        for _ in range(runs):
            start = time.perf_counter()
            result = fn(prompt)
            latencies.append(time.perf_counter() - start)
            tokens.append(result.get("usage", {}).get("total_tokens", 0))
    return {
        "p50_latency": statistics.median(latencies),
        "p95_latency": statistics.quantiles(latencies, n=20)[18],
        "avg_tokens": statistics.mean(tokens),
    }
```

Run this against both endpoints with representative prompts, then multiply the API version's token count by your per-token cost.

## What I'd Actually Choose

For a new project today: start with the API, gate your spend with a token budget, and revisit when your monthly bill hits $500. At that point, the self-hosting conversation becomes worth the ops investment. If your data is sensitive from day one, go self-hosted immediately — Ollama makes the setup genuinely painless now.
