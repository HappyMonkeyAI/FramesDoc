import shutil
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from video_document_agent.models import EvidenceMoment, FrameCandidate, GeneratedDocument
from video_document_agent.ocr import (
    _parse_tesseract_tsv,
    analyze_frames,
    command_agreement,
    corroborate_document,
)


def test_parses_tesseract_tsv_and_preserves_lines() -> None:
    tsv = """level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext
5\t1\t1\t1\t1\t1\t10\t20\t30\t10\t90.0\tuv
5\t1\t1\t1\t1\t2\t42\t20\t40\t10\t80.0\tsync
5\t1\t1\t1\t2\t1\t10\t40\t50\t10\t70.0\tready
"""

    text, confidence, words = _parse_tesseract_tsv(tsv)

    assert text == "uv sync\nready"
    assert confidence == pytest.approx(0.8)
    assert words[0].left == 10


def test_command_agreement_and_corroboration_remain_separate() -> None:
    assert command_agreement(["uv sync"], "Terminal output\n$ uv sync\nDone") == 1.0
    frame = FrameCandidate(
        timestamp=2,
        frame_path=Path("frame.jpg"),
        sources=["periodic"],
        novelty_score=1,
    )
    document = GeneratedDocument(
        title="Runbook",
        overview="Overview",
        moments=[
            EvidenceMoment(
                title="Install",
                kind="command",
                summary="Install packages.",
                timestamp=2,
                frame_path=frame.frame_path,
                transcript_start=1,
                transcript_end=3,
                visible_text="model text",
                commands=["uv sync"],
                confidence=0.8,
            )
        ],
    )
    from video_document_agent.models import OcrObservation

    result = corroborate_document(
        document,
        [
            OcrObservation(
                timestamp=2,
                frame_path=frame.frame_path,
                engine="tesseract",
                text="uv sync",
                mean_confidence=0.9,
            )
        ],
    )

    assert result.moments[0].visible_text == "model text"
    assert result.moments[0].ocr_text == "uv sync"
    assert result.moments[0].command_ocr_agreement == 1.0


@pytest.mark.skipif(not shutil.which("tesseract"), reason="Tesseract is not installed")
def test_tesseract_reads_high_contrast_frame(tmp_path: Path) -> None:
    image_path = tmp_path / "frame.jpg"
    image = Image.new("RGB", (900, 220), "white")
    font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    font = ImageFont.truetype(str(font_path), 64) if font_path.is_file() else ImageFont.load_default()
    ImageDraw.Draw(image).text((30, 60), "VIDEO DOC 123", fill="black", font=font)
    image.save(image_path)
    frame = FrameCandidate(
        timestamp=0,
        frame_path=image_path,
        sources=["periodic"],
        novelty_score=1,
    )

    observation = analyze_frames([frame], engine="tesseract")[0]

    assert "VIDEO" in observation.text.upper()
    assert observation.mean_confidence > 0.5
