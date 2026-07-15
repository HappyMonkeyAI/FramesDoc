---
type: semantic
tags: [architecture, mvp, evidence, local-first]
created: 2026-07-15
related: [../../../docs/adr/0001-mvp-video-to-docs-pipeline.md, ../../../CONTEXT.md]
blast_radius: [pipeline, storage, ui]
confidence: high
---

# Local-First Evidence Pipeline

## Status

Active

## Context

The initial target is a hackathon demo. Scope risk is high if the project starts with enterprise ingestion, Confluence synchronization, permissions, and multi-video retrieval.

## Decision

Start with a local pipeline that processes one MP4 into inspectable intermediate artifacts and a generated markdown or HTML document.

## Rationale

This makes the core value visible quickly: keyframes plus transcript plus model analysis become a timestamped runbook or knowledge page. It also lets future agents debug each stage independently.
