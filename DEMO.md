# Hackathon Demo Video Runbook

## Goal

Record one 3–5 minute screen-sharing walkthrough that demonstrates ephemeral team knowledge becoming a grounded runbook.

## 1. Demo Scenario

Record a teammate onboarding walkthrough titled:

> How to run Video Document Agent locally without an API key

This naturally provides:

- Workspace setup
- Commands worth preserving
- Configuration guidance
- A safety warning
- A verification step
- Visually distinct screens

## 2. Prepare The Recording

Before recording:

- Use 1920×1080 resolution.
- Increase terminal font to at least 22–26 px.
- Hide notifications, credentials, usernames, and unrelated tabs.
- Use placeholder API keys only.
- Prepare commands in a scratch file to avoid typing mistakes.
- Keep each important screen visible for at least 4 seconds.
- Use three clearly different visual states:
  - README or file browser
    - Terminal
      - Generated artifact or review screen

      Create a clean sample input name:

      ```text
      input.mp4
      ```

      ## 3. Suggested Timeline

      ### 00:00–00:30 — Introduce The Problem

      Show the project README.

      Say:

      > This project turns screen-shared meeting knowledge into evidence-backed documentation. I’ll show the keyless local workflow.

      Avoid a long product introduction. The pipeline needs actionable spoken and visual evidence.

      ### 00:30–01:15 — Setup Moment

      Show the repository and terminal.

      Say explicit cue words:

      > Open the project workspace and make sure Python, uv, FFmpeg, and Tesseract are available.

      Show:

      ```sh
      cd /home/stephen/projects/video-document-agent
      uv sync --extra dev
      tesseract --version
      ffmpeg -version
      ```

      Keep the successful output visible briefly.

      Expected classification: `setup`.

      ### 01:15–02:00 — Command Moment

      Clear the terminal so the main command is visually isolated.

      Say:

      > Run this command with the timestamped transcript to generate the keyless runbook and OCR evidence.

      Show:

      ```sh
      uv run video-doc input.mp4 \
        --demo \
          --transcript input.vtt \
            --ocr auto
            ```

            Keep the complete command visible for 5–8 seconds.

            Expected classification: `command`.

            ### 02:00–02:40 — Warning Moment

            Show the generated artifact directory.

            Say:

            > The important warning is that deterministic mode validates the pipeline, but it does not validate GPT-5.6 synthesis quality. Always review commands before executing them.

            Show:

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

            Expected classification: `warning`.

            ### 02:40–03:30 — Review Workflow

            Launch the interface:

            ```sh
            uv run streamlit run app.py
            ```

            Show:

            - Video playback
            - Evidence screenshot
            - Transcript quotation
            - OCR corroboration
            - Accept/reject control
            - Editable summary and transcript span
            - Reviewed export buttons

            Say:

            > The reviewer can correct descriptive content and transcript spans, but the source frame and video timestamp remain fixed.

            ### 03:30–04:00 — Verification

            Show the evaluation command:

            ```sh
            uv run video-doc-eval \
              artifacts/<job>/manifest.json \
                evaluation/fixtures/hackathon-demo.json
                ```

                Explain that recall, visual redundancy, grounding, and OCR agreement are reported separately.

                ## 4. Produce The Transcript

                Prefer an exported WebVTT transcript. If necessary, create one manually:

                ```vtt
                WEBVTT

                00:00:30.000 --> 00:01:15.000
                Stephen: Open the project workspace and make sure Python, uv, FFmpeg, and Tesseract are available.

                00:01:15.000 --> 00:02:00.000
                Stephen: Run this command with the timestamped transcript to generate the keyless runbook and OCR evidence.

                00:02:00.000 --> 00:02:40.000
                Stephen: The important warning is that deterministic mode validates the pipeline, but it does not validate GPT-5.6 synthesis quality.

                00:02:40.000 --> 00:03:30.000
                Stephen: The reviewer can correct the content while the source frame and video timestamp remain fixed.
                ```

                Use actual recording timestamps rather than copying these blindly.

                ## 5. Run The Keyless Rehearsal

                ```sh
                uv run video-doc demo/hackathon-demo.mp4 \
                  --demo \
                    --transcript demo/hackathon-demo.vtt \
                      --ocr tesseract \
                        --max-frames 20 \
                          --frame-interval 8
                          ```

                          Inspect:

                          - `manifest.json`
                          - Every retained frame
                          - Transcript spans
                          - `ocr.json`
                          - `document.md`
                          - The HTML export

                          Deterministic document text is template-based. Judge this rehearsal on evidence capture, OCR, review UX, and artifact integrity—not synthesis quality.

                          ## 6. Create Independent Labels

                          Create `evaluation/fixtures/hackathon-demo.json` before looking at the generated document:

                          ```json
                          {
                            "name": "Hackathon onboarding walkthrough",
                              "redundancy_threshold": 0.12,
                                "expected_moments": [
                                    {
                                          "label": "local prerequisites",
                                                "timestamp": 30,
                                                      "tolerance": 8,
                                                            "kind": "setup"
                                                                },
                                                                    {
                                                                          "label": "keyless generation command",
                                                                                "timestamp": 75,
                                                                                      "tolerance": 8,
                                                                                            "kind": "command"
                                                                                                },
                                                                                                    {
                                                                                                          "label": "deterministic mode warning",
                                                                                                                "timestamp": 120,
                                                                                                                      "tolerance": 8,
                                                                                                                            "kind": "warning"
                                                                                                                                }
                                                                                                                                  ]
                                                                                                                                  }
                                                                                                                                  ```

                                                                                                                                  Adjust timestamps to the actual recording, not the generated selections.

                                                                                                                                  ## 7. Acceptance Gates

                                                                                                                                  The recording is demo-ready when:

                                                                                                                                  - All three labelled moments have useful evidence frames.
                                                                                                                                  - Command text is legible in the extracted JPEG.
                                                                                                                                  - Tesseract captures the main command accurately enough to review.
                                                                                                                                  - Evidence grounding is 100%.
                                                                                                                                  - Useful-moment recall is 100% for the three core labels.
                                                                                                                                  - Visual redundancy is understood and preferably below 40%.
                                                                                                                                  - The Streamlit review produces separate reviewed artifacts.
                                                                                                                                  - No secrets or personal information appear in any frame.
                                                                                                                                  - The complete workflow finishes comfortably within the presentation time.

                                                                                                                                  ## 8. Final Live-Model Pass

                                                                                                                                  When an API key becomes available:

                                                                                                                                  ```sh
                                                                                                                                  export OPENAI_API_KEY="your-key"

                                                                                                                                  uv run video-doc demo/hackathon-demo.mp4 \
                                                                                                                                    --transcript demo/hackathon-demo.vtt \
                                                                                                                                      --ocr tesseract \
                                                                                                                                        --max-frames 20 \
                                                                                                                                          --frame-interval 8
                                                                                                                                          ```

                                                                                                                                          Compare the live and deterministic manifests. The final submission should demonstrate live GPT-5.6 synthesis, while the keyless rehearsal remains the repeatable fallback.

                                                                                                                                          The most important recording constraint is visual clarity: large text, deliberate screen changes, explicit spoken cue words, and several seconds of dwell time on every command or warning.
                                                                                                                                          