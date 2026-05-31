---
title: "From Chains to Graphs: Moving Agent Workflows to LangGraph"
categories:
    - Tech
tags:
    - ai
    - langchain
    - langgraph
    - agents
    - python
    - learning
toc: true
---

Sequential chains are a natural starting point for LLM-powered workflows. You have a prompt, you call an LLM, you parse the output, you pass it along. That works until it doesn't — and the moment it stops working is usually when you need branching, retries, or any loop that isn't "do this once, in order."

I hit this wall building a research agent that needed to search, evaluate whether it had enough information, and search again if not. Sequential chains can't express "go back to step 2 if the answer is incomplete." LangGraph can.

## The Problem with Sequential Chains

LangChain's `LCEL` (LangChain Expression Language) chains are composable and readable for linear workflows:

```python
chain = prompt | llm | output_parser
result = chain.invoke({"question": "..."})
```

This is great. But real agent workflows have control flow:
- If the LLM says it needs more information, retrieve again
- If a tool call fails, retry with a modified input
- If confidence is low, route to a different tool

Expressing these with chains means bolting on Python control flow outside the chain, which quickly turns into a mess of `if/else` wrappers that aren't observable, restartable, or easy to test.

## The LangGraph Model: State, Nodes, Edges

LangGraph models a workflow as a directed graph where:

- **State**: A typed dict that flows through the graph and accumulates results
- **Nodes**: Functions that take state, do work, and return state updates
- **Edges**: Connections between nodes, which can be conditional

The state is the key insight. Every node receives the full current state and returns only what it wants to update. This makes nodes easy to test in isolation and makes the accumulated context visible at any point in execution.

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

class AgentState(TypedDict):
    question: str
    documents: Annotated[list, operator.add]  # accumulates across nodes
    answer: str
    needs_more_info: bool
```

## A Working Agent Graph Example

Here's a simple research agent that retrieves documents, decides if it has enough context, and loops back to retrieve more if needed:

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini")

def retrieve(state: AgentState) -> dict:
    """Retrieve documents for the current question."""
    # Your retriever here
    docs = retriever.invoke(state["question"])
    return {"documents": docs}

def evaluate(state: AgentState) -> dict:
    """Decide if we have enough context to answer."""
    context = "\n".join(d.page_content for d in state["documents"])
    prompt = f"""Given these documents, can you answer '{state["question"]}'?
    Documents: {context}
    Reply with YES or NO only."""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"needs_more_info": response.content.strip() == "NO"}

def generate_answer(state: AgentState) -> dict:
    """Generate a final answer from accumulated documents."""
    context = "\n".join(d.page_content for d in state["documents"])
    prompt = f"Answer this question using the context:\nQ: {state['question']}\nContext: {context}"
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"answer": response.content}

def should_continue(state: AgentState) -> str:
    """Conditional edge: loop back or proceed to answer."""
    if state["needs_more_info"] and len(state["documents"]) < 10:
        return "retrieve"
    return "generate"

# Build the graph
graph = StateGraph(AgentState)
graph.add_node("retrieve", retrieve)
graph.add_node("evaluate", evaluate)
graph.add_node("generate", generate_answer)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "evaluate")
graph.add_conditional_edges("evaluate", should_continue, {
    "retrieve": "retrieve",
    "generate": "generate",
})
graph.add_edge("generate", END)

app = graph.compile()
result = app.invoke({"question": "What are the main causes of inflation?", "documents": []})
print(result["answer"])
```

The `add_conditional_edges` call is where the control flow lives. The function `should_continue` returns a string key, which LangGraph maps to the next node. This is the thing chains can't express cleanly.

## Honest Caveats About LangGraph

LangGraph is genuinely more powerful than chains for complex agents, but the learning curve is real.

**The graph mental model takes time.** If you're used to thinking in functions and returns, the "state flows through nodes" model requires a shift. The first few graphs you write will feel awkward.

**Debugging is harder than it looks.** LangGraph has streaming and checkpointing built in, which helps, but understanding why a conditional edge routed the wrong way still requires careful logging.

**It's not always worth it.** If your workflow is truly linear — input, retrieve, generate, output — use a chain. LangGraph shines when you have loops, branching, or parallel branches. Don't introduce graph complexity for a workflow that's actually a pipeline.

The payoff, when you do need it, is a workflow that's explicit about its control flow, restartable from any checkpoint, and much easier to reason about than nested Python conditionals wrapped around chains.
