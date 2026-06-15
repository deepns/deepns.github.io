---
title: "OKF: Google's Markdown-Based Knowledge Format for AI Agents"
categories:
    - Tech
tags:
    - ai
    - llm
    - knowledge-management
    - agents
    - markdown
toc: true
header:
  teaser: /assets/images/teasers/nubelson-fernandes-CO6r5hbt1jg-unsplash.jpg
---

Two days ago, Google Cloud published a spec called the Open Knowledge Format (OKF). It's a v0.1 release — early, explicit about that — but the idea behind it is worth understanding now because it points at a real problem that anyone building with LLMs runs into eventually.

The problem: your AI agents don't have a good place to put what they learn.

RAG pipelines are good at retrieval. They're not good at accumulation. You ingest documents, chunk them, embed them, and query them — but the pipeline doesn't build on itself. Every new piece of knowledge has to be shoved into the same undifferentiated vector soup. There's no structure, no relationships, no concept of "this table depends on that metric." There's also no way for agents to write back what they've figured out.

OKF is Google's answer to the question: what if we treated organizational knowledge as a format rather than a platform?

---

## The Core Idea

OKF is simple to state: a **bundle** is a directory of Markdown files. Each file represents one concept — a database table, a business metric, an API endpoint, a runbook. Files link to each other using standard Markdown links. The whole thing ships as a folder, a tarball, or a git repository.

That's it. No proprietary database. No vendor SDK. No authentication layer between your agents and the knowledge.

The insight that makes this interesting is the separation between **producers** and **consumers**. Whatever writes OKF bundles — an LLM, a script, a human — doesn't need to know anything about whatever reads them. The format is the contract. A BigQuery enrichment agent can produce a bundle, and a completely unrelated AI assistant can consume it, without either side knowing about the other.

This is what Andrej Karpathy was gesturing at with his "LLM Wiki" idea: instead of repeatedly retrieving from raw documents, have agents incrementally build and maintain a structured wiki. Knowledge compiles once and stays current. OKF formalizes that pattern.

---

## File Format

A concept file looks like this:

```markdown
---
type: BigQuery Table
title: orders
description: Source of truth for all e-commerce transactions
resource: https://bigquery.googleapis.com/projects/myproject/datasets/ecommerce/tables/orders
tags: [ecommerce, transactions, revenue]
timestamp: 2026-06-12T00:00:00Z
---

## Schema

| Column      | Type      | Description                  |
|-------------|-----------|------------------------------|
| order_id    | INTEGER   | Primary key                  |
| customer_id | INTEGER   | FK → [customers](/tables/customers.md) |
| total_usd   | FLOAT     | Order total before tax       |
| created_at  | TIMESTAMP | UTC creation time            |

## Purpose

This table feeds the [Revenue metric](/metrics/revenue.md) and is the primary
source for the daily orders dashboard.

## Gotchas

`created_at` is stored in UTC but the reporting layer converts to PST.
Don't join against `sessions` on this column directly — use the
`event_date` partition key instead.
```

The only required frontmatter field is `type`. Everything else — `title`, `description`, `resource`, `tags`, `timestamp` — is optional. The Markdown body is completely free-form. You write what's useful.

Two filenames are reserved:

- `index.md` — a bundle overview / table of contents for progressive disclosure
- `log.md` — a chronological change history in ISO 8601 format

Everything else is up to you.

---

## Bundle Structure

A typical bundle for a data warehouse might look like:

```
knowledge/
├── index.md
├── log.md
├── tables/
│   ├── orders.md
│   ├── customers.md
│   └── sessions.md
├── metrics/
│   ├── revenue.md
│   ├── dau.md
│   └── conversion_rate.md
└── playbooks/
    ├── incident-response.md
    └── oncall-runbook.md
```

The cross-references between files (`/tables/customers.md`, `/metrics/revenue.md`) create a knowledge graph that both humans and agents can traverse. Navigate it in a text editor, in a git browser, or in one of the reference visualizers Google shipped alongside the spec.

What makes this git-native is that bundles are just directories. You get diffs, blame, branch-based experimentation, and PRs for free. An agent updates `metrics/revenue.md` and the change shows up in the PR review like any other file edit.

---

## Concept Types

OKF is deliberately unopinionated about what types are valid. The spec defines a few illustrative examples:

| Type | Example use |
|---|---|
| `BigQuery Table` | Data warehouse table documentation |
| `Metric` | Business metric with calculation and owners |
| `API Endpoint` | REST endpoint with method, path, auth |
| `Playbook` | Step-by-step operational runbook |
| `Policy` | Access control or data governance rules |
| `Laravel Model` | Application model with relationships |

You define your own taxonomy. A team building internal tooling might have `type: Slack Workflow` or `type: Terraform Module`. The spec doesn't care.

The `type` field is the only required field because it's the minimum needed for tooling to route and categorize concepts — without it, you have no way to tell a metric file from a runbook file programmatically.

---

## Reference Tools

Google shipped three tools alongside the v0.1 spec:

**BigQuery enrichment agent** — walks your dataset and auto-generates an OKF bundle from table and view definitions. You point it at a BigQuery project and it drafts concept docs for every table, pulling schema information, partition keys, and row counts into structured files.

**Static HTML visualizer** — renders a bundle as an interactive graph. Single self-contained HTML file, no backend required. You can ship the visualizer alongside a bundle in the same tarball and it works offline.

**Sample bundles** — reference implementations for GA4 e-commerce, Stack Overflow data, and Bitcoin transaction data. Useful for seeing what a well-structured bundle looks like before you build your own.

These are reference implementations, not the product. The point is to demonstrate that the format is useful without requiring anyone to adopt Google's specific toolchain.

---

## Use Cases

**Self-maintaining data dictionaries.** The current state of most data team documentation: stale Confluence pages that were last touched eighteen months ago. An enrichment agent that runs on a schedule, diffs the current schema against the OKF bundle, and opens a PR with updates is genuinely useful. The knowledge doesn't live in the agent's context — it lives in files that persist across runs.

**Runbooks that agents can read and write.** An on-call agent works through an incident response playbook, executes the steps, and appends a `## 2026-06-12` section to the playbook with what it did and what it found. The next time there's a similar incident, the playbook is richer. This is accumulation, not just retrieval.

**Portable client knowledge.** If you're a consultancy or a vendor, you can ship an OKF bundle alongside your automation that documents what the automation does, what data it touches, and how to debug it. The documentation travels with the code in the repo. When the engagement ends, the client has both.

**Compliance audit trails.** The optional `log.md` is ISO 8601 timestamped by convention. If you're writing entries into it as knowledge changes, you get an audit trail of what was known and when without any extra infrastructure. Whether that's sufficient for actual compliance requirements depends on your context, but it's a useful starting point.

**Agent context bootstrapping.** Instead of shoving your entire knowledge base into a system prompt, you give an agent a bundle path and it reads the specific files it needs. The `index.md` provides navigation. The agent traverses relationships to build up just the context it needs for the task at hand.

---

## How It Compares

It's worth being clear about what OKF is not, because there are a lot of overlapping things in this space.

**OKF vs. RAG.** RAG retrieves chunks from a document corpus. OKF stores structured, curated, linked knowledge. They're complementary — you might RAG over OKF bundles, but OKF bundles are also useful without any RAG in the pipeline. The difference is authorship: RAG sources are usually documents written for humans; OKF files are often written or maintained by agents specifically for agent consumption.

**OKF vs. MCP.** Model Context Protocol connects agents to tools and data sources at runtime. OKF is static knowledge at rest. An MCP server might expose an OKF bundle as a resource — that's a sensible combination — but they're solving different problems.

**OKF vs. llms.txt.** The [llms.txt proposal](https://llmstxt.org/) is a single file convention for mapping a website's structure. OKF is a multi-file format for representing an organization's internal knowledge graph. Different scale, different purpose.

**OKF vs. Notion/Confluence.** These tools have richer editors, mature ecosystems, and better accessibility for non-technical users. OKF's advantages are: no authentication needed for agents, git-native versioning, zero vendor lock-in, and a format that doesn't change on you. If your team already lives in Notion, OKF doesn't replace it — but you could export a Notion database as an OKF bundle and the agent-facing properties become much simpler.

**OKF vs. data catalogs.** Tools like Datahub or Alation are heavyweight: they require dedicated infrastructure, have their own data models, and are mostly read-only for agents. OKF is lightweight enough that a shell script can produce a valid bundle. Whether that simplicity is a feature or a limitation depends on your scale.

---

## What's Missing (So Far)

v0.1 means incomplete by design. A few things are notably absent:

**Access control.** A bundle is a directory. If an agent can read the directory, it can read everything. For sensitive knowledge (PII policies, security runbooks), you'd need to handle this at the filesystem or repository level, outside the spec.

**Conflict resolution.** If two agents write to the same file concurrently, you have a merge conflict like any other. The spec doesn't define a strategy for this. In practice, you'd probably handle it the same way you handle concurrent git edits — with locks, queuing, or PR-based workflows.

**Query semantics.** There's no defined way to query across a bundle beyond "read the files you need." For small bundles this is fine. For a bundle with thousands of concept files, you'd want some kind of index — either an LLM-navigable index.md hierarchy or a simple key-value lookup by type and name. The spec doesn't specify this.

**Validation beyond type.** The only required field is `type`. There's a validator for v0.1 compliance, but nothing prevents a concept file from having incorrect schema information or outdated descriptions. Data quality is still a human (or agent) responsibility.

---

## Why This Matters Now

The timing makes sense. The last year has produced solid tooling for agents that act (MCP, tool use, function calling) but relatively little for agents that know and remember. Context windows are larger but still finite. RAG is mature but doesn't accumulate. Fine-tuning is expensive and static.

A simple, portable, text-based format for persistent structured knowledge fills a gap that wasn't filled by any of the above. The fact that it's just Markdown in a folder means the barrier to adoption is nearly zero — if your agents can write files, they can write OKF.

Whether OKF specifically becomes a standard or whether it gets superseded by something better, the pattern it embodies — agents maintaining interlinked knowledge files — is going to be a fixture of how AI systems work. The question of where knowledge lives, who maintains it, and how it's structured is one of the genuinely interesting open problems in applied AI right now.

OKF is a reasonable opening move.
