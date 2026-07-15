"""Orchestrate the inspectable one-video-to-one-document workflow."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

from pydantic import BaseModel, Field

from .media import extract_audio, probe_video, select_frames
from .models import PipelineManifest
from .openai_analysis import DemoDocumentAgent, OpenAIDocumentAgent
from .render import render_html, render_markdown


class PipelineConfig(BaseModel):
    artifacts_dir: Path = Path("artifacts")
    demo_mode: bool = False
    periodic_interval: float = Field(default=4.0, ge=0.5)
    novelty_threshold: float = Field(default=0.12, ge=0, le=1)
    max_frames: int = Field(default=30, ge=1, le=100)
    transcription_model: str = "gpt-4o-transcribe-diarize"
    analysis_model: str = "gpt-5.6"


class VideoDocumentPipeline:
    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()

    def run(self, video_path: Path) -> PipelineManifest:
        video_path = video_path.resolve()
        if not video_path.is_file():
            raise FileNotFoundError(video_path)
        job_id = _content_hash(video_path)
        job_dir = self.config.artifacts_dir.resolve() / job_id
        frames_dir = job_dir / "frames"
        job_dir.mkdir(parents=True, exist_ok=True)
        source_video = job_dir / f"source{video_path.suffix.lower() or '.mp4'}"
        if source_video != video_path:
            shutil.copy2(video_path, source_video)

        metadata = probe_video(source_video)
        agent = self._agent()
        if metadata.has_audio:
            audio_path = extract_audio(source_video, job_dir / "audio.wav")
            transcript = agent.transcribe(audio_path)
        elif self.config.demo_mode:
            transcript = agent.transcribe(job_dir / "audio.wav")
        else:
            transcript = []

        frames = select_frames(
            source_video,
            frames_dir,
            metadata,
            transcript,
            periodic_interval=self.config.periodic_interval,
            novelty_threshold=self.config.novelty_threshold,
            max_frames=self.config.max_frames,
        )
        document = agent.create_document(frames, transcript)
        markdown_path = render_markdown(document, source_video, job_dir / "document.md")
        html_path = render_html(document, source_video, job_dir / "document.html")
        manifest = PipelineManifest(
            source_video=source_video,
            metadata=metadata,
            transcript=transcript,
            frames=frames,
            document=document,
            markdown_path=markdown_path,
            html_path=html_path,
            demo_mode=self.config.demo_mode,
        )
        (job_dir / "manifest.json").write_text(
            json.dumps(manifest.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        return manifest

    def _agent(self) -> DemoDocumentAgent | OpenAIDocumentAgent:
        if self.config.demo_mode:
            return DemoDocumentAgent()
        return OpenAIDocumentAgent(
            api_key=os.getenv("OPENAI_API_KEY"),
            transcription_model=os.getenv(
                "VIDEO_DOC_TRANSCRIPTION_MODEL", self.config.transcription_model
            ),
            analysis_model=os.getenv("VIDEO_DOC_ANALYSIS_MODEL", self.config.analysis_model),
        )


def _content_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:12]

