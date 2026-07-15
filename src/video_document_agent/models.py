"""Typed contracts shared by extraction, analysis, rendering, and the UI."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


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

    @model_validator(mode="after")
    def validate_span(self) -> "TranscriptSegment":
        if self.end < self.start:
            raise ValueError("transcript segment end must be at or after start")
        if not self.text.strip():
            raise ValueError("transcript segment text must not be empty")
        return self


class FrameCandidate(BaseModel):
    timestamp: float = Field(ge=0)
    frame_path: Path
    sources: list[Literal["periodic", "scene", "transcript_cue"]]
    novelty_score: float = Field(ge=0, le=1)


class OcrWord(BaseModel):
    text: str
    confidence: float = Field(ge=0, le=1)
    left: int = Field(ge=0)
    top: int = Field(ge=0)
    width: int = Field(ge=0)
    height: int = Field(ge=0)


class OcrObservation(BaseModel):
    timestamp: float = Field(ge=0)
    frame_path: Path
    engine: Literal["tesseract"]
    text: str = ""
    mean_confidence: float = Field(ge=0, le=1)
    words: list[OcrWord] = Field(default_factory=list)


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
    ocr_text: str = ""
    ocr_confidence: float | None = Field(default=None, ge=0, le=1)
    command_ocr_agreement: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def validate_transcript_span(self) -> "EvidenceMoment":
        if self.transcript_end < self.transcript_start:
            raise ValueError("evidence transcript end must be at or after start")
        return self


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
    transcript_source: Literal["openai", "sidecar", "demo", "none"]
    transcript_path: Path | None = None
    ocr: list[OcrObservation] = Field(default_factory=list)
    ocr_engine: Literal["tesseract"] | None = None
    ocr_path: Path | None = None


class ReviewDecision(BaseModel):
    """Human edits while the source video timestamp and frame remain immutable."""

    original_index: int = Field(ge=0)
    accepted: bool = True
    title: str
    kind: Literal["setup", "command", "warning", "decision", "workflow", "reference"]
    summary: str
    transcript_start: float | None = Field(default=None, ge=0)
    transcript_end: float | None = Field(default=None, ge=0)
    transcript_quote: str = ""
    visible_text: str = ""
    commands: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_transcript_span(self) -> "ReviewDecision":
        if (
            self.transcript_start is not None
            and self.transcript_end is not None
            and self.transcript_end < self.transcript_start
        ):
            raise ValueError("review transcript end must be at or after start")
        return self


class ReviewRecord(BaseModel):
    title: str
    overview: str
    decisions: list[ReviewDecision]


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


class ExpectedMoment(BaseModel):
    timestamp: float = Field(ge=0)
    tolerance: float = Field(default=2.0, ge=0)
    kind: Literal["setup", "command", "warning", "decision", "workflow", "reference"] | None = None
    label: str = ""


class EvaluationFixture(BaseModel):
    name: str
    expected_moments: list[ExpectedMoment]
    redundancy_threshold: float = Field(default=0.12, ge=0, le=1)


class EvaluationReport(BaseModel):
    fixture_name: str
    expected_moments: int
    matched_moments: int
    useful_moment_recall: float = Field(ge=0, le=1)
    redundant_frames: int
    evaluated_frame_pairs: int
    redundant_frame_rate: float = Field(ge=0, le=1)
    grounded_moments: int
    generated_moments: int
    evidence_grounding_rate: float = Field(ge=0, le=1)
    command_ocr_agreement: float | None = Field(default=None, ge=0, le=1)
    unmatched_labels: list[str] = Field(default_factory=list)
