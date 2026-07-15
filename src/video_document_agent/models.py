"""Typed contracts shared by extraction, analysis, rendering, and the UI."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    duration_seconds: float = Field(ge=0)
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    fps: float = Field(ge=0)
    has_audio: bool


class TranscriptSegment(BaseModel):
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    speaker: str = "UNKNOWN"
    text: str


class FrameCandidate(BaseModel):
    timestamp: float = Field(ge=0)
    frame_path: Path
    sources: list[Literal["periodic", "scene", "transcript_cue"]]
    novelty_score: float = Field(ge=0, le=1)


class EvidenceMoment(BaseModel):
    title: str
    kind: Literal["setup", "command", "warning", "decision", "workflow", "reference"]
    summary: str
    timestamp: float = Field(ge=0)
    frame_path: Path
    transcript_start: float = Field(ge=0)
    transcript_end: float = Field(ge=0)
    transcript_quote: str = ""
    visible_text: str = ""
    commands: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class GeneratedDocument(BaseModel):
    title: str
    overview: str
    moments: list[EvidenceMoment]
    limitations: list[str] = Field(default_factory=list)


class PipelineManifest(BaseModel):
    source_video: Path
    metadata: VideoMetadata
    transcript: list[TranscriptSegment]
    frames: list[FrameCandidate]
    document: GeneratedDocument
    markdown_path: Path
    html_path: Path
    demo_mode: bool


class ModelMoment(BaseModel):
    """Schema returned by the model before local evidence is reattached."""

    frame_index: int = Field(ge=0)
    title: str
    kind: Literal["setup", "command", "warning", "decision", "workflow", "reference"]
    summary: str
    transcript_quote: str = ""
    visible_text: str = ""
    commands: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ModelDocument(BaseModel):
    title: str
    overview: str
    moments: list[ModelMoment]
    limitations: list[str] = Field(default_factory=list)

