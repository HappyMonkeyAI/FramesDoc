"""Local media probing, audio extraction, and hybrid frame selection."""

from __future__ import annotations

import json
import math
import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from .models import FrameCandidate, TranscriptSegment, VideoMetadata


DOCUMENTATION_CUES = re.compile(
    r"\b(run|command|click|select|open|configure|install|make sure|warning|"
    r"next|then|step|notice|important|decision|deploy|setup)\b",
    re.IGNORECASE,
)


class MediaCommandError(RuntimeError):
    """Raised when ffmpeg or ffprobe cannot process the input."""


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown media error"
        raise MediaCommandError(detail)
    return result


def probe_video(video_path: Path) -> VideoMetadata:
    result = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,width,height,avg_frame_rate",
            "-of",
            "json",
            str(video_path),
        ]
    )
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    video_stream = next((item for item in streams if item.get("codec_type") == "video"), {})
    rate = video_stream.get("avg_frame_rate", "0/1")
    numerator, denominator = (float(value) for value in rate.split("/", maxsplit=1))
    fps = numerator / denominator if denominator else 0.0
    return VideoMetadata(
        duration_seconds=float(payload.get("format", {}).get("duration", 0)),
        width=int(video_stream.get("width", 0)),
        height=int(video_stream.get("height", 0)),
        fps=fps,
        has_audio=any(item.get("codec_type") == "audio" for item in streams),
    )


def extract_audio(video_path: Path, audio_path: Path) -> Path:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio_path),
        ]
    )
    return audio_path


def detect_scene_timestamps(video_path: Path) -> list[float]:
    """Return scene starts and midpoints; import lazily to keep basic tests light."""

    from scenedetect import AdaptiveDetector, detect

    scenes = detect(str(video_path), AdaptiveDetector(), show_progress=False)
    timestamps: list[float] = []
    for start, end in scenes:
        start_seconds = start.get_seconds()
        end_seconds = end.get_seconds()
        timestamps.extend([start_seconds, (start_seconds + end_seconds) / 2])
    return timestamps


def periodic_timestamps(duration: float, interval: float) -> list[float]:
    if duration <= 0:
        return []
    interval = max(interval, 0.5)
    values = list(np.arange(0, duration, interval, dtype=float))
    final = max(0.0, duration - 0.1)
    values.append(final)
    return sorted(set(round(value, 3) for value in values))


def transcript_cue_timestamps(segments: Iterable[TranscriptSegment]) -> list[float]:
    return [segment.start for segment in segments if DOCUMENTATION_CUES.search(segment.text)]


@dataclass(frozen=True)
class TimestampSeed:
    timestamp: float
    sources: tuple[str, ...]


def merge_timestamp_seeds(
    periodic: Iterable[float],
    scenes: Iterable[float],
    cues: Iterable[float],
    *,
    tolerance: float = 0.75,
) -> list[TimestampSeed]:
    tagged = [*((value, "periodic") for value in periodic)]
    tagged.extend((value, "scene") for value in scenes)
    tagged.extend((value, "transcript_cue") for value in cues)
    merged: list[tuple[float, set[str]]] = []
    for timestamp, source in sorted(tagged):
        timestamp = max(0.0, float(timestamp))
        if merged and abs(timestamp - merged[-1][0]) <= tolerance:
            previous_timestamp, sources = merged[-1]
            sources.add(source)
            if source == "transcript_cue":
                merged[-1] = (timestamp, sources)
            else:
                merged[-1] = (previous_timestamp, sources)
        else:
            merged.append((timestamp, {source}))
    return [TimestampSeed(timestamp=value, sources=tuple(sorted(sources))) for value, sources in merged]


def extract_frame(video_path: Path, timestamp: float, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output_path),
        ]
    )
    return output_path


def difference_hash(image_path: Path) -> int:
    with Image.open(image_path) as image:
        pixels = np.asarray(image.convert("L").resize((9, 8), Image.Resampling.LANCZOS))
    bits = pixels[:, 1:] > pixels[:, :-1]
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bit)
    return value


def hash_novelty(current_hash: int, previous_hash: int | None) -> float:
    if previous_hash is None:
        return 1.0
    return (current_hash ^ previous_hash).bit_count() / 64


def select_frames(
    video_path: Path,
    output_dir: Path,
    metadata: VideoMetadata,
    transcript: list[TranscriptSegment],
    *,
    periodic_interval: float = 4.0,
    novelty_threshold: float = 0.12,
    max_frames: int = 30,
) -> list[FrameCandidate]:
    periodic = periodic_timestamps(metadata.duration_seconds, periodic_interval)
    scenes = detect_scene_timestamps(video_path)
    cues = transcript_cue_timestamps(transcript)
    seeds = merge_timestamp_seeds(periodic, scenes, cues)

    candidates: list[FrameCandidate] = []
    previous_hash: int | None = None
    for index, seed in enumerate(seeds):
        if seed.timestamp >= metadata.duration_seconds and metadata.duration_seconds > 0:
            continue
        frame_path = output_dir / f"frame-{index:04d}-{int(seed.timestamp * 1000):010d}.jpg"
        extract_frame(video_path, seed.timestamp, frame_path)
        current_hash = difference_hash(frame_path)
        novelty = hash_novelty(current_hash, previous_hash)
        keep = not candidates or novelty >= novelty_threshold or "transcript_cue" in seed.sources
        if keep:
            candidates.append(
                FrameCandidate(
                    timestamp=seed.timestamp,
                    frame_path=frame_path,
                    sources=list(seed.sources),
                    novelty_score=novelty,
                )
            )
            previous_hash = current_hash
        else:
            frame_path.unlink(missing_ok=True)

    if len(candidates) <= max_frames:
        return candidates

    def priority(frame: FrameCandidate) -> tuple[int, float]:
        source_score = 3 if "transcript_cue" in frame.sources else 2 if "scene" in frame.sources else 1
        return source_score, frame.novelty_score

    selected = sorted(candidates, key=priority, reverse=True)[:max_frames]
    selected_paths = {item.frame_path for item in selected}
    for frame in candidates:
        if frame.frame_path not in selected_paths:
            frame.frame_path.unlink(missing_ok=True)
    return sorted(selected, key=lambda item: item.timestamp)


def format_timestamp(seconds: float) -> str:
    seconds = max(0, math.floor(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

