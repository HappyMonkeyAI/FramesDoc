## Script

### 0:00–0:20 — Problem

**Action:** Show the README or repo homepage. Leave it still for a moment.

**Say:**  
“FramesDoc turns important knowledge buried in meeting videos into grounded documentation. Instead of scrubbing through recordings to find a command, demo, or warning, it extracts the useful moments and turns them into something the team can review and reuse.”

### 0:20–0:45 — Config

**Action:** Open `.env.example` or the relevant config file with the model settings visible.

**Say:**  
“This project uses OpenAI models for the live pipeline. Here the transcription model is `gpt-4o-transcribe-diarize`, and the analysis model is `gpt-5.6-sol`, which decides which moments are documentation-worthy and how to structure them.”

### 0:45–1:15 — Setup

**Action:** Switch to terminal and run setup or environment checks.

**Show:**
```sh
cd /home/stephen/projects/video-document-agent
uv sync --extra dev
tesseract --version
ffmpeg -version
```

**Say:**  
“I’ll show the local workflow on a sample meeting recording. The pipeline depends on Python, uv, FFmpeg, and Tesseract, because we combine transcript data, extracted frames, and OCR evidence.”

### 1:15–1:50 — Main run

**Action:** Clear the terminal, then paste the main command. Leave it visible before pressing Enter.

**Show:**
```sh
uv run video-doc demo/hackathon-demo.mp4 \
  --transcript demo/hackathon-demo.vtt \
  --ocr tesseract \
  --max-frames 20 \
  --frame-interval 8
```

**Say before Enter:**  
“This command processes the meeting recording, extracts candidate key moments, runs OCR on useful frames, and uses GPT-5.6-sol to turn that evidence into documentation.”

**Action:** Press Enter.

**While it runs, say:**  
“In the live path, the terminal logs the selected models, then moves through transcription, keyframe extraction, OCR, and analysis before writing the final document artifacts.”

## Runtime narration

At this point, it helps if your app prints a few clear lines in the terminal such as “Transcription model: gpt-4o-transcribe-diarize” and “Analysis model: gpt-5.6-sol,” because your runbook already distinguishes the deterministic rehearsal from the final live-model pass. Read those lines aloud briefly rather than explaining too much.

### 1:50–2:20 — Artifacts

**Action:** Show the output folder and key files.

**Show:**
```text
artifacts/<job>/
├── source.mp4
├── transcript.vtt
├── frames/
├── ocr.json
├── manifest.json
├── document.md
└── document.html
```

**Say:**  
“The important thing here is that FramesDoc does not just produce a summary. It creates an evidence-backed artifact set: retained frames, OCR output, a manifest of selected moments, and a generated document you can actually review and publish.”

### 2:20–3:00 — Review UI

**Action:** Launch the Streamlit app and show the review interface.

**Show:**
```sh
uv run streamlit run app.py
```

**Then show on screen:** video playback, screenshot, transcript quote, OCR text, accept/reject controls, edit fields, export buttons.

**Say:**  
“This is the review step. The reviewer can inspect the evidence for each extracted moment, see the screenshot, transcript span, and OCR corroboration, then accept or edit the description before export.”
“The source frame and timestamp remain fixed, so the generated documentation stays grounded in the original recording.”

### 3:00–3:25 — Verification

**Action:** Show the evaluation command.

**Show:**
```sh
uv run video-doc-eval \
  artifacts/<job>/manifest.json \
  evaluation/fixtures/demo-runbook.json
```

**Say:**  
“We also evaluate the extraction quality separately. This reports useful-moment recall, grounding, OCR agreement, and visual redundancy so we can check whether the system is actually finding the right moments instead of just generating plausible text.”

### 3:25–3:45 — Close

**Action:** End on the generated document or reviewed export.

**Say:**  
“So the result is a meeting recording turned into reusable documentation: screenshots, commands, explanations, and timestamped links back to the source. That makes team knowledge easier to recover, review, and share.”

## Small notes

The runbook recommends a demo scenario like a teammate onboarding walkthrough, because it naturally creates setup steps, commands, warnings, and verification moments that are visually distinct and easy for the system to capture. It also recommends keeping terminal font around 22–26 px and using a recording where the important screens stay visible long enough for extraction and OCR to work cleanly.

## Best tweak

If you can, make the live terminal output explicitly print:
- `Transcription model: gpt-4o-transcribe-diarize`
- `Analysis model: gpt-5.6-sol`
- `OCR engine: tesseract`
- `Writing manifest and document artifacts`

That will make the demo much easier to follow and will reinforce model usage without you having to over-explain it.