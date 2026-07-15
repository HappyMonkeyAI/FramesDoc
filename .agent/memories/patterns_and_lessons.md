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
- Have the model select numbered evidence, then reattach provenance locally.
- Keep a deterministic mode that exercises real media processing while clearly labelling synthetic analysis.
- Use transcript cues to preserve documentation-worthy frames even when visual novelty is low.
- Hash sidecar inputs into job identity so alternate transcripts cannot collide.
- Store human review as a separate artifact; keep visual evidence coordinates immutable and audit transcript-span corrections.
- Use timestamped sidecars to validate most of the product without coupling development to API credentials.
- Keep OCR observations separate from model-visible text and compare them explicitly instead of overwriting either source.
- Evaluate recall, redundancy, grounding, and OCR agreement separately; a single aggregate score hides actionable failures.

## Failure Lessons To Avoid

- Starting with Confluence synchronization before markdown or HTML output is convincing creates integration drag.
- Adding multi-video retrieval before one-video extraction works weakens the demo.
- Talking-head recordings with little screen content make the product look like ordinary meeting summarization.
- Copying generic bootstrap examples into project memory creates false history; only repository-grounded findings belong here.
- Scene-change detection alone misses small but important terminal and UI changes.
- A broad transcript window is useful model context but too imprecise as the persisted citation span; attach the closest source segment instead.
- Streamlit review state must outlive widget-triggered reruns; retain the manifest in session state and persist reviewed exports to disk.
- Low perceptual novelty can be an intentional transcript-cued frame, so report visual redundancy as a diagnostic rather than an automatic rejection rule.
