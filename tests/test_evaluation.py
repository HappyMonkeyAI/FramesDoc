from pathlib import Path

from video_document_agent.evaluation import evaluate_manifest
from video_document_agent.models import (
    EvaluationFixture,
    EvidenceMoment,
    ExpectedMoment,
    FrameCandidate,
    GeneratedDocument,
    PipelineManifest,
    TranscriptSegment,
    VideoMetadata,
)


def test_evaluation_reports_recall_redundancy_grounding_and_ocr() -> None:
    frames = [
        FrameCandidate(
            timestamp=0,
            frame_path=Path("frame-0.jpg"),
            sources=["periodic"],
            novelty_score=1,
        ),
        FrameCandidate(
            timestamp=5,
            frame_path=Path("frame-5.jpg"),
            sources=["transcript_cue"],
            novelty_score=0.05,
        ),
    ]
    document = GeneratedDocument(
        title="Runbook",
        overview="Overview",
        moments=[
            EvidenceMoment(
                title="Run",
                kind="command",
                summary="Run it.",
                timestamp=5,
                frame_path=frames[1].frame_path,
                transcript_start=4,
                transcript_end=6,
                transcript_quote="Run uv sync",
                commands=["uv sync"],
                confidence=0.8,
                command_ocr_agreement=0.9,
            )
        ],
    )
    manifest = PipelineManifest(
        source_video=Path("source.mp4"),
        metadata=VideoMetadata(
            duration_seconds=10, width=100, height=100, fps=10, has_audio=True
        ),
        transcript=[
            TranscriptSegment(start=4, end=6, speaker="A", text="Run uv sync")
        ],
        frames=frames,
        document=document,
        markdown_path=Path("document.md"),
        html_path=Path("document.html"),
        demo_mode=True,
        transcript_source="sidecar",
    )
    fixture = EvaluationFixture(
        name="fixture",
        expected_moments=[
            ExpectedMoment(timestamp=5, tolerance=1, kind="command", label="command"),
            ExpectedMoment(timestamp=8, tolerance=0.5, kind="warning", label="warning"),
        ],
    )

    report = evaluate_manifest(manifest, fixture)

    assert report.useful_moment_recall == 0.5
    assert report.redundant_frame_rate == 1.0
    assert report.evidence_grounding_rate == 1.0
    assert report.command_ocr_agreement == 0.9
    assert report.unmatched_labels == ["warning"]
