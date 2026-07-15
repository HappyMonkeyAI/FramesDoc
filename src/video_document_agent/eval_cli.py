"""Evaluate a generated manifest against labelled moments."""

from __future__ import annotations

import argparse
from pathlib import Path

from .evaluation import evaluate_manifest, load_fixture, load_manifest, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate an evidence-backed video document.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    manifest = load_manifest(args.manifest)
    fixture = load_fixture(args.fixture)
    output = args.output or args.manifest.parent / "evaluation.json"
    report = evaluate_manifest(manifest, fixture)
    write_report(report, output)
    print(f"Report: {output.resolve()}")
    print(f"Useful moment recall: {report.useful_moment_recall:.0%}")
    print(f"Redundant frame rate: {report.redundant_frame_rate:.0%}")
    print(f"Evidence grounding rate: {report.evidence_grounding_rate:.0%}")
    if report.command_ocr_agreement is not None:
        print(f"Command/OCR agreement: {report.command_ocr_agreement:.0%}")


if __name__ == "__main__":
    main()
