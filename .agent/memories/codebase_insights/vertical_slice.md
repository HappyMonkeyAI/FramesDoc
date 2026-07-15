---
type: semantic
tags: [pipeline, artifacts, streamlit, openai, ffmpeg]
created: 2026-07-15
related: [../../../README.md, ../../../CONTEXT.md, ../../../src/video_document_agent/pipeline.py]
blast_radius: [cli, ui, media, analysis, rendering]
confidence: high
---

# Runnable Vertical Slice

The first implementation processes one local video into a content-addressed artifact directory. `manifest.json` is the machine-readable source of truth; Markdown and HTML are projections for people.

Deterministic demo mode still probes the real video and extracts real frames, but its transcript and document content are synthetic and explicitly labelled. It exists for repeatable development and cannot validate live model quality.

The Streamlit UI is intentionally thin. Business logic belongs in `src/video_document_agent/`, so the CLI, tests, and future interfaces use the same pipeline.

