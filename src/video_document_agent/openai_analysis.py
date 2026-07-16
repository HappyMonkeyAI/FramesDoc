"""OpenAI-backed transcription and evidence-grounded document synthesis."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

from openai import OpenAI

from .models import (
    EvidenceMoment,
    FrameCandidate,
    GeneratedDocument,
    ModelDocument,
    TranscriptSegment,
)


SYSTEM_PROMPT = """You create durable internal documentation from meeting evidence.
Do not produce a generic meeting summary. Select only moments that support setup steps,
commands, warnings, decisions, workflows, or references. Every moment must point to one
provided frame index. Copy commands and visible text conservatively; never invent text
that is not visible or supported by the transcript. Return limitations when evidence is
ambiguous. Prefer a small number of high-value moments over exhaustive narration.

Note: The input images are provided in the exact order of their frame indices (the first image corresponds to FRAME 0, the second image to FRAME 1, the third image to FRAME 2, etc.). Use the visual evidence in each image to correctly identify which FRAME contains the setup steps, commands, or warnings."""


def _data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def nearby_transcript(
    timestamp: float,
    transcript: list[TranscriptSegment],
    *,
    radius: float = 20.0,
) -> list[TranscriptSegment]:
    return [
        segment
        for segment in transcript
        if segment.end >= timestamp - radius and segment.start <= timestamp + radius
    ]


def closest_transcript_segment(
    timestamp: float,
    transcript: list[TranscriptSegment],
) -> TranscriptSegment | None:
    if not transcript:
        return None

    def distance(segment: TranscriptSegment) -> float:
        if segment.start <= timestamp <= segment.end:
            return 0.0
        return min(abs(timestamp - segment.start), abs(timestamp - segment.end))

    return min(transcript, key=lambda segment: (distance(segment), -segment.start))


def grounded_quote(candidate: str, segment: TranscriptSegment | None) -> str:
    if segment is None:
        return ""
    candidate = candidate.strip()
    if candidate and candidate.casefold() in segment.text.casefold():
        return candidate
    return segment.text


class OpenAIDocumentAgent:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        transcription_model: str = "gpt-4o-transcribe-diarize",
        analysis_model: str = "gpt-5.6",
    ) -> None:
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.transcription_model = transcription_model
        self.analysis_model = analysis_model

    def transcribe(self, audio_path: Path) -> list[TranscriptSegment]:
        with audio_path.open("rb") as audio_file:
            result = self.client.audio.transcriptions.create(
                model=self.transcription_model,
                file=audio_file,
                response_format="diarized_json",
                chunking_strategy="auto",
            )
        return [
            TranscriptSegment(
                start=float(segment.start),
                end=float(segment.end),
                speaker=str(segment.speaker),
                text=str(segment.text).strip(),
            )
            for segment in result.segments
        ]

    def create_document(
        self,
        frames: list[FrameCandidate],
        transcript: list[TranscriptSegment],
    ) -> GeneratedDocument:
        # 1. Content for Responses API (new OpenAI responses endpoint) - Interleaved
        content_responses: list[dict[str, str]] = [
            {
                "type": "input_text",
                "text": "Analyze the numbered evidence frames and their nearby transcript. Use frame_index values exactly as provided.\n\n",
            }
        ]
        for index, frame in enumerate(frames):
            content_responses.append(
                {
                    "type": "input_text",
                    "text": _frame_context(index, frame, nearby_transcript(frame.timestamp, transcript)),
                }
            )
            content_responses.append(
                {
                    "type": "input_image",
                    "image_url": _data_url(frame.frame_path),
                    "detail": "original",
                }
            )

        # 2. Content for standard Chat Completions API (used by local models / LM Studio) - Interleaved
        content_chat: list[dict[str, any]] = [
            {
                "type": "text",
                "text": "Analyze the numbered evidence frames and their nearby transcript. Use frame_index values exactly as provided.\n\n",
            }
        ]
        for index, frame in enumerate(frames):
            content_chat.append(
                {
                    "type": "text",
                    "text": _frame_context(index, frame, nearby_transcript(frame.timestamp, transcript)),
                }
            )
            content_chat.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": _data_url(frame.frame_path),
                        "detail": "high",
                    },
                }
            )

        # Determine if we should attempt /responses or default to chat/completions
        is_local = "api.openai.com" not in str(self.client.base_url)
        parsed = None

        if not is_local:
            try:
                response = self.client.responses.parse(
                    model=self.analysis_model,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": content_responses},
                    ],
                    text_format=ModelDocument,
                )
                parsed = response.output_parsed
            except Exception:
                # Fall back if the responses endpoint is unsupported
                pass

        if parsed is None:
            # Fall back to standard Chat Completions with JSON Schema response format
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content_chat},
            ]
            schema = ModelDocument.model_json_schema()
            response = self.client.chat.completions.create(
                model=self.analysis_model,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "ModelDocument",
                        "schema": schema,
                    }
                },
            )
            content = response.choices[0].message.content
            if content:
                parsed = ModelDocument.model_validate_json(content)

        if parsed is None:
            raise RuntimeError("LLM client returned no structured document")
        return _reattach_evidence(parsed, frames, transcript)


def _frame_context(
    index: int,
    frame: FrameCandidate,
    transcript: list[TranscriptSegment],
) -> str:
    lines = [
        f"FRAME {index} (Note: This corresponds to Vision Image #{index + 1} below)",
        f"timestamp_seconds: {frame.timestamp:.3f}",
        f"candidate_sources: {', '.join(frame.sources)}",
        "nearby_transcript:",
    ]
    lines.extend(
        f"- [{segment.start:.2f}-{segment.end:.2f}] {segment.speaker}: {segment.text}"
        for segment in transcript
    )
    return "\n".join(lines)


def _reattach_evidence(
    draft: ModelDocument,
    frames: list[FrameCandidate],
    transcript: list[TranscriptSegment],
) -> GeneratedDocument:
    moments: list[EvidenceMoment] = []
    for item in draft.moments:
        if item.frame_index >= len(frames):
            continue
        frame = frames[item.frame_index]
        closest = closest_transcript_segment(frame.timestamp, transcript)
        transcript_start = closest.start if closest else frame.timestamp
        transcript_end = closest.end if closest else frame.timestamp
        moments.append(
            EvidenceMoment(
                title=item.title,
                kind=item.kind,
                summary=item.summary,
                timestamp=frame.timestamp,
                frame_path=frame.frame_path,
                transcript_start=transcript_start,
                transcript_end=transcript_end,
                transcript_quote=grounded_quote(item.transcript_quote, closest),
                visible_text=item.visible_text,
                commands=item.commands,
                confidence=item.confidence,
            )
        )
    return GeneratedDocument(
        title=draft.title,
        overview=draft.overview,
        moments=sorted(moments, key=lambda moment: moment.timestamp),
        limitations=draft.limitations,
    )


class DemoDocumentAgent:
    """Deterministic adapter for local testing without credentials."""

    def transcribe(self, audio_path: Path) -> list[TranscriptSegment]:
        del audio_path
        return [
            TranscriptSegment(
                start=0.0,
                end=4.0,
                speaker="SPEAKER_00",
                text="Open the terminal and make sure the project directory is selected.",
            ),
            TranscriptSegment(
                start=4.0,
                end=9.0,
                speaker="SPEAKER_00",
                text="Run the command shown on screen to start the service.",
            ),
            TranscriptSegment(
                start=9.0,
                end=14.0,
                speaker="SPEAKER_01",
                text="The important warning is to keep the evidence artifacts for review.",
            ),
        ]

    def create_document(
        self,
        frames: list[FrameCandidate],
        transcript: list[TranscriptSegment],
    ) -> GeneratedDocument:
        if not frames:
            return GeneratedDocument(
                title="Demo runbook",
                overview="No usable visual evidence was extracted.",
                moments=[],
                limitations=["The demo input did not yield any frames."],
            )
        moments: list[EvidenceMoment] = []
        for index, frame in enumerate(frames[:3]):
            closest = closest_transcript_segment(frame.timestamp, transcript)
            moments.append(
                EvidenceMoment(
                    title=("Prepare the workspace", "Start the service", "Preserve evidence")[index],
                    kind=("setup", "command", "warning")[index],
                    summary=(
                        "Open a terminal in the project workspace.",
                        "Run the demonstrated service command.",
                        "Keep generated frames and transcript spans for review.",
                    )[index],
                    timestamp=frame.timestamp,
                    frame_path=frame.frame_path,
                    transcript_start=closest.start if closest else frame.timestamp,
                    transcript_end=closest.end if closest else frame.timestamp,
                    transcript_quote=closest.text if closest else "",
                    visible_text="",
                    commands=["uv run video-doc input.mp4 --demo"] if index == 1 else [],
                    confidence=0.5,
                )
            )
        return GeneratedDocument(
            title="Evidence-backed demo runbook",
            overview="A deterministic demonstration of the video-to-document artifact contract.",
            moments=moments,
            limitations=[
                "Deterministic analysis uses template document content; OCR, when enabled, is attached separately."
            ],
        )
