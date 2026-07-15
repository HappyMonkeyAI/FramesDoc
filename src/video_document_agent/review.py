"""Apply human review without mutating the original generated artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from .models import GeneratedDocument, PipelineManifest, ReviewRecord
from .render import render_html, render_markdown


def build_reviewed_document(
    original: GeneratedDocument,
    review: ReviewRecord,
) -> GeneratedDocument:
    seen: set[int] = set()
    moments = []
    for decision in review.decisions:
        if decision.original_index in seen:
            raise ValueError(f"duplicate review index: {decision.original_index}")
        seen.add(decision.original_index)
        if decision.original_index >= len(original.moments):
            raise ValueError(f"review index out of range: {decision.original_index}")
        if not decision.accepted:
            continue
        source = original.moments[decision.original_index]
        transcript_start = (
            decision.transcript_start
            if decision.transcript_start is not None
            else source.transcript_start
        )
        transcript_end = (
            decision.transcript_end if decision.transcript_end is not None else source.transcript_end
        )
        if transcript_end < transcript_start:
            raise ValueError("review transcript end must be at or after start")
        moments.append(
            source.__class__.model_validate(
                source.model_dump()
                | {
                    "title": decision.title.strip(),
                    "kind": decision.kind,
                    "summary": decision.summary.strip(),
                    "transcript_start": transcript_start,
                    "transcript_end": transcript_end,
                    "transcript_quote": decision.transcript_quote.strip(),
                    "visible_text": decision.visible_text.strip(),
                    "commands": [command.strip() for command in decision.commands if command.strip()],
                }
            )
        )
    return GeneratedDocument(
        title=review.title.strip(),
        overview=review.overview.strip(),
        moments=moments,
        limitations=original.limitations,
    )


def persist_review(manifest: PipelineManifest, review: ReviewRecord) -> PipelineManifest:
    document = build_reviewed_document(manifest.document, review)
    job_dir = manifest.source_video.parent
    markdown_path = render_markdown(document, manifest.source_video, job_dir / "document-reviewed.md")
    html_path = render_html(document, manifest.source_video, job_dir / "document-reviewed.html")
    reviewed_manifest = manifest.model_copy(
        update={
            "document": document,
            "markdown_path": markdown_path,
            "html_path": html_path,
        }
    )
    (job_dir / "review.json").write_text(
        json.dumps(review.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    (job_dir / "manifest-reviewed.json").write_text(
        json.dumps(reviewed_manifest.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    return reviewed_manifest
