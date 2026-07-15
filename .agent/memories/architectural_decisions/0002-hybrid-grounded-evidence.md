---
type: semantic
tags: [architecture, frame-selection, evidence, openai, provenance]
created: 2026-07-15
related: [../../../docs/adr/0002-hybrid-frame-selection-and-grounded-output.md, ../../../CONTEXT.md]
blast_radius: [media, model-analysis, artifacts, ui]
confidence: high
---

# Hybrid And Grounded Evidence

## Status

Active

## Hidden Knowledge

Scene cuts are insufficient for terminal and UI walkthroughs because meaningful changes can be visually small. Candidate generation therefore combines periodic, scene, transcript-cue, and perceptual-novelty signals. Transcript cues are allowed through visual deduplication.

The model receives numbered evidence frames and returns frame indexes. Local code owns final paths and timestamps. Transcript quotations are checked against the nearest segment before persistence. This separation is a provenance boundary, not merely an implementation detail.

