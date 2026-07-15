---
type: procedural
tags: [agents-protocol, video-document-agent, hackathon]
created: 2026-07-15
related: [README.md, CONTEXT.md, HERMES.md]
blast_radius: [docs, memory, workflow]
confidence: high
---

# AGENTS.md: Video Document Agent

You are an autonomous developer agent working on Video Document Agent, an OpenAI Build Week / Devpost project that turns team meeting recordings into timestamped internal documentation.

## Prime Directive

Minimize friction, maximize momentum, and keep the project demoable. Favor a narrow, working video-to-documentation loop over broad platform features.

## Grounding Routine

At the start of each session, read:

1. `README.md`
2. `CONTEXT.md`
3. `HERMES.md`
4. Relevant `.agent/memories/**` files
5. The current task or planning note

## Product Focus

The MVP is not generic meeting summarization. It generates documentation from visual and spoken team knowledge, including:

- Terminal commands shown during meetings
- Product or system walkthrough steps
- Setup instructions and warnings
- Decisions with supporting transcript context
- Screenshots and timestamps that link back to the source video

## Technical Standards

- Keep the first workflow local and inspectable: uploaded MP4, extracted keyframes, transcript chunks, OCR/vision annotations, and generated markdown or HTML.
- Preserve source evidence for every generated documentation section: timestamp, frame image, transcript span, and model label or rationale where available.
- Prefer simple file-based artifacts until the core loop is proven.
- Treat Confluence publishing and multi-video retrieval as post-MVP integrations unless the demo requires them.
- Keep OpenAI model usage central and explicit in code paths and documentation.
- Do not claim a feature, model, or integration works until it has been verified.

## Long-Term Memory

Persistent memory lives in `.agent/memories/`:

- `codebase_insights/` for product/module facts and hidden knowledge
- `architectural_decisions/` for decisions, context, and tradeoffs
- `history/` for dated session outcomes
- `patterns_and_lessons.md` for reusable workflows and failure lessons

Use frontmatter fields `type`, `tags`, `created`, `related`, `blast_radius`, and `confidence`. Do not invent history; ground entries in files, commits, user notes, or verified external references.

## Workflow

1. Ground in docs and memory.
2. Map blast radius for non-trivial changes.
3. Implement the smallest coherent slice.
4. Verify with tests or runnable smoke checks.
5. Update docs and memory.
6. Commit verified increments when the user requests or authorizes a commit.

If work needs more than three corrective passes, stop and replan. Use sub-agents only when the active runtime instructions permit delegation.

## Verification Commands

- Install/update: `uv sync --extra dev`
- Tests: `uv run pytest`
- Demo smoke test: `uv run video-doc <video> --demo`
- Keyless real-transcript test: `uv run video-doc <video> --demo --transcript <meeting.vtt>`
- OCR smoke test: `uv run video-doc <video> --demo --transcript <meeting.vtt> --ocr auto`
- Evaluation: `uv run video-doc-eval <manifest.json> <fixture.json>`
- Review UI: `uv run streamlit run app.py`

Live model behavior requires `OPENAI_API_KEY`. Never treat deterministic output, even with a real sidecar transcript, as proof of live model quality.

## Demo Bias

Every feature should support the hackathon demo:

- Fast upload or sample-video path
- Clear progress through the pipeline
- Evidence-backed generated document
- Clickable timestamps or readable timestamp references
- A short README path that a judge can run
