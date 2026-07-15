# ADR 0002: Hybrid Frame Selection And Locally Grounded Output

Date: 2026-07-15

## Status

Accepted

## Context

Scene-change detection alone is poorly matched to screen-shared terminals and applications. A valuable command can appear as a small text change inside an otherwise static scene. Sending every frame to a vision model is too expensive and makes evidence review noisy.

Model-generated paths, timestamps, and transcript quotations would also weaken provenance because those values could be malformed or unsupported.

## Decision

Generate frame candidates from four signals:

1. Periodic safety sampling
2. PySceneDetect scene boundaries and midpoints
3. Transcript segments containing documentation cues
4. Perceptual-hash novelty

Transcript-cued candidates survive visual deduplication, and a configurable frame budget bounds analysis cost.

Ask the model to select numbered frame indexes through a structured Pydantic schema. Reattach frame paths and timestamps locally. Retain a model-proposed transcript quote only when it occurs in the closest transcript segment; otherwise use that source segment verbatim.

## Consequences

- Static screen shares can still produce candidate moments.
- The model cannot redirect evidence to nonexistent files or timestamps.
- Frame count and cost remain bounded.
- Small on-screen changes without transcript cues can still be missed by perceptual hashing.
- Command text remains review-required because vision extraction is not deterministic verification.

## Alternatives Considered

- `video-keyframe-detector`: simple, but GPL-3.0 and less mature than PySceneDetect.
- Fixed-interval sampling only: predictable but redundant and insensitive to meeting meaning.
- Academic adaptive video sampling: promising, but too operationally heavy for the hackathon slice.
- Full-video model input: unsupported by the selected GPT-5.6 model and less inspectable.

