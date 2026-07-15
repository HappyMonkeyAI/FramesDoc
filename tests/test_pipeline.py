import shutil
import subprocess
from pathlib import Path

import pytest

from video_document_agent.pipeline import PipelineConfig, VideoDocumentPipeline


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg is required")
def test_demo_pipeline_creates_inspectable_artifacts(tmp_path: Path) -> None:
    video = tmp_path / "sample.mp4"
    result = subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=navy:s=320x180:r=12",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=16000",
            "-t",
            "3",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    manifest = VideoDocumentPipeline(
        PipelineConfig(
            artifacts_dir=tmp_path / "artifacts",
            demo_mode=True,
            max_frames=4,
            periodic_interval=1.5,
        )
    ).run(video)

    assert manifest.metadata.duration_seconds == pytest.approx(3, abs=0.1)
    assert manifest.frames
    assert manifest.document.moments
    assert manifest.markdown_path.is_file()
    assert manifest.html_path.is_file()
    assert (manifest.markdown_path.parent / "manifest.json").is_file()
    assert manifest.document.moments[0].frame_path.is_file()


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg is required")
def test_demo_pipeline_uses_sidecar_without_transcribing(tmp_path: Path) -> None:
    video = tmp_path / "silent.mp4"
    result = subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=320x180:r=12",
            "-t",
            "2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    transcript = tmp_path / "meeting.vtt"
    transcript.write_text(
        "WEBVTT\n\n00:00.000 --> 00:02.000\nAlex: Run the setup command.\n",
        encoding="utf-8",
    )

    manifest = VideoDocumentPipeline(
        PipelineConfig(
            artifacts_dir=tmp_path / "artifacts",
            demo_mode=True,
            transcript_path=transcript,
            max_frames=2,
        )
    ).run(video)

    assert manifest.transcript_source == "sidecar"
    assert manifest.transcript[0].speaker == "Alex"
    assert manifest.transcript_path is not None
    assert manifest.transcript_path.is_file()
    assert manifest.document.moments[0].transcript_quote == "Run the setup command."
