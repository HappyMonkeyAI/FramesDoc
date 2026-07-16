#!/usr/bin/env python3
"""Helper script to transcribe video audio to a VTT file using OpenAI Whisper."""

import os
import sys
import subprocess
from pathlib import Path

# Trigger .env loading via package import
try:
    import video_document_agent
except ImportError:
    pass

from openai import OpenAI


def main():
    if len(sys.argv) < 3:
        print("Usage: uv run python scripts/transcribe_to_vtt.py <input_video> <output_vtt>")
        sys.exit(1)

    video_path = Path(sys.argv[1])
    output_vtt = Path(sys.argv[2])

    if not video_path.is_file():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)

    # Ensure api key is set
    api_key = os.getenv("OPENAI_API_KEY")
    # If the user has a real key, it should not be 'lm-studio' (since LM Studio does not run Whisper)
    if not api_key or api_key == "lm-studio":
        # Prompt user or look in environment
        real_key = os.getenv("REAL_OPENAI_API_KEY")
        if real_key:
            api_key = real_key
        else:
            print("Error: A real OPENAI_API_KEY is required to use the Whisper API.")
            print("Please set it in your environment or prefix the command:")
            print("  OPENAI_API_KEY=sk-... uv run python scripts/transcribe_to_vtt.py ...")
            sys.exit(1)

    # Create client pointing to standard OpenAI (ignoring local base_url if any)
    client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")

    # Extract audio to temp file
    temp_audio = video_path.parent / f"{video_path.stem}_temp_audio.mp3"
    print(f"Extracting audio from {video_path}...")
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-vn",
                "-ar",
                "16000",
                "-ac",
                "1",
                str(temp_audio),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Error extracting audio: {e}")
        if temp_audio.is_file():
            temp_audio.unlink()
        sys.exit(1)

    print("Transcribing via OpenAI Whisper API...")
    try:
        with temp_audio.open("rb") as audio_file:
            vtt_content = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="vtt",
            )
        output_vtt.write_text(vtt_content, encoding="utf-8")
        print(f"Success! VTT file written to {output_vtt}")
    except Exception as e:
        print(f"Error during transcription: {e}")
    finally:
        if temp_audio.is_file():
            temp_audio.unlink()


if __name__ == "__main__":
    main()
