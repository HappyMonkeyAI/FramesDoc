---
type: episodic
tags: [implementation, vertical-slice, verification, research]
created: 2026-07-15
related: [../../../README.md, ../../../docs/adr/0002-hybrid-frame-selection-and-grounded-output.md]
blast_radius: [application, docs, memory, research]
confidence: high
---

# 2026-07-15 Vertical Spike

## Outcome

Implemented the first runnable video-to-documentation loop with FFmpeg, PySceneDetect, OpenAI adapters, Pydantic evidence contracts, Markdown/HTML output, a CLI, and a Streamlit review UI.

## Verification

- Unit and integration tests passed.
- A generated MP4 with audio completed the deterministic pipeline and produced real frames, a manifest, Markdown, and HTML.
- Streamlit started successfully and returned `ok` from its health endpoint.
- Live OpenAI calls were not run because `OPENAI_API_KEY` was unset.

## Research Applied

- PySceneDetect replaced `video-keyframe-detector` as the preferred permissive scene detector.
- VideoLens validated the cached timeline/evidence architecture but was kept as a reference to preserve project differentiation.
- Mimik informed export/review ideas.
- Zoom's RTMS starter kit validated screen-share deduplication and transcript-linked playback patterns, but its code has no visible license and was not copied.

