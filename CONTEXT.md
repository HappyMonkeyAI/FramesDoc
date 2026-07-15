# CONTEXT.md

## Current State

This repository is newly bootstrapped from `20260715-planning.txt`. There is no application code or runnable quickstart yet.

## Product Intent

Video Document Agent should convert meeting recordings into useful internal documentation by combining:

- Video keyframe extraction
- Timestamped transcript segmentation
- OCR or vision analysis of frames
- LLM ranking and synthesis
- Markdown, HTML, or Confluence-ready output

The strongest framing is **documentation generation from ephemeral team knowledge**, not ordinary meeting summarization.

## Hackathon Context

The project targets the OpenAI Build Week Devpost event. The likely category is Work & Productivity, with Developer Tools as a secondary fit if the demo focuses on engineering runbooks.

## MVP Architecture

1. `video_ingest`: accept a local MP4 and derive duration/timestamp metadata.
2. `transcript`: create or load transcript chunks with timestamps.
3. `keyframes`: extract candidate frames from visual changes and scene transitions.
4. `frame_understanding`: use OCR and/or vision analysis for each candidate frame.
5. `moment_selection`: use an OpenAI model to select documentation-worthy moments and assign labels.
6. `doc_generation`: emit markdown or HTML with evidence citations.
7. `review_ui`: provide a minimal way to inspect source frames, timestamps, and generated sections.

## Evidence Contract

Each generated section should retain:

- `video_timestamp`
- `frame_path`
- `transcript_start` and `transcript_end`
- `visible_text` or a structured frame observation
- `model_label`

This contract prevents the output from becoming an unsupported summary.

## Tooling Candidates

- `video-keyframe-detector`: reference for frame-difference-based keyframe extraction.
- `memvid`: possible later retrieval layer; not required for the first extraction loop.
- OpenAI multimodal and text models: central to moment understanding, classification, and documentation synthesis.

These are candidates from the planning note, not installed dependencies or finalized choices.

## Constraints

- Keep the first implementation local-first.
- Prefer inspectable intermediate artifacts over opaque one-shot generation.
- Avoid Confluence API work until markdown/HTML output is credible.
- Use small sample videos for smoke tests and demos.

## What Not To Do

- Do not build a generic meeting summary tool.
- Do not start with enterprise integrations.
- Do not discard timestamps or frame evidence after synthesis.
- Do not optimize for broad video search before the one-video document loop works.
