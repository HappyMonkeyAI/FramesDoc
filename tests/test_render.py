from pathlib import Path

from video_document_agent.models import EvidenceMoment, GeneratedDocument
from video_document_agent.render import render_html, render_markdown


def _document() -> GeneratedDocument:
    return GeneratedDocument(
        title="Deploy service",
        overview="A short runbook.",
        moments=[
            EvidenceMoment(
                title="Start service",
                kind="command",
                summary="Run the service.",
                timestamp=12.5,
                frame_path=Path("frames/frame.jpg"),
                transcript_start=10,
                transcript_end=14,
                transcript_quote="Run this command.",
                visible_text="uv run app",
                commands=["uv run app"],
                confidence=0.9,
            )
        ],
    )


def test_markdown_contains_timestamp_evidence(tmp_path: Path) -> None:
    path = render_markdown(_document(), Path("source.mp4"), tmp_path / "document.md")
    content = path.read_text()
    assert "source.mp4#t=12.500" in content
    assert "frames/frame.jpg" in content
    assert "uv run app" in content


def test_html_escapes_model_content(tmp_path: Path) -> None:
    document = _document()
    document.moments[0].summary = "Use <script>alert(1)</script> safely."
    path = render_html(document, Path("source.mp4"), tmp_path / "document.html")
    content = path.read_text()
    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;" in content
    assert "source.mp4#t=12.500" in content

