# ADR 0003: Sidecar Transcripts And Non-Destructive Review

Date: 2026-07-15

## Status

Accepted

## Context

API credentials are not always available during local development, and many meeting platforms already export timestamped captions. The original deterministic mode used only a synthetic transcript, which could validate media plumbing but not transcript-driven evidence selection on real content.

Interactive editing also causes Streamlit reruns. Holding a generated manifest only inside the button branch loses the document on the first edit, while overwriting original output would destroy the distinction between generated and reviewed evidence.

## Decision

Accept SRT, WebVTT, and JSON transcript sidecars. A sidecar bypasses transcription, is copied into the artifact directory, and participates in the content-derived job identifier.

Persist the active manifest in Streamlit session state. Record accept/edit/reject decisions separately in `review.json`, and render accepted edits to `document-reviewed.md`, `document-reviewed.html`, and `manifest-reviewed.json`. Keep video timestamps and frame paths immutable; permit transcript-span corrections and retain them in the review audit.

## Consequences

- The media, evidence-selection, review, and export loop can use real transcript evidence without an API key.
- Different sidecars for the same video cannot overwrite one another.
- Generated and human-reviewed claims remain distinguishable and auditable.
- Sidecars must contain timestamped segments; plain text is intentionally insufficient.
- Deterministic analysis still does not validate OpenAI vision or synthesis quality.

## Alternatives Considered

- Run a local Whisper stack: useful later, but adds model downloads and hardware variability.
- Accept plain text: easy to ingest, but cannot ground frame cues or evidence spans.
- Overwrite `document.md`: simpler, but loses the original generation and review audit trail.
- Make video timestamps or frame paths editable: flexible, but weakens provenance and can point claims at unrelated visual evidence.
