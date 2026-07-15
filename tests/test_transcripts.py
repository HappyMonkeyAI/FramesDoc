import json
from pathlib import Path

import pytest

from video_document_agent.transcripts import load_transcript


def test_loads_srt_speakers_and_multiline_text(tmp_path: Path) -> None:
    transcript = tmp_path / "meeting.srt"
    transcript.write_text(
        """1
00:00:01,250 --> 00:00:03,500
Alice: Run uv sync
before starting.

2
00:00:04,000 --> 00:00:05,000
Keep the artifacts.
""",
        encoding="utf-8",
    )

    segments = load_transcript(transcript)

    assert segments[0].start == 1.25
    assert segments[0].speaker == "Alice"
    assert segments[0].text == "Run uv sync before starting."
    assert segments[1].speaker == "UNKNOWN"


def test_loads_webvtt_voice_tags(tmp_path: Path) -> None:
    transcript = tmp_path / "meeting.vtt"
    transcript.write_text(
        """WEBVTT

00:01.000 --> 00:03.000 align:start
<v Bob>Click <b>Deploy</b> now.
""",
        encoding="utf-8",
    )

    segment = load_transcript(transcript)[0]

    assert segment.speaker == "Bob"
    assert segment.text == "Click Deploy now."


def test_loads_json_object_and_rejects_invalid_span(tmp_path: Path) -> None:
    transcript = tmp_path / "meeting.json"
    transcript.write_text(
        json.dumps({"segments": [{"start": "00:02.5", "end": 4, "text": "A decision"}]}),
        encoding="utf-8",
    )
    assert load_transcript(transcript)[0].start == 2.5

    transcript.write_text(
        json.dumps([{"start": 5, "end": 4, "text": "invalid"}]), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="end must be"):
        load_transcript(transcript)
