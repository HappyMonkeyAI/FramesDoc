# CONTEXT.md

## Current State

The repository contains a runnable vertical slice for one-video-to-one-document processing. It includes a CLI, Streamlit review UI, deterministic demo mode, OpenAI live adapter, hybrid frame selection, typed evidence contracts, Markdown/HTML rendering, and automated tests.

Live model behavior is implemented against the current OpenAI SDK but remains unverified without an `OPENAI_API_KEY`. Local media processing and the complete demo-mode pipeline are verified.

## Product Intent

Video Document Agent converts meeting recordings into useful internal documentation by combining:

- Hybrid keyframe extraction
- Timestamped, speaker-labelled transcript segments
- Vision analysis of frames
- LLM ranking and structured synthesis
- Evidence-backed Markdown and HTML output

The product is **documentation generation from ephemeral team knowledge**, not ordinary meeting summarization.

## Implemented Architecture

1. `media.probe_video`: inspect duration, dimensions, frame rate, and audio availability with ffprobe.
2. `media.extract_audio`: produce mono 16 kHz WAV with FFmpeg.
3. `OpenAIDocumentAgent.transcribe`: request diarized transcript segments.
4. `media.select_frames`: combine periodic samples, PySceneDetect boundaries, transcript cues, and perceptual novelty.
5. `OpenAIDocumentAgent.create_document`: send numbered frames plus nearby transcript through GPT-5.6 Structured Outputs.
6. `_reattach_evidence`: map model-selected frame indexes back to local paths and timestamps, and ground transcript quotations locally.
7. `render`: emit Markdown and portable HTML with media-fragment timestamp links.
8. `pipeline`: persist all intermediate artifacts and a typed JSON manifest.
9. `app.py`: show the video, evidence cards, commands, transcript quotes, limitations, and downloads.

## Evidence Contract

Each generated documentation moment retains:

- `timestamp`
- `frame_path`
- `transcript_start` and `transcript_end`
- A locally grounded `transcript_quote`
- `visible_text`
- `commands`
- `kind`
- `confidence`

The model returns a `frame_index`, not an arbitrary evidence path or timestamp. The application owns the final source mapping and discards transcript quotations that cannot be grounded in the closest source segment.

## Stack

- Python 3.12+
- `uv` and `pyproject.toml`
- FFmpeg/ffprobe
- PySceneDetect and OpenCV
- Pillow and NumPy for perceptual novelty
- OpenAI Python SDK and Pydantic Structured Outputs
- Streamlit
- pytest

## Model Choices

- `gpt-4o-transcribe-diarize` for meeting transcript segments and speaker labels.
- `gpt-5.6` for image understanding and structured documentation synthesis.
- `detail: original` for frames because terminal and UI screenshots contain dense text.

The analysis model accepts images rather than video, so audio and frame extraction remain explicit pipeline stages.

## Constraints

- Keep the workflow local-first and artifacts inspectable.
- Treat extracted commands as review-required evidence, never automatically executable instructions.
- Keep frame count bounded for cost and latency.
- Avoid Confluence work until the reviewable local document is convincing.
- Use a short, visually rich meeting recording for the demo.

## What Not To Do

- Do not build a generic meeting summary tool.
- Do not allow model output to define source paths or timestamps.
- Do not discard intermediate frames or transcript spans.
- Do not introduce multi-video retrieval before the single-video loop is evaluated on real meetings.
- Do not present deterministic demo-mode text as model analysis.

## Next Validation Targets

1. Run live mode on a 3–5 minute terminal walkthrough.
2. Measure useful-moment recall and redundant-frame rate.
3. Compare GPT-5.6 visible text against a deterministic OCR engine on command-heavy frames.
4. Add a human accept/edit/reject step before export.
