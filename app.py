"""Streamlit review UI for the vertical spike."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st

from video_document_agent.media import format_timestamp
from video_document_agent.pipeline import PipelineConfig, VideoDocumentPipeline


st.set_page_config(page_title="Video Document Agent", page_icon="🎞️", layout="wide")
st.title("Video Document Agent")
st.caption("Turn visual meeting knowledge into evidence-backed runbooks.")

uploaded = st.file_uploader("Meeting recording", type=["mp4", "mov", "webm", "mkv"])
default_demo = not bool(os.getenv("OPENAI_API_KEY"))
demo_mode = st.toggle(
    "Deterministic demo mode",
    value=default_demo,
    help="Uses real frame extraction with synthetic transcript/document analysis; no API key required.",
)
max_frames = st.slider("Maximum evidence frames", min_value=3, max_value=50, value=20)
interval = st.slider("Periodic sampling interval (seconds)", 1.0, 10.0, 4.0, 0.5)

if uploaded and st.button("Generate documentation", type="primary"):
    suffix = Path(uploaded.name).suffix or ".mp4"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
        temp_file.write(uploaded.getbuffer())
        temp_path = Path(temp_file.name)
    try:
        with st.status("Processing video", expanded=True) as status:
            st.write("Probing media, transcribing, and selecting evidence frames…")
            manifest = VideoDocumentPipeline(
                PipelineConfig(
                    artifacts_dir=Path("artifacts"),
                    demo_mode=demo_mode,
                    max_frames=max_frames,
                    periodic_interval=interval,
                )
            ).run(temp_path)
            status.update(label="Documentation generated", state="complete")
        st.video(manifest.source_video.read_bytes())
        st.header(manifest.document.title)
        st.write(manifest.document.overview)
        for moment in manifest.document.moments:
            left, right = st.columns([2, 3])
            with left:
                st.image(str(moment.frame_path), caption=format_timestamp(moment.timestamp))
            with right:
                st.subheader(moment.title)
                st.write(f"{moment.kind} · {format_timestamp(moment.timestamp)} · {moment.confidence:.0%}")
                st.write(moment.summary)
                if moment.commands:
                    st.code("\n".join(moment.commands), language="bash")
                if moment.visible_text:
                    st.code(moment.visible_text, language="text")
                if moment.transcript_quote:
                    st.info(moment.transcript_quote)
        st.download_button(
            "Download Markdown",
            data=manifest.markdown_path.read_bytes(),
            file_name="video-runbook.md",
            mime="text/markdown",
        )
        st.download_button(
            "Download HTML",
            data=manifest.html_path.read_bytes(),
            file_name="video-runbook.html",
            mime="text/html",
        )
        if manifest.document.limitations:
            st.warning("\n".join(manifest.document.limitations))
    except Exception as exc:
        st.exception(exc)
    finally:
        temp_path.unlink(missing_ok=True)

