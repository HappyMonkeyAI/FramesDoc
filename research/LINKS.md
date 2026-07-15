# Research Links

Research was reviewed on 2026-07-15. “Use” describes current intent, not an installed or shipped integration unless explicitly stated.

## Transcript Sidecar Standards

- WebVTT specification: https://www.w3.org/TR/webvtt1/
- SubRip SRT format description: https://www.loc.gov/preservation/digital/formats/fdd/fdd000569.shtml
- Use: Keyless timestamped transcript interchange from meeting platforms and caption exporters.
- Applied: Local SRT/VTT import, WebVTT voice-tag parsing, speaker-prefix parsing, and transcript-driven frame cues.
- JSON extension: Accept a simple typed segment list for programmatic fixtures and integrations.

## OpenAI Build Week / Devpost

- URL: https://openai.devpost.com/
- Use: Submission context and category fit.
- Notes: Frame the project as Work & Productivity unless implementation becomes strongly developer-tool specific.

## OpenAI API Documentation

- GPT-5.6 model: https://developers.openai.com/api/docs/models/gpt-5.6
- Images and vision: https://developers.openai.com/api/docs/guides/images-vision
- Speech to text: https://developers.openai.com/api/docs/guides/speech-to-text
- Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs
- Use: Verify current modalities, multi-image input, `detail: original`, diarized transcription, and Pydantic-backed output parsing.
- Applied: `gpt-4o-transcribe-diarize`, GPT-5.6 image analysis, and locally grounded structured evidence.
- Constraint: GPT-5.6 accepts image and text input, not meeting-video input; media decomposition remains necessary.

## PySceneDetect

- URL: https://github.com/Breakthrough/PySceneDetect
- License: BSD-3-Clause.
- Use: Scene boundaries and midpoints inside hybrid candidate generation.
- Applied: `AdaptiveDetector` plus independent periodic, transcript-cue, and novelty signals.
- Avoid: Treating scene boundaries as sufficient for static terminal or UI content.

## VideoLens

- URL: https://github.com/shadoprizm/videolens
- License: MIT.
- Use: Architecture comparator for cached extraction, time-windowed evidence, frame budgets, and Markdown/JSON output.
- Cherry-pick: Inspectable intermediate timeline and cost-aware frame caps.
- Avoid: Cloning the product or reducing this entry to generic video reporting. Differentiate through durable runbooks, command extraction, evidence review, and knowledge publishing.
- Maturity note: Early alpha with little adoption at review time.

## Zoom RTMS Meeting Assistant Starter Kit

- URL: https://github.com/zoom/rtms-meeting-assistant-starter-kit
- License: No visible repository license at review time.
- Use: Reference for screen-share frame deduplication, timestamp logs, transcript-linked playback, and per-meeting artifact layout.
- Avoid: Copying code without explicit licensing; live Zoom ingestion is post-MVP.

## Mimik

- URL: https://github.com/westpoint-io/mimik
- License: MIT.
- Use: Reference for step review, annotated screenshots, sensitive-data blur, and Markdown/HTML/PDF export.
- Cherry-pick: Human review and multi-format guide UX.
- Avoid: Browser event capture in the current uploaded-video slice.

## PaddleOCR

- URL: https://github.com/PaddlePaddle/PaddleOCR
- License: Apache-2.0.
- Use: Candidate deterministic OCR corroboration for command-heavy frames.
- Cherry-pick: Text boxes and structured coordinates for reviewing terminal/UI text.
- Avoid: Adding the full document parsing stack before measuring GPT-5.6 command accuracy.

## Tesseract OCR

- Repository: https://github.com/tesseract-ocr/tesseract
- Command-line TSV reference: https://github.com/tesseract-ocr/tesseract/wiki/Command-Line-Usage
- License: Apache-2.0; Leptonica has its own BSD-2-Clause terms.
- Use: Lightweight local corroboration for selected English-language terminal and UI frames.
- Applied: Optional subprocess integration, TSV word boxes/confidence, `ocr.json`, and command-text agreement.
- Observed: The generated OCR smoke video read `uv sync` with 95% mean word confidence.
- Avoid: Treating confidence or string similarity as correctness; PaddleOCR remains a later multilingual/complex-layout comparator.

## video-analyzer

- URL: https://github.com/byjlw/video-analyzer
- License: Apache-2.0.
- Use: Reference for a modular frame extraction, transcription, frame-analysis, and JSON pipeline.
- Cherry-pick: Prompt isolation and configurable local/cloud analysis stages.
- Avoid: Generic chronological video description as the final product.

## WhisperX And pyannote.audio

- URLs:
  - https://github.com/m-bain/whisperX
  - https://github.com/pyannote/pyannote-audio
- Licenses: BSD-2-Clause and MIT respectively; pretrained model terms must be reviewed separately.
- Use: Possible offline transcription, alignment, and speaker-diarization fallback.
- Avoid: GPU/model-download complexity in the primary hackathon workflow.

## Millet

- URL: https://github.com/pretyflaco/millet
- License: GPL-3.0.
- Use: Reference for typed meeting frontmatter, decisions, actions, participants, and source metadata.
- Cherry-pick: Versioned machine-readable meeting schema concepts.
- Avoid: Direct dependency in the permissive MVP and its heavier recording/local-model stack.

## Memvid

- URL: https://github.com/memvid/memvid
- License: Apache-2.0.
- Use: Possible later searchable memory layer across extracted meeting artifacts.
- Cherry-pick: Portable retrieval and image/audio feature concepts after the MVP works.
- Avoid: Adding retrieval before one-video extraction and documentation are evaluated.

## video-keyframe-detector

- URL: https://github.com/joelibaceta/video-keyframe-detector
- License: GPL-3.0.
- Use: Historical idea reference for frame-difference peak estimation.
- Decision: Do not use as the primary dependency; PySceneDetect is more mature and permissively licensed.

## Screenpipe

- URL: https://github.com/screenpipe/screenpipe
- License: Source-available Screenpipe Commercial License at review time.
- Use: Reference for event-driven capture, accessibility-first text, OCR fallback, and content permissions.
- Avoid: Core dependency because commercial use requires separate licensing and continuous desktop capture is outside the MVP.

## Adaptive Keyframe Sampling

- URL: https://github.com/ncTimTang/AKS
- Use: Research support for balancing prompt relevance with visual coverage.
- Cherry-pick: Relevance-plus-coverage principle.
- Avoid: Its heavy BLIP/CLIP/LLaVA evaluation stack for the hackathon.

## Video-RAG

- URL: https://github.com/Leon1207/Video-RAG-master
- Use: Research support for aligning OCR, ASR, object signals, and selected frames.
- Cherry-pick: Treat OCR and ASR as time-aligned evidence rather than one flattened transcript.
- Avoid: Research-model installation and multi-video retrieval before the local runbook loop works.

## Agents Protocol

- URL: https://github.com/HappyMonkeyAI/AgentsProtocol
- Use: Agent workflow, documentation spine, and long-term memory conventions.
- Applied: `.agent/memories/`, `AGENTS.md`, `CONTEXT.md`, ADRs, research notes, grounding, and incremental verification.
