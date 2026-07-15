# Video Document Agent

Video Document Agent turns team meeting recordings into timestamped internal documentation. It targets meetings where important knowledge appears briefly on screen: terminal commands, setup walkthroughs, product demos, incident-review steps, and decisions that people later need to find again.

## Hackathon Pitch

An AI documentation agent that watches meeting recordings, finds the important on-screen moments, and turns them into linked runbooks and knowledge pages.

## Current Vertical Slice

The runnable MVP accepts one local video and produces:

- Speaker-labelled transcript segments in live mode
- Hybrid keyframes selected from scene changes, periodic sampling, transcript cues, and visual novelty
- GPT-5.6-generated setup, command, warning, decision, workflow, and reference moments
- Locally reattached evidence paths and timestamps that model output cannot override
- `manifest.json`, `document.md`, `document.html`, source video, audio, and extracted frames
- A Streamlit review/download interface

Deterministic demo mode performs real media probing and frame extraction but uses clearly labelled synthetic transcript and document content. This makes the pipeline runnable without credentials and keeps tests independent of model availability.

## Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- FFmpeg and ffprobe on `PATH`
- An OpenAI API key for live mode

## Quickstart

Install the locked environment:

```sh
uv sync --extra dev
```

Run the deterministic local workflow:

```sh
uv run video-doc path/to/meeting.mp4 --demo
```

Run live analysis:

```sh
export OPENAI_API_KEY="your-key"
uv run video-doc path/to/meeting.mp4
```

`.env.example` documents the supported environment variables; the application reads them from the process environment.

Launch the review UI:

```sh
uv run streamlit run app.py
```

Run the test suite:

```sh
uv run pytest
```

## Artifact Layout

Each video is stored under a content-derived job identifier:

```text
artifacts/<video-hash>/
├── source.mp4
├── audio.wav
├── frames/
│   └── frame-<index>-<timestamp-ms>.jpg
├── manifest.json
├── document.md
└── document.html
```

Every documentation moment retains its source timestamp, frame path, transcript span, visible text, commands, classification, and confidence. Markdown and HTML timestamps link back to a media-fragment URL such as `source.mp4#t=12.500`.

## Model Defaults

- Transcription: `gpt-4o-transcribe-diarize`
- Evidence selection and documentation synthesis: `gpt-5.6`
- Frame detail: `original`, because terminal and UI text can be spatially dense

Override model names with `VIDEO_DOC_TRANSCRIPTION_MODEL` and `VIDEO_DOC_ANALYSIS_MODEL`.

## Non-Goals For This Slice

- Full enterprise video ingestion
- Confluence synchronization
- Permission and identity management
- Long-term semantic search across many recordings
- Browser or desktop meeting capture
- Perfect OCR or command verification

## Known Limitations

- Live OpenAI calls require credentials and were not exercised during the credential-free bootstrap.
- Scene detection and perceptual hashes are candidate filters, not guarantees that every useful terminal change is found.
- Model-read visible text should be reviewed before commands are executed.
- The HTML export is deliberately minimal; the Streamlit UI is the primary review experience.

## Project Docs

- `20260715-planning.txt` is the source planning conversation.
- `CONTEXT.md` captures current architecture and constraints.
- `AGENTS.md` contains project-specific agent rules.
- `HERMES.md` records the local Agents Protocol operating loop.
- `.agent/memories/` stores long-term memory for future agents.
- `docs/adr/` stores architecture decision records.
- `research/LINKS.md` records evaluated external projects and official documentation.
