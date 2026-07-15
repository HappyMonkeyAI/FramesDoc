from pathlib import Path

from video_document_agent.models import FrameCandidate, ModelDocument, ModelMoment, TranscriptSegment
from video_document_agent.openai_analysis import (
    _reattach_evidence,
    closest_transcript_segment,
    grounded_quote,
    nearby_transcript,
)


def test_nearby_transcript_uses_time_window() -> None:
    transcript = [
        TranscriptSegment(start=0, end=2, text="first"),
        TranscriptSegment(start=40, end=42, text="second"),
    ]
    assert [item.text for item in nearby_transcript(1, transcript, radius=5)] == ["first"]


def test_closest_transcript_and_quote_are_grounded() -> None:
    transcript = [
        TranscriptSegment(start=0, end=2, text="first grounded sentence"),
        TranscriptSegment(start=8, end=10, text="second grounded sentence"),
    ]
    closest = closest_transcript_segment(9, transcript)
    assert closest is transcript[1]
    assert grounded_quote("invented quote", closest) == "second grounded sentence"
    assert grounded_quote("grounded sentence", closest) == "grounded sentence"

    boundary = closest_transcript_segment(
        2,
        [
            TranscriptSegment(start=0, end=2, text="ending"),
            TranscriptSegment(start=2, end=4, text="starting"),
        ],
    )
    assert boundary is not None
    assert boundary.text == "starting"


def test_model_output_cannot_override_local_evidence_path() -> None:
    frames = [
        FrameCandidate(
            timestamp=5,
            frame_path=Path("frames/real.jpg"),
            sources=["scene"],
            novelty_score=1,
        )
    ]
    transcript = [TranscriptSegment(start=4, end=6, speaker="A", text="Run the command.")]
    draft = ModelDocument(
        title="Runbook",
        overview="Overview",
        moments=[
            ModelMoment(
                frame_index=0,
                title="Run it",
                kind="command",
                summary="Start the app.",
                commands=["uv run app"],
                confidence=0.9,
            )
        ],
    )
    document = _reattach_evidence(draft, frames, transcript)
    assert document.moments[0].frame_path == Path("frames/real.jpg")
    assert document.moments[0].timestamp == 5
    assert document.moments[0].transcript_start == 4
