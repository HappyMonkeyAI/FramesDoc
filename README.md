# Video Document Agent

Video Document Agent turns team meeting recordings into timestamped internal documentation. It targets meetings where important knowledge appears briefly on screen: terminal commands, setup walkthroughs, product demos, incident-review steps, and decisions that people later need to find again.

## Hackathon Pitch

An AI documentation agent that watches meeting recordings, finds the important on-screen moments, and turns them into linked runbooks and knowledge pages.

## Built With Codex And GPT-5.6

This project was created for [OpenAI Build Week](https://openai.devpost.com/) using **Codex with GPT-5.6**.

- **Codex accelerated the complete development workflow:** product research, architecture, implementation, test generation, debugging, documentation, demo planning, and incremental verification.
- **GPT-5.6 is part of the product:** live mode uses GPT-5.6 vision and Structured Outputs to turn selected video frames and nearby transcript evidence into typed documentation moments.
- **Key decisions are inspectable:** the local-first evidence contract, hybrid frame selection, grounded model output, sidecar transcripts, human review, OCR corroboration, and evaluation strategy are recorded in [`docs/adr/`](docs/adr/) and the Agents Protocol memory under [`.agent/memories/`](.agent/memories/).

The repository intentionally keeps generated claims traceable to source frames, video timestamps, and transcript spans. This reflects the central design direction developed with Codex: use GPT-5.6 for multimodal understanding while retaining provenance and human review in application-owned code.

## Current Vertical Slice

The runnable MVP accepts one local video and produces:

- Speaker-labelled transcript segments from OpenAI or SRT/VTT/JSON sidecars
- Hybrid keyframes selected from scene changes, periodic sampling, transcript cues, and visual novelty
- Optional Tesseract OCR with word confidence, bounding boxes, and command-text agreement
- GPT-5.6-generated setup, command, warning, decision, workflow, and reference moments
- Locally reattached evidence paths and timestamps that model output cannot override
- `manifest.json`, `document.md`, `document.html`, source video, audio, and extracted frames
- A Streamlit accept/edit/reject workflow with separate reviewed exports
- Labelled evaluation for moment recall, visual redundancy, evidence grounding, and OCR agreement

Deterministic mode performs real media probing and frame extraction. Without a sidecar it uses a synthetic transcript; with `--transcript` it uses the supplied real transcript for frame cues and evidence quotations. Document analysis remains deterministic and clearly labelled, making the complete workflow runnable without credentials.

## Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- FFmpeg and ffprobe on `PATH`
- Tesseract on `PATH` for optional local OCR
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

Run keyless with a real timestamped transcript:

```sh
uv run video-doc path/to/meeting.mp4 --demo --transcript path/to/meeting.vtt
```

Enable locally installed OCR corroboration:

```sh
uv run video-doc path/to/meeting.mp4 --demo --transcript path/to/meeting.vtt --ocr auto
```

Supported sidecars are SRT, WebVTT, and JSON. JSON may be a segment list or an object with a `segments` list; each segment needs `start`, `end`, and `text`, with optional `speaker`.

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

Evaluate a generated manifest against human-labelled moments:

```sh
uv run video-doc-eval artifacts/<job>/manifest.json evaluation/fixtures/demo-runbook.json
```

## Artifact Layout

Each video is stored under a content-derived job identifier:

```text
artifacts/<content-hash>/
├── source.mp4
├── audio.wav                 # when audio extraction is needed
├── transcript.vtt           # when a sidecar is supplied
├── ocr.json                 # when OCR is enabled
├── frames/
│   └── frame-<index>-<timestamp-ms>.jpg
├── manifest.json
├── document.md
├── document.html
├── review.json              # after human review
├── manifest-reviewed.json
├── document-reviewed.md
├── document-reviewed.html
└── evaluation.json          # after running video-doc-eval
```

The job identifier hashes both video and sidecar content, preventing different transcripts for the same video from overwriting each other. Original generated artifacts remain unchanged when a review is saved. Reviewers may adjust transcript spans, while the source video timestamp and frame path stay immutable.

Every documentation moment retains its source timestamp, frame path, transcript span, visible text, commands, classification, and confidence. Markdown and HTML timestamps link back to a media-fragment URL such as `source.mp4#t=12.500`.

OCR text never overwrites model-visible text. The manifest retains both sources plus the normalized agreement score for extracted commands. `ocr.json` also retains word-level locations and confidence values.

## Evaluation

Evaluation fixtures are independent JSON labels rather than snapshots of generated output. Current metrics are:

- Useful-moment recall within labelled timestamp windows and optional kinds
- Visual redundancy among selected frame pairs
- Evidence-grounding rate for frame/timestamp and transcript quotations
- Command/OCR agreement when both signals exist

See `evaluation/README.md`. The included fixture is a schema and smoke-test example; label the actual hackathon recording before reporting its metrics.

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
- Deterministic mode uses transcript evidence but does not interpret frame contents or replace GPT-5.6 synthesis quality.
- Tesseract confidence is an engine signal, not proof that command text is correct; command/OCR agreement is also heuristic.
- Scene detection and perceptual hashes are candidate filters, not guarantees that every useful terminal change is found.
- Model-read visible text should be reviewed before commands are executed.
- The HTML export is deliberately minimal; the Streamlit UI is the primary review experience.

## Project Docs

- `20260715-planning.txt` is the source planning conversation.
- `CONTEXT.md` captures current architecture and constraints.
- `DEMO.md` is the recording, rehearsal, evaluation, and live-pass runbook.
- `AGENTS.md` contains project-specific agent rules.
- `.agent/memories/` stores long-term memory for future agents.
- `docs/adr/` stores architecture decision records.
- `research/LINKS.md` records evaluated external projects and official documentation.
