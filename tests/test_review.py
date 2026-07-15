from pathlib import Path

from video_document_agent.models import (
    EvidenceMoment,
    FrameCandidate,
    GeneratedDocument,
    PipelineManifest,
    ReviewDecision,
    ReviewRecord,
    VideoMetadata,
)
from video_document_agent.review import build_reviewed_document, persist_review


def _moment(title: str, timestamp: float) -> EvidenceMoment:
    return EvidenceMoment(
        title=title,
        kind="reference",
        summary="Original",
        timestamp=timestamp,
        frame_path=Path(f"frame-{timestamp}.jpg"),
        transcript_start=timestamp,
        transcript_end=timestamp + 1,
        transcript_quote="Source quote",
        confidence=0.5,
    )


def test_review_edits_content_rejects_moment_and_preserves_evidence() -> None:
    original = GeneratedDocument(
        title="Draft",
        overview="Draft overview",
        moments=[_moment("First", 2), _moment("Second", 4)],
    )
    review = ReviewRecord(
        title="Reviewed",
        overview="Reviewed overview",
        decisions=[
            ReviewDecision(
                original_index=0,
                accepted=True,
                title="Install dependencies",
                kind="setup",
                summary="Install before launch.",
                transcript_start=1.5,
                transcript_end=3.5,
                transcript_quote="Edited quotation",
                commands=["uv sync"],
            ),
            ReviewDecision(
                original_index=1,
                accepted=False,
                title="Second",
                kind="reference",
                summary="Original",
            ),
        ],
    )

    result = build_reviewed_document(original, review)

    assert result.title == "Reviewed"
    assert len(result.moments) == 1
    assert result.moments[0].commands == ["uv sync"]
    assert result.moments[0].timestamp == 2
    assert result.moments[0].transcript_start == 1.5
    assert result.moments[0].transcript_end == 3.5
    assert result.moments[0].frame_path == original.moments[0].frame_path


def test_persist_review_writes_separate_audit_and_exports(tmp_path: Path) -> None:
    source_video = tmp_path / "source.mp4"
    source_video.touch()
    frame_path = tmp_path / "frames" / "frame.jpg"
    frame_path.parent.mkdir()
    frame_path.touch()
    original_document = GeneratedDocument(
        title="Draft", overview="Draft overview", moments=[_moment("First", 2)]
    )
    original_markdown = tmp_path / "document.md"
    original_markdown.write_text("original", encoding="utf-8")
    manifest = PipelineManifest(
        source_video=source_video,
        metadata=VideoMetadata(
            duration_seconds=5, width=320, height=180, fps=12, has_audio=False
        ),
        transcript=[],
        frames=[
            FrameCandidate(
                timestamp=2,
                frame_path=frame_path,
                sources=["periodic"],
                novelty_score=1,
            )
        ],
        document=original_document,
        markdown_path=original_markdown,
        html_path=tmp_path / "document.html",
        demo_mode=True,
        transcript_source="none",
    )
    review = ReviewRecord(
        title="Reviewed",
        overview="Ready",
        decisions=[
            ReviewDecision(
                original_index=0,
                title="Accepted",
                kind="reference",
                summary="Reviewed summary",
            )
        ],
    )

    reviewed = persist_review(manifest, review)

    assert reviewed.markdown_path.name == "document-reviewed.md"
    assert reviewed.markdown_path.is_file()
    assert reviewed.html_path.is_file()
    assert (tmp_path / "review.json").is_file()
    assert (tmp_path / "manifest-reviewed.json").is_file()
    assert original_markdown.read_text(encoding="utf-8") == "original"
