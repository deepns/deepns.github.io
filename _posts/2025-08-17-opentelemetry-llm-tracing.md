---
title: "Tracing AI Pipelines with OpenTelemetry"
categories:
    - Tech
tags:
    - ai
    - observability
    - opentelemetry
    - python
    - learning
toc: true
---

LLM observability is not the same as regular API observability, and the difference matters in production. A typical REST endpoint has latency you can measure in milliseconds and errors you can count. An LLM pipeline has latency measured in seconds, responses that can be subtly wrong without raising an exception, token costs that accumulate silently, and prompt versions that change the behavior of the same endpoint. Standard APM tools handle the first two. They're mostly blind to the rest.

OpenTelemetry gives you a foundation for building useful observability for LLM services, even if you have to instrument the interesting parts manually.

## Why LLM Observability Is Different

A few things that make LLM pipelines harder to observe:

- **Latency is high and variable** — a single LLM call can be 500ms to 30s depending on output length, load, and model. Average latency is nearly meaningless; you need p95 and p99, and you need to know which model and prompt version produced them.
- **Errors are often semantic, not exceptions** — a hallucinated answer doesn't throw a `500`. You need to track outputs, not just exceptions.
- **Token costs are invisible without instrumentation** — you won't know which prompts are expensive until you're looking at an API bill.
- **Prompt version matters** — the same endpoint behaves differently after a prompt change. You need to correlate traces with prompt versions.

Span attributes are the right tool for all of this: capture model name, prompt version, input token count, output token count, and (optionally) the prompt and response as span attributes.

## Setting Up OTEL SDK with FastAPI

Install the dependencies:

```bash
pip install opentelemetry-sdk opentelemetry-instrumentation-fastapi \
    opentelemetry-exporter-otlp-proto-grpc openai
```

Configure the tracer and instrument FastAPI:

```python
# tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing(app, service_name: str = "llm-service"):
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    return trace.get_tracer(service_name)
```

```python
# main.py
from fastapi import FastAPI
from tracing import setup_tracing

app = FastAPI()
tracer = setup_tracing(app)
```

## Instrumenting LLM Calls with Custom Spans

The automatic FastAPI instrumentation captures HTTP-level spans. You need manual spans for the LLM calls themselves, with token counts and model names as attributes:

```python
from opentelemetry import trace
from openai import AsyncOpenAI

client = AsyncOpenAI()
tracer = trace.get_tracer("llm-service")

async def traced_completion(
    prompt: str,
    model: str = "gpt-4o-mini",
    prompt_version: str = "v1"
) -> str:
    with tracer.start_as_current_span("llm.completion") as span:
        span.set_attribute("llm.model", model)
        span.set_attribute("llm.prompt_version", prompt_version)
        span.set_attribute("llm.prompt_length", len(prompt))

        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        usage = response.usage
        span.set_attribute("llm.input_tokens", usage.prompt_tokens)
        span.set_attribute("llm.output_tokens", usage.completion_tokens)
        span.set_attribute("llm.total_tokens", usage.total_tokens)
        # Optionally capture prompt and response (watch out for PII)
        # span.set_attribute("llm.prompt", prompt[:500])
        # span.set_attribute("llm.response", response.choices[0].message.content[:500])

        return response.choices[0].message.content
```

These span attributes are what make the traces useful — filtering by `llm.prompt_version` in Jaeger lets you compare latency and token usage before and after a prompt change.

## Running Jaeger Locally with Docker

```bash
docker run -d \
  --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest
```

Open `http://localhost:16686` for the Jaeger UI. Traces from your FastAPI service appear under the service name you set in the tracer. You can filter by span attributes — useful for finding all traces where `llm.total_tokens > 2000` or where `llm.prompt_version = "v1"`.

## Full Trace for a RAG Request

For a RAG pipeline, create parent and child spans to show the full request breakdown:

```python
@app.post("/query")
async def query(request: QueryRequest):
    with tracer.start_as_current_span("rag.pipeline") as parent_span:
        parent_span.set_attribute("query.text", request.question[:200])

        with tracer.start_as_current_span("rag.retrieval"):
            docs = await retrieve_documents(request.question)
            trace.get_current_span().set_attribute("retrieval.doc_count", len(docs))

        context = "\n".join(d.content for d in docs)
        prompt = build_prompt(request.question, context)

        answer = await traced_completion(prompt, prompt_version="v2")
        return {"answer": answer}
```

This gives you a trace with three spans: the outer `rag.pipeline`, a `rag.retrieval` child, and a `llm.completion` child — with latency breakdown between retrieval and generation visible in the Jaeger waterfall view.

## OpenLLMetry as a Higher-Level Alternative

If you want semantic LLM tracing without writing spans manually, Traceloop's **OpenLLMetry** library auto-instruments OpenAI, Anthropic, and other providers:

```bash
pip install traceloop-sdk
```

```python
from traceloop.sdk import Traceloop

Traceloop.init(app_name="llm-service", api_key="...", disable_batch=True)
# OpenAI calls are now traced automatically with token counts and model names
```

OpenLLMetry is a faster start but less flexible — you can't add custom attributes as easily, and you're dependent on their instrumentation keeping up with provider API changes. For a prototype or small service, it's a good shortcut. For a production system where you need full control over what's captured, manual OTEL spans are worth the extra code.
