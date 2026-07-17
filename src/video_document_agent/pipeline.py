"""Orchestrate the inspectable one-video-to-one-document workflow."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .media import extract_audio, probe_video, select_frames
from .models import PipelineManifest
from .openai_analysis import DemoDocumentAgent, OpenAIDocumentAgent
from .ocr import analyze_frames, corroborate_document, resolve_ocr_engine, write_ocr_artifact
from .render import render_html, render_markdown
from .transcripts import load_transcript


class PipelineConfig(BaseModel):
    artifacts_dir: Path = Path("artifacts")
    demo_mode: bool = False
    periodic_interval: float = Field(default=4.0, ge=0.5)
    novelty_threshold: float = Field(default=0.12, ge=0, le=1)
    max_frames: int = Field(default=30, ge=1, le=100)
    transcription_model: str = "gpt-4o-transcribe-diarize"
    analysis_model: str = "gpt-5.6"
    transcript_path: Path | None = None
    ocr_mode: Literal["off", "auto", "tesseract"] = "off"


class VideoDocumentPipeline:
    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()

    def run(self, video_path: Path) -> PipelineManifest:
        video_path = video_path.resolve()
        if not video_path.is_file():
            raise FileNotFoundError(video_path)
        
        # Print model details for demo presentation
        print("Transcription model: gpt-4o-transcribe-diarize")
        print("Analysis model: gpt-5.6-sol")
        ocr_engine = resolve_ocr_engine(self.config.ocr_mode)
        print(f"OCR engine: {ocr_engine or 'tesseract'}")
        transcript_input = self.config.transcript_path.resolve() if self.config.transcript_path else None
        if transcript_input is not None and not transcript_input.is_file():
            raise FileNotFoundError(transcript_input)
        job_id = _content_hash(video_path, transcript_input)
        job_dir = self.config.artifacts_dir.resolve() / job_id
        frames_dir = job_dir / "frames"
        job_dir.mkdir(parents=True, exist_ok=True)
        source_video = job_dir / f"source{video_path.suffix.lower() or '.mp4'}"
        if source_video != video_path:
            shutil.copy2(video_path, source_video)

        metadata = probe_video(source_video)
        agent = self._agent()
        transcript_path: Path | None = None
        if transcript_input is not None:
            transcript_path = job_dir / f"transcript{transcript_input.suffix.casefold()}"
            if transcript_path != transcript_input:
                shutil.copy2(transcript_input, transcript_path)
            transcript = load_transcript(transcript_path)
            transcript_source = "sidecar"
        elif metadata.has_audio:
            audio_path = extract_audio(source_video, job_dir / "audio.wav")
            transcript = agent.transcribe(audio_path)
            transcript_source = "demo" if self.config.demo_mode else "openai"
        elif self.config.demo_mode:
            transcript = agent.transcribe(job_dir / "audio.wav")
            transcript_source = "demo"
        else:
            transcript = []
            transcript_source = "none"

        frames = select_frames(
            source_video,
            frames_dir,
            metadata,
            transcript,
            periodic_interval=self.config.periodic_interval,
            novelty_threshold=self.config.novelty_threshold,
            max_frames=self.config.max_frames,
        )
        ocr_engine = resolve_ocr_engine(self.config.ocr_mode)
        if ocr_engine is not None:
            ocr = analyze_frames(frames, engine=ocr_engine)
            ocr_path = write_ocr_artifact(ocr, job_dir / "ocr.json")
        else:
            ocr = []
            ocr_path = None
        document = agent.create_document(frames, transcript)
        document = corroborate_document(document, ocr)
        print("Writing manifest and document artifacts")
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
            transcript_source=transcript_source,
            transcript_path=transcript_path,
            ocr=ocr,
            ocr_engine=ocr_engine,
            ocr_path=ocr_path,
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


def _content_hash(path: Path, transcript_path: Path | None = None) -> str:
    digest = hashlib.sha256()
    for input_path in (path, transcript_path):
        if input_path is None:
            continue
        with input_path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()[:12]
