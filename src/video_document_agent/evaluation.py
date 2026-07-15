"""Deterministic evaluation for moment coverage, redundancy, and grounding."""

from __future__ import annotations

import json
from pathlib import Path

from .models import EvaluationFixture, EvaluationReport, PipelineManifest


def load_fixture(path: Path) -> EvaluationFixture:
    return EvaluationFixture.model_validate_json(path.read_text(encoding="utf-8"))


def load_manifest(path: Path) -> PipelineManifest:
    return PipelineManifest.model_validate_json(path.read_text(encoding="utf-8"))


def evaluate_manifest(
    manifest: PipelineManifest,
    fixture: EvaluationFixture,
) -> EvaluationReport:
    available = set(range(len(manifest.document.moments)))
    matched = 0
    unmatched_labels: list[str] = []
    for expected in fixture.expected_moments:
        candidates = [
            index
            for index in available
            if abs(manifest.document.moments[index].timestamp - expected.timestamp)
            <= expected.tolerance
            and (
                expected.kind is None
                or manifest.document.moments[index].kind == expected.kind
            )
        ]
        if candidates:
            best = min(
                candidates,
                key=lambda index: abs(
                    manifest.document.moments[index].timestamp - expected.timestamp
                ),
            )
            available.remove(best)
            matched += 1
        else:
            unmatched_labels.append(expected.label or f"moment at {expected.timestamp:.3f}s")

    frame_pairs = max(0, len(manifest.frames) - 1)
    redundant = sum(
        frame.novelty_score < fixture.redundancy_threshold for frame in manifest.frames[1:]
    )
    grounded = sum(_moment_is_grounded(manifest, index) for index in range(len(manifest.document.moments)))
    agreements = [
        moment.command_ocr_agreement
        for moment in manifest.document.moments
        if moment.command_ocr_agreement is not None
    ]
    expected_count = len(fixture.expected_moments)
    generated_count = len(manifest.document.moments)
    return EvaluationReport(
        fixture_name=fixture.name,
        expected_moments=expected_count,
        matched_moments=matched,
        useful_moment_recall=matched / expected_count if expected_count else 1.0,
        redundant_frames=redundant,
        evaluated_frame_pairs=frame_pairs,
        redundant_frame_rate=redundant / frame_pairs if frame_pairs else 0.0,
        grounded_moments=grounded,
        generated_moments=generated_count,
        evidence_grounding_rate=grounded / generated_count if generated_count else 1.0,
        command_ocr_agreement=sum(agreements) / len(agreements) if agreements else None,
        unmatched_labels=unmatched_labels,
    )


def _moment_is_grounded(manifest: PipelineManifest, moment_index: int) -> bool:
    moment = manifest.document.moments[moment_index]
    frame_grounded = any(
        frame.frame_path.resolve() == moment.frame_path.resolve()
        and abs(frame.timestamp - moment.timestamp) <= 0.001
        for frame in manifest.frames
    )
    if not frame_grounded:
        return False
    if not moment.transcript_quote:
        return True
    return any(
        segment.start <= moment.transcript_end
        and segment.end >= moment.transcript_start
        and moment.transcript_quote.casefold() in segment.text.casefold()
        for segment in manifest.transcript
    )


def write_report(report: EvaluationReport, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    return path
