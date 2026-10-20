---
title: "Applied AI"
permalink: /ai/
layout: archive
author_profile: true
---

Hands-on notes from building AI infrastructure: RAG pipelines, vector databases, taking LLM-backed services to production, and the formats and tooling that agents rely on. Each post is code-first and covers what worked and what didn't.

Read oldest to newest, the posts follow a progression: RAG fundamentals, then vector store tradeoffs, then a production Q&A service, then knowledge formats for agents.

{% for post in site.tags.ai %}
  {% include archive-single.html %}
{% endfor %}
