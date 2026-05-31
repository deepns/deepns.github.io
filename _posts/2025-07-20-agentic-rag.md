---
title: "Agentic RAG: When Your Retrieval Pipeline Gets a Brain"
categories:
    - Tech
tags:
    - ai
    - rag
    - agents
    - python
    - learning
toc: true
---

Basic RAG is a pipeline: embed the query, retrieve top-k chunks, stuff them in a prompt, generate an answer. That works well for a surprisingly large range of questions. It stops working when the question is complex enough to require multiple retrieval steps — when the answer to "what changed in the authentication API between v2 and v3 and what should I update in my client code?" requires finding the v2 docs, finding the v3 docs, finding a migration guide, and then synthesizing across all three.

Vanilla RAG does one retrieval step and then answers. Agentic RAG adds a reasoning loop that decides whether it has enough information and, if not, keeps retrieving.

## The Limitations of Single-Shot Retrieval

A standard RAG pipeline assumes that one retrieval step is enough. This breaks down on:

- **Multi-hop questions**: Questions where answering requires chaining facts ("who founded the company that acquired X, and what other companies did they found?")
- **Comparative questions**: Questions requiring information from multiple, possibly non-adjacent documents
- **Ambiguous queries**: Where the initial retrieval returns the wrong type of content and the system needs to refine

The fundamental issue is that vanilla RAG is a open-loop system — it retrieves once and commits, with no mechanism to detect when the retrieved context doesn't actually answer the question.

## Query Decomposition

The first technique in agentic RAG is query decomposition: break a complex question into sub-questions that can each be answered with a single retrieval step.

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini")

def decompose_query(question: str) -> list[str]:
    prompt = f"""Break this question into 2-4 simpler sub-questions that can each be answered independently.
Return one sub-question per line, nothing else.

Question: {question}"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return [q.strip() for q in response.content.strip().split("\n") if q.strip()]

sub_questions = decompose_query(
    "What changed between GPT-4 and GPT-4o, and how does pricing compare?"
)
# ["What are the new capabilities in GPT-4o compared to GPT-4?",
#  "What is the pricing for GPT-4?",
#  "What is the pricing for GPT-4o?"]
```

Each sub-question runs through retrieval independently, and the answers are synthesized at the end.

## Retrieval as a Tool: The Tool-Use Pattern

In the tool-use pattern, the LLM decides when to call retrieval and with what query. The agent runs in a loop, calling tools until it decides it has enough information:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    question: str
    retrieved_docs: Annotated[list, operator.add]
    tool_calls: int
    final_answer: str

def should_retrieve_more(state: AgentState) -> str:
    """Ask the LLM if we have enough context."""
    if state["tool_calls"] >= 3:  # hard limit on retrieval loops
        return "generate"

    context = "\n\n".join(d["content"] for d in state["retrieved_docs"])
    prompt = f"""Do you have enough information to fully answer this question?
Question: {state['question']}
Current context: {context}
Reply YES or NO only."""
    response = llm.invoke([HumanMessage(content=prompt)])
    return "generate" if "YES" in response.content else "retrieve"

def retrieve(state: AgentState) -> dict:
    """Generate a refined query and retrieve."""
    context = "\n".join(d["content"] for d in state["retrieved_docs"][-2:])
    prompt = f"""Given the question and what you know so far, write a search query to find missing information.
Question: {state['question']}
Known so far: {context if context else 'Nothing yet.'}
Write only the search query, nothing else."""
    refined_query = llm.invoke([HumanMessage(content=prompt)]).content.strip()

    docs = retriever.invoke(refined_query)
    return {
        "retrieved_docs": [{"content": d.page_content, "query": refined_query} for d in docs],
        "tool_calls": state["tool_calls"] + 1
    }

def generate(state: AgentState) -> dict:
    context = "\n\n".join(d["content"] for d in state["retrieved_docs"])
    prompt = f"Answer this question using the context below.\n\nQuestion: {state['question']}\n\nContext:\n{context}"
    answer = llm.invoke([HumanMessage(content=prompt)]).content
    return {"final_answer": answer}

graph = StateGraph(AgentState)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.set_entry_point("retrieve")
graph.add_conditional_edges("retrieve", should_retrieve_more, {
    "retrieve": "retrieve",
    "generate": "generate",
})
graph.add_edge("generate", END)

app = graph.compile()
result = app.invoke({"question": "...", "retrieved_docs": [], "tool_calls": 0, "final_answer": ""})
```

The `tool_calls` counter is a safety valve. Without a hard limit, a poorly calibrated "enough information" check can run forever.

## When Agentic RAG Is Overkill

Agentic RAG adds latency and cost. A 3-loop agentic pipeline is 3-4x slower and more expensive than single-shot RAG. It's worth it when:

- Questions genuinely require multi-hop reasoning and users expect thorough answers
- Your document corpus is large and queries are diverse enough that one retrieval is rarely sufficient
- You have a latency budget (>5s) that accommodates multiple retrieval + LLM calls

It's overkill when:
- Most questions are self-contained and answerable from a single chunk
- You have latency requirements under 2-3 seconds
- Your users ask predictable, narrow questions (FAQ-style support)

The pragmatic path is to measure how often single-shot RAG returns incomplete answers and only add the agentic loop if that rate is high enough to justify the cost. Often, improving the retrieval quality (better chunking, hybrid search) fixes the problem without adding agent complexity.
