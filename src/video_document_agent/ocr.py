"""Optional deterministic OCR and command-text corroboration."""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from difflib import SequenceMatcher
from io import StringIO
from pathlib import Path
from typing import Literal

from .models import EvidenceMoment, FrameCandidate, GeneratedDocument, OcrObservation, OcrWord


class OcrUnavailableError(RuntimeError):
    """Raised when an explicitly requested OCR engine is unavailable."""


def tesseract_available() -> bool:
    return shutil.which("tesseract") is not None


def resolve_ocr_engine(mode: Literal["off", "auto", "tesseract"]) -> Literal["tesseract"] | None:
    if mode == "off":
        return None
    if tesseract_available():
        return "tesseract"
    if mode == "tesseract":
        raise OcrUnavailableError("Tesseract OCR was requested but is not available on PATH")
    return None


def analyze_frames(
    frames: list[FrameCandidate],
    *,
    engine: Literal["tesseract"],
) -> list[OcrObservation]:
    if engine != "tesseract":
        raise ValueError(f"unsupported OCR engine: {engine}")
    return [_run_tesseract(frame) for frame in frames]


def _run_tesseract(frame: FrameCandidate) -> OcrObservation:
    result = subprocess.run(
        ["tesseract", str(frame.frame_path), "stdout", "--psm", "6", "tsv"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown Tesseract error"
        raise RuntimeError(f"Tesseract failed for {frame.frame_path}: {detail}")
    text, confidence, words = _parse_tesseract_tsv(result.stdout)
    return OcrObservation(
        timestamp=frame.timestamp,
        frame_path=frame.frame_path,
        engine="tesseract",
        text=text,
        mean_confidence=confidence,
        words=words,
    )


def _parse_tesseract_tsv(content: str) -> tuple[str, float, list[OcrWord]]:
    lines: dict[tuple[str, str, str, str], list[str]] = {}
    words: list[OcrWord] = []
    for row in csv.DictReader(StringIO(content), delimiter="\t"):
        text = (row.get("text") or "").strip()
        try:
            raw_confidence = float(row.get("conf") or -1)
        except ValueError:
            continue
        if not text or raw_confidence < 0:
            continue
        confidence = max(0.0, min(1.0, raw_confidence / 100))
        word = OcrWord(
            text=text,
            confidence=confidence,
            left=int(row.get("left") or 0),
            top=int(row.get("top") or 0),
            width=int(row.get("width") or 0),
            height=int(row.get("height") or 0),
        )
        words.append(word)
        line_key = tuple(row.get(key) or "0" for key in ("page_num", "block_num", "par_num", "line_num"))
        lines.setdefault(line_key, []).append(text)
    rendered = "\n".join(" ".join(line_words) for line_words in lines.values())
    mean_confidence = sum(word.confidence for word in words) / len(words) if words else 0.0
    return rendered, mean_confidence, words


def normalized_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9._/=:~-]+", value.casefold()))


def command_agreement(commands: list[str], ocr_text: str) -> float | None:
    normalized_ocr = normalized_text(ocr_text)
    if not commands or not normalized_ocr:
        return None
    ocr_candidates = [normalized_ocr]
    ocr_candidates.extend(
        normalized_line for line in ocr_text.splitlines() if (normalized_line := normalized_text(line))
    )
    scores: list[float] = []
    for command in commands:
        normalized_command = normalized_text(command)
        if not normalized_command:
            continue
        if normalized_command in normalized_ocr:
            scores.append(1.0)
            continue
        scores.append(
            max(
                SequenceMatcher(None, normalized_command, candidate).ratio()
                for candidate in ocr_candidates
            )
        )
    return max(scores) if scores else None


def corroborate_document(
    document: GeneratedDocument,
    observations: list[OcrObservation],
) -> GeneratedDocument:
    by_frame = {observation.frame_path.resolve(): observation for observation in observations}
    moments: list[EvidenceMoment] = []
    for moment in document.moments:
        observation = by_frame.get(moment.frame_path.resolve())
        if observation is None:
            moments.append(moment)
            continue
        moments.append(
            moment.model_copy(
                update={
                    "ocr_text": observation.text,
                    "ocr_confidence": observation.mean_confidence,
                    "command_ocr_agreement": command_agreement(moment.commands, observation.text),
                }
            )
        )
    return document.model_copy(update={"moments": moments})


def write_ocr_artifact(observations: list[OcrObservation], path: Path) -> Path:
    path.write_text(
        json.dumps([item.model_dump(mode="json") for item in observations], indent=2),
        encoding="utf-8",
    )
    return path
