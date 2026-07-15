# Evaluation Fixtures

Fixtures label documentation-worthy moments independently of generated output. Evaluate a manifest with:

```sh
uv run video-doc-eval artifacts/<job>/manifest.json evaluation/fixtures/demo-runbook.json
```

Each expected moment has a timestamp, matching tolerance, optional documentation kind, and human-readable label. The report records:

- Useful-moment recall: labelled moments matched once within their time window and optional kind.
- Redundant-frame rate: selected frames after the first whose novelty score is below the fixture threshold.
- Evidence-grounding rate: generated moments whose timestamp/frame maps to a selected frame and whose quotation maps to an overlapping transcript segment.
- Command/OCR agreement: mean normalized text similarity when both command and OCR evidence exist.

The included fixture matches the local 12-second smoke video used during development. Replace it with labels from the actual hackathon demo recording before using the numbers in a submission.
