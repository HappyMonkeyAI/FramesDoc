# ADR 0004: Optional OCR And Diagnostic Evaluation

Date: 2026-07-15

## Status

Accepted

## Context

Command text is central to the product and costly to hallucinate. Model-visible text needs an independent signal, but installing a large OCR model stack would make the keyless hackathon workflow slower and less portable. The project also lacked a reproducible way to distinguish missed moments, redundant frames, unsupported citations, and command-reading errors.

## Decision

Integrate the locally available Tesseract CLI as an optional engine with `off`, `auto`, and explicit `tesseract` modes. Parse TSV output into text, word boxes, and normalized confidence. Keep this evidence separate from model-visible text and calculate command/OCR similarity only when both exist.

Evaluate generated manifests against independent timestamp labels. Report useful-moment recall, visual frame redundancy, evidence-grounding rate, and command/OCR agreement independently. Do not collapse them into a composite score.

## Consequences

- Keyless runs can corroborate dense on-screen text without another Python model dependency.
- OCR evidence is inspectable in `ocr.json` and rendered beside, not over, other evidence.
- Labelled fixtures make regressions measurable before live model access is available.
- Tesseract availability and language data vary by host; `auto` degrades to no OCR.
- Similarity and OCR confidence are diagnostics, not guarantees of correctness.
- Visual redundancy can include deliberately retained transcript-cued frames.

## Alternatives Considered

- PaddleOCR immediately: broader and potentially stronger, but heavier than necessary before measuring the simple baseline.
- Trust GPT-5.6 text alone: simpler, but provides no independent command corroboration.
- Replace model text with OCR: destroys source separation and can make lower-quality OCR look authoritative.
- One aggregate quality score: easy to present, but obscures which pipeline stage needs work.
