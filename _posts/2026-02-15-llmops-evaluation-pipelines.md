---
title: "LLMOps in Practice: Building Evaluation Pipelines That Catch Regressions"
categories:
    - Tech
tags:
    - ai
    - llmops
    - evaluation
    - python
    - learning
toc: true
---

When I changed a prompt last month — a small tweak, just tightening the instructions — a downstream behavior broke in a way I didn't notice for two days. No test caught it. No metric moved. The output looked fine until a user pointed out it was truncating a specific type of response. That's when I got serious about eval pipelines.

The problem with LLM evaluation is that it's genuinely hard. You can't write a unit test for "was this response helpful?" But you can build a pipeline that catches regressions reliably enough to gate deployments.

## Why Eval Is Hard for LLMs

With traditional software, correctness is binary. With LLMs, quality is a distribution. The same input produces slightly different outputs on each run. "Good" is contextual — a response that's perfect for a technical user might be confusing for a general audience.

There's also no universal ground truth. You can define expected outputs for specific test cases, but those quickly go stale as your application evolves. And LLM-as-judge (using an LLM to score another LLM's output) introduces model bias — GPT-4o tends to prefer GPT-4o-style responses.

Despite all this, a structured eval pipeline gives you something concrete: a comparison between today's behavior and yesterday's. That regression signal is valuable even when the absolute quality score is fuzzy.

## Pipeline Structure

The core eval loop is straightforward:

```
Golden dataset → Run prompts → Score outputs → Compare to baseline → Gate or alert
```

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class EvalCase:
    id: str
    prompt: str
    expected: str | None  # None for open-ended cases
    metadata: dict = None

@dataclass
class EvalResult:
    case_id: str
    output: str
    scores: dict[str, float]
    passed: bool

def run_eval_pipeline(
    cases: list[EvalCase],
    model_fn: Callable[[str], str],
    scorers: list[Callable],
    pass_threshold: float = 0.7,
) -> list[EvalResult]:
    results = []
    for case in cases:
        output = model_fn(case.prompt)
        scores = {}
        for scorer in scorers:
            score_name, score_value = scorer(case, output)
            scores[score_name] = score_value
        avg_score = sum(scores.values()) / len(scores)
        results.append(EvalResult(
            case_id=case.id,
            output=output,
            scores=scores,
            passed=avg_score >= pass_threshold,
        ))
    return results
```

## RAGAS for RAG Evaluation

For RAG-specific eval, RAGAS provides three metrics that are actually useful:

- **Faithfulness**: Does the answer contain only claims supported by the retrieved context? Catches hallucination.
- **Answer Relevance**: Does the answer address the question? Catches off-topic responses.
- **Context Recall**: Did retrieval surface the documents needed to answer correctly? Catches retrieval failures.

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from datasets import Dataset

def run_ragas_eval(qa_pairs: list[dict]) -> dict:
    """
    qa_pairs: list of {question, answer, contexts, ground_truth}
    """
    dataset = Dataset.from_list(qa_pairs)
    result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_recall],
    )
    return result.to_pandas().mean().to_dict()

# Example usage
pairs = [
    {
        "question": "What is the default timeout for the API?",
        "answer": "The default timeout is 30 seconds.",
        "contexts": ["API requests time out after 30 seconds by default. This can be configured."],
        "ground_truth": "30 seconds",
    }
]
scores = run_ragas_eval(pairs)
print(scores)  # {'faithfulness': 1.0, 'answer_relevancy': 0.92, 'context_recall': 1.0}
```

## A CI-Style Eval Script

The eval runner should compare against a stored baseline and fail the build if things regress:

```python
import json
from pathlib import Path

BASELINE_PATH = Path("eval/baseline_scores.json")
REGRESSION_THRESHOLD = 0.05  # 5% drop in any metric fails the build

def load_baseline() -> dict:
    if BASELINE_PATH.exists():
        return json.loads(BASELINE_PATH.read_text())
    return {}

def save_baseline(scores: dict):
    BASELINE_PATH.parent.mkdir(exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(scores, indent=2))

def check_regression(current: dict, baseline: dict) -> list[str]:
    failures = []
    for metric, score in current.items():
        if metric in baseline:
            drop = baseline[metric] - score
            if drop > REGRESSION_THRESHOLD:
                failures.append(
                    f"{metric}: {baseline[metric]:.3f} → {score:.3f} (dropped {drop:.3f})"
                )
    return failures

if __name__ == "__main__":
    current_scores = run_ragas_eval(load_golden_dataset())
    baseline = load_baseline()
    failures = check_regression(current_scores, baseline)

    if failures:
        print("EVAL REGRESSION DETECTED:")
        for f in failures:
            print(f"  - {f}")
        exit(1)
    else:
        print("Eval passed. Saving as new baseline.")
        save_baseline(current_scores)
        exit(0)
```

Run this in CI on every PR that changes a prompt or model configuration.

## The Meta-Problem: Eval Your Eval

Here's the uncomfortable part: your evaluation pipeline itself can be wrong. If your LLM judge has a bias, if your golden dataset has stale expected answers, if your faithfulness scorer has a blind spot for a particular response style — you're measuring the wrong thing and feeling good about it.

The partial fix is to review eval failures manually on a sample each week. When the eval flags a case as a failure that you'd consider a pass, that's signal that your scorer needs work. When it passes a case you'd call a failure, same thing.

Eval pipelines aren't a replacement for judgment. They're a way to scale your judgment and catch regressions before users do.
