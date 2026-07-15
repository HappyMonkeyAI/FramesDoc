# ADR 0001: MVP Video-To-Documentation Pipeline

Date: 2026-07-15

## Status

Accepted

## Context

The project is a hackathon entry intended to turn team meeting videos into timestamped documentation. The planning note emphasizes meetings where valuable information is shown on screen, such as terminal commands, setup tutorials, and product walkthroughs.

## Decision

Build the first version as a local, evidence-preserving pipeline:

1. Ingest one meeting video.
2. Generate or load timestamped transcript chunks.
3. Extract candidate keyframes.
4. Analyze frames with OCR and/or a vision model.
5. Use an OpenAI model to select and label documentation-worthy moments.
6. Generate markdown or HTML with screenshots, transcript context, and timestamps.

## Consequences

This keeps the demo focused and inspectable. Confluence publishing, multi-video retrieval, and enterprise ingestion remain later integrations after the one-video loop produces useful output.
