"""Command-line entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import PipelineConfig, VideoDocumentPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Turn a meeting video into timestamped documentation.")
    parser.add_argument("video", type=Path)
    parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--demo", action="store_true", help="Use deterministic local analysis.")
    parser.add_argument("--max-frames", type=int, default=30)
    parser.add_argument("--frame-interval", type=float, default=4.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = PipelineConfig(
        artifacts_dir=args.artifacts_dir,
        demo_mode=args.demo,
        max_frames=args.max_frames,
        periodic_interval=args.frame_interval,
    )
    manifest = VideoDocumentPipeline(config).run(args.video)
    print(f"Markdown: {manifest.markdown_path}")
    print(f"HTML: {manifest.html_path}")
    print(f"Evidence moments: {len(manifest.document.moments)}")


if __name__ == "__main__":
    main()

