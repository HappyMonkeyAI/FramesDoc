---
type: procedural
tags: [patterns, lessons, agents-protocol, hackathon]
created: 2026-07-15
related: [../../AGENTS.md, ../../HERMES.md]
blast_radius: [workflow]
confidence: high
---

# Patterns And Lessons

## Success Patterns

- Keep the first demo loop narrow: one MP4 to one evidence-backed documentation page.
- Preserve intermediate artifacts so extraction, model selection, and document generation can be inspected independently.
- Treat timestamps, frames, and transcript spans as first-class data, not metadata to discard after summarization.
- Position the product as documentation generation from visual team knowledge, which is sharper than generic meeting summarization.

## Failure Lessons To Avoid

- Starting with Confluence synchronization before markdown or HTML output is convincing creates integration drag.
- Adding multi-video retrieval before one-video extraction works weakens the demo.
- Talking-head recordings with little screen content make the product look like ordinary meeting summarization.
- Copying generic bootstrap examples into project memory creates false history; only repository-grounded findings belong here.
