---
type: decision
tags: [ocr, evaluation, grounding, keyless]
created: 2026-07-15
related: [../../../docs/adr/0004-optional-ocr-and-diagnostic-evaluation.md]
blast_radius: [pipeline, artifacts, cli, ui, evaluation]
confidence: high
---

# Optional OCR And Separate Diagnostic Metrics

Tesseract is optional and emits a distinct `ocr.json` evidence source with word confidence and boxes. OCR never overwrites model-visible text. Evaluation reports moment recall, visual redundancy, grounding, and command/OCR agreement separately rather than as a composite.
