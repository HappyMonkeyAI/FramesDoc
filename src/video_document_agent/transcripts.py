"""Parse timestamped sidecar transcripts without external services."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from .models import TranscriptSegment


_VOICE_TAG = re.compile(r"^<v(?:\.[^ ]+)?\s+([^>]+)>(.*)$", re.DOTALL | re.IGNORECASE)
_SPEAKER_PREFIX = re.compile(r"^([A-Za-z][\w .-]{0,30}):\s+(.+)$", re.DOTALL)
_HTML_TAG = re.compile(r"<[^>]+>")


def load_transcript(path: Path) -> list[TranscriptSegment]:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    suffix = path.suffix.casefold()
    if suffix == ".json":
        segments = _parse_json(path.read_text(encoding="utf-8-sig"))
    elif suffix in {".srt", ".vtt"}:
        segments = _parse_cues(path.read_text(encoding="utf-8-sig"))
    else:
        raise ValueError("transcript must use .srt, .vtt, or .json")
    if not segments:
        raise ValueError(f"transcript contains no timestamped segments: {path}")
    return sorted(segments, key=lambda segment: (segment.start, segment.end))


def _parse_json(content: str) -> list[TranscriptSegment]:
    payload = json.loads(content)
    rows: Any = payload.get("segments") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("JSON transcript must be a list or contain a 'segments' list")
    return [
        TranscriptSegment(
            start=_seconds(row["start"]),
            end=_seconds(row["end"]),
            speaker=str(row.get("speaker") or "UNKNOWN"),
            text=str(row["text"]).strip(),
        )
        for row in rows
        if isinstance(row, dict)
    ]


def _parse_cues(content: str) -> list[TranscriptSegment]:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    segments: list[TranscriptSegment] = []
    for block in re.split(r"\n\s*\n", normalized):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing_index = next((index for index, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        start_token, end_part = lines[timing_index].split("-->", 1)
        end_token = end_part.strip().split()[0]
        raw_text = " ".join(lines[timing_index + 1 :]).strip()
        if not raw_text:
            continue
        speaker, text = _speaker_and_text(raw_text)
        segments.append(
            TranscriptSegment(
                start=_seconds(start_token.strip()),
                end=_seconds(end_token),
                speaker=speaker,
                text=text,
            )
        )
    return segments


def _seconds(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    parts = str(value).strip().replace(",", ".").split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours, minutes, seconds = "0", *parts
    else:
        return float(parts[0])
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _speaker_and_text(raw_text: str) -> tuple[str, str]:
    voice_match = _VOICE_TAG.match(raw_text)
    if voice_match:
        speaker = html.unescape(voice_match.group(1)).strip()
        text = voice_match.group(2)
    else:
        prefix_match = _SPEAKER_PREFIX.match(raw_text)
        speaker = prefix_match.group(1).strip() if prefix_match else "UNKNOWN"
        text = prefix_match.group(2) if prefix_match else raw_text
    clean_text = html.unescape(_HTML_TAG.sub("", text)).strip()
    return speaker or "UNKNOWN", clean_text
