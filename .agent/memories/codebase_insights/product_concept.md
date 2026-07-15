---
type: semantic
tags: [product, mvp, video-documentation, hackathon]
created: 2026-07-15
related: [../../../20260715-planning.txt, ../../../README.md, ../../../CONTEXT.md]
blast_radius: [product-scope, docs, pipeline]
confidence: high
---

# Product Concept

Video Document Agent exists to recover important team knowledge trapped in meeting recordings, especially visual information that ordinary transcript summaries miss.

The highest-value use cases are:

- Terminal commands or configuration shown during a screen share
- Setup or deployment walkthroughs
- Product demos with specific UI states
- Incident-review steps and decisions
- “Wasn't that in a meeting?” lookup moments

The product should generate evidence-backed documentation, not just a prose summary. Every generated section should point back to timestamps, frames, and transcript spans where possible.
