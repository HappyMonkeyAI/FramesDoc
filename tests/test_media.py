from pathlib import Path

from PIL import Image

from video_document_agent.media import (
    difference_hash,
    format_timestamp,
    hash_novelty,
    merge_timestamp_seeds,
    transcript_cue_timestamps,
)
from video_document_agent.models import TranscriptSegment


def test_format_timestamp() -> None:
    assert format_timestamp(0) == "00:00:00"
    assert format_timestamp(3661.9) == "01:01:01"


def test_transcript_cues_select_documentation_language() -> None:
    segments = [
        TranscriptSegment(start=1, end=2, text="We should run this command now."),
        TranscriptSegment(start=3, end=4, text="How was your weekend?"),
        TranscriptSegment(start=5, end=6, text="Make sure the token is configured."),
    ]
    assert transcript_cue_timestamps(segments) == [1, 5]


def test_timestamp_seed_merging_prefers_cue_timestamp() -> None:
    seeds = merge_timestamp_seeds([0, 4], [4.2], [4.4])
    assert len(seeds) == 2
    assert seeds[1].timestamp == 4.4
    assert set(seeds[1].sources) == {"periodic", "scene", "transcript_cue"}


def test_difference_hash_reports_visual_change(tmp_path: Path) -> None:
    black = tmp_path / "black.png"
    split = tmp_path / "split.png"
    Image.new("RGB", (32, 32), "black").save(black)
    image = Image.new("RGB", (32, 32), "black")
    for x in range(16, 32):
        for y in range(32):
            image.putpixel((x, y), (255, 255, 255))
    image.save(split)
    black_hash = difference_hash(black)
    split_hash = difference_hash(split)
    assert hash_novelty(black_hash, None) == 1.0
    assert hash_novelty(split_hash, black_hash) > 0

