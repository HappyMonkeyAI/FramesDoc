---
type: decision
tags: [transcripts, review, provenance, keyless]
created: 2026-07-15
related: [../../../docs/adr/0003-sidecar-transcripts-and-non-destructive-review.md]
blast_radius: [pipeline, cli, ui, artifacts]
confidence: high
---

# Keyless Sidecars And Review Artifacts

SRT, WebVTT, and JSON sidecars bypass transcription, are copied into the job directory, and contribute to job identity. Human edits are written as separate review and reviewed-document artifacts. Video timestamps and frame paths stay immutable; transcript-span corrections remain auditable in `review.json`.
