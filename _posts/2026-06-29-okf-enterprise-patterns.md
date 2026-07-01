---
title: "OKF in the Enterprise: Five Patterns Worth Watching"
categories:
    - Tech
tags:
    - ai
    - llm
    - knowledge-management
    - agents
    - data-engineering
    - enterprise
toc: true
header:
  teaser: /assets/images/teasers/mario-verduzco-network-sphere-unsplash.jpg
---

*This is part two of a series on Google's Open Knowledge Format. [Part one](/tech/google-open-knowledge-format/) covered what OKF is and the design philosophy behind it. This post looks at where it lands in enterprise settings.*

OKF is seventeen days old as of this writing. There are no production case studies yet. What exists is a working reference implementation, a fast-growing community tool ecosystem, and a set of patterns that practitioners are actively discussing and prototyping. What follows is a survey of those patterns — what's concrete, what's credible, and what's still early.

---

## Pattern 1: The Self-Maintaining Data Dictionary

This is the most concrete enterprise application of OKF, and the one Google shipped working tooling for at launch.

The pain it targets is familiar to anyone who has worked on a data team: documentation is perpetually stale. Table definitions drift from their documented descriptions. Columns get added without corresponding updates to the data dictionary. Confluence pages about `orders` last touched eighteen months ago get cited in Slack as though they're authoritative. The problem isn't that teams don't value documentation — it's that there's no forcing function that keeps it current.

The OKF approach: a BigQuery enrichment agent walks your dataset and auto-generates one OKF file per table and view, pulling schema definitions, partition keys, and row counts into structured Markdown files. A second LLM pass enriches those files with inferred descriptions, documented join paths, and caught gotchas. The agent runs on a schedule, diffs the current schema against the existing bundle, and opens a PR when anything has changed.

The structural advantage over a traditional data catalog is that the bundle lives in the same git repository as the dbt models or SQL definitions. A schema change and its corresponding documentation update travel together in the same PR. Reviewers see both in one diff. If a column is removed and the downstream metric file still references it, the discrepancy is visible at review time rather than discovered six months later when an analyst files a ticket.

Google's BigQuery enrichment agent is a reference implementation, not a production product — but it's runnable, and data teams are the exact profile most likely to adopt something like this: git-native, already writing YAML, already managing schema-as-code.

---

## Pattern 2: Runbooks That Accumulate

The second pattern is one that's discussed consistently across multiple sources but doesn't have a public production example yet. That said, the architecture is sound and connects directly to existing agent infrastructure.

The idea: an on-call agent reads `index.md`, follows cross-links through an incident response playbook, executes the documented steps, and appends a dated section to the runbook with what it did and what it found. The next time a similar alert fires, the runbook is richer than it was before — not because a human updated it, but because the previous agent run left structured notes.

This is the write-back pattern: agents that don't just retrieve knowledge but contribute to it. OKF's Markdown-and-git structure makes this straightforward. The agent writes a file, commits it, opens a PR. The change is reviewable, reversible, and auditable. It doesn't require a proprietary database or vendor-specific tool — just file writes.

PagerDuty's SRE Agent, launched in October 2025, already implements a version of this pattern — learning from incidents to generate smarter playbooks. OKF provides a vendor-neutral storage format for that kind of accumulated knowledge. A runbook bundle that an on-call agent has been maintaining for six months is more useful than one written once and left alone, and it's portable across whatever tooling the team is using.

The gap that makes this a design pattern rather than a deployed practice: concurrent writes. If two on-call agents respond to two simultaneous incidents and both try to update the same runbook file, you get a git merge conflict. The spec doesn't define a resolution strategy. In practice, teams reaching for this pattern would need to decide between lock-based approaches, PR-based queuing, or file-per-incident structures that aggregate separately.

---

## Pattern 3: Data Sovereignty and Local-First Agent Stacks

This is the least obvious enterprise use case and one of the more interesting ones.

For organizations in European regulated industries — financial services, healthcare, public sector — there's a meaningful constraint on what knowledge can flow through external cloud services. Internal database schemas, metric definitions, and data governance policies may be sensitive enough that sending them to a US-hosted enrichment endpoint for processing isn't permissible, or requires legal review that adds friction.

OKF's design is local-first by nature. A bundle is a directory. The knowledge lives in files. An enrichment agent that runs inside the organization's own infrastructure, reads local schemas, writes to a local bundle, and never sends that data to an external API is architecturally straightforward. There's no authentication surface between the agent and the knowledge store, because the knowledge store is a folder.

This framing — OKF as an enabler for agent stacks that keep sensitive knowledge within organizational boundaries — is explicitly being explored by European AI consultancies building for regulated clients. It's not a feature Google emphasized in the spec announcement, but it's a natural consequence of the format's design choices. The same property that makes OKF appealing for simplicity (no database, no vendor SDK) makes it viable in contexts where data residency is a hard constraint.

---

## Pattern 4: Knowledge Composability in Data Mesh Architectures

Organizations that have adopted data mesh principles — where domain teams own their data products rather than a central platform team — run into a documentation coordination problem. Each domain team has their own tables, metrics, and pipelines. Discovery across domains typically requires either a central catalog (which reintroduces centralization) or bespoke tooling per domain.

OKF fits into this structure without requiring either. Each domain team maintains their own bundle — one directory in the repo, covering their tables and metrics. A central discovery agent can traverse multiple bundles by reading each domain's `index.md` and following links. The bundles are independent and can evolve at different rates without coordination overhead.

The complementarity with dbt is worth noting. The dbt semantic layer handles transformation logic and metric computation — what the numbers mean and how they're calculated. OKF handles the broader context layer: why a table exists, who owns it, what gotchas a consumer should know, what upstream systems it depends on. They address different questions and don't overlap significantly in practice.

This is a design pattern with no reference implementation yet — just architectural reasoning and community discussion. Whether it scales to large data mesh deployments (dozens of domain teams, hundreds of bundles) depends on index.md hierarchy strategies that the spec doesn't currently prescribe.

---

## Pattern 5: Knowledge as a Deliverable

When a consulting engagement ends or a vendor relationship changes, operational knowledge tends to get left behind — either trapped in the vendor's SaaS platform or distributed across email threads and slide decks. The receiving organization starts from scratch.

A few AI consultancies have started positioning OKF bundles as part of their engagement deliverable. The automation they build for a client ships with an OKF bundle that documents what it does, what data it reads and writes, how to debug it, and what decisions were made during implementation. The bundle lives in the client's repository. When the engagement ends, the client's agents and engineers can query it directly — no login to a third-party tool, no dependency on the consultant's infrastructure.

This reframes knowledge transfer from a one-time handoff document (typically a PDF that goes stale immediately) to a maintained artifact that future agents can consume. The value proposition is similar to the data dictionary case: knowledge in a format that agents can traverse is more useful than knowledge in a format that only humans read.

There are no public case studies for this pattern. It's being discussed as a differentiation strategy in the AI consulting space, but it's early enough that it's more positioning than practice.

---

## What's Still Missing

None of these patterns are complete solutions, and it's worth being direct about the gaps that enterprise adopters will encounter.

**Access control is entirely external to the spec.** A bundle is a directory. If an agent or user can read the directory, they can read everything in it. For sensitive knowledge (security runbooks, PII policies, internal pricing), fine-grained access control has to be handled at the filesystem or repository level — outside OKF. In most enterprise environments, this means the team will need a separate strategy for what lives in the bundle and what doesn't.

**No query semantics for large bundles.** For a bundle with dozens of concept files, "read the files you need" works. For a bundle with thousands, it doesn't. The spec doesn't define how to query across a bundle by type, tag, or relationship. The community is experimenting with LLM-navigable `index.md` hierarchies and external key-value indexes, but nothing is standardized. Teams building at scale will need to decide on their own index strategy.

**Validation is opt-in.** The only required frontmatter field is `type`. A concept file with an outdated schema, broken cross-links, or an incorrect metric formula is still valid OKF. The spec includes a v0.1 validator for basic compliance, but content quality is the responsibility of whoever maintains the bundle — human, agent, or both.

**Non-technical contributor workflow.** For organizations where the most relevant knowledge lives with business analysts, compliance officers, or domain experts who aren't comfortable with git, OKF's "it's just a folder" model creates a participation barrier. There's no Notion-style editor, no web-based contribution UI, nothing between the knowledge holder and the Markdown file. This is a real friction point for knowledge that isn't already owned by technical teams.

---

## Where the Ecosystem Is Heading

The tooling ecosystem around OKF moved quickly after the v0.1 announcement. A zero-dependency Rust implementation, a Claude Code native plugin (`okf-skills`), an MCP server implementation in the `kcmd` CLI, a community-built linter, and Kiso — a full OKF publishing engine — all appeared within the first two weeks. The Hugo CMS project has an open integration request.

The more significant signal is at the platform level. Google is rebranding Dataplex as Knowledge Catalog — described as an "always-on context engine" for AI agents — with OKF as its export format. Collibra, Datahub, and Unity Catalog are named in the official OKF README as future bundle producers. The spec governance sits under the W3C Holon Community Group rather than Google, which matters for enterprise procurement teams who want assurance the format won't be unilaterally changed.

These are forward-looking signals, not shipped integrations. But they indicate the intended path from reference implementation to enterprise infrastructure.

---

The five patterns above sit at different maturity levels. The data dictionary case has a working implementation today. The runbook accumulation pattern has solid architectural grounding but no public production examples. The sovereignty, data mesh, and consultant handoff patterns are earlier still — plausible and being actively discussed, but without case studies to validate assumptions. The gap between "architecturally sound" and "deployed in production" is where most of the interesting work will happen over the next year.

*Next in this series: the write-back pattern — what it means for agents to accumulate knowledge rather than just retrieve it, and what that changes about how AI systems are designed.*
