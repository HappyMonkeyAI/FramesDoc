"""Streamlit review UI for generation, human editing, and reviewed export."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st

from video_document_agent.media import format_timestamp
from video_document_agent.models import ReviewDecision, ReviewRecord
from video_document_agent.ocr import tesseract_available
from video_document_agent.pipeline import PipelineConfig, VideoDocumentPipeline
from video_document_agent.review import persist_review


KINDS = ["setup", "command", "warning", "decision", "workflow", "reference"]

st.set_page_config(page_title="Video Document Agent", page_icon="🎞️", layout="wide")
st.title("Video Document Agent")
st.caption("Turn visual meeting knowledge into evidence-backed, human-reviewed runbooks.")

uploaded = st.file_uploader("Meeting recording", type=["mp4", "mov", "webm", "mkv"])
transcript_upload = st.file_uploader(
    "Timestamped transcript (optional)",
    type=["srt", "vtt", "json"],
    help="A sidecar transcript skips API transcription and improves keyless evidence selection.",
)
default_demo = not bool(os.getenv("OPENAI_API_KEY"))
demo_mode = st.toggle(
    "Deterministic analysis mode",
    value=default_demo,
    help="Uses real video and any supplied transcript with deterministic document analysis; no API key required.",
)
max_frames = st.slider("Maximum evidence frames", min_value=3, max_value=50, value=20)
interval = st.slider("Periodic sampling interval (seconds)", 1.0, 10.0, 4.0, 0.5)
ocr_enabled = st.toggle(
    "Tesseract OCR corroboration",
    value=False,
    disabled=not tesseract_available(),
    help="Reads selected frames locally and keeps OCR separate from model-visible text.",
)

if uploaded and st.button("Generate documentation", type="primary"):
    temporary_paths: list[Path] = []
    try:
        suffix = Path(uploaded.name).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(uploaded.getbuffer())
            video_path = Path(temp_file.name)
            temporary_paths.append(video_path)

        transcript_path = None
        if transcript_upload is not None:
            transcript_suffix = Path(transcript_upload.name).suffix.casefold()
            with tempfile.NamedTemporaryFile(suffix=transcript_suffix, delete=False) as temp_file:
                temp_file.write(transcript_upload.getbuffer())
                transcript_path = Path(temp_file.name)
                temporary_paths.append(transcript_path)

        with st.status("Processing video", expanded=True) as status:
            st.write("Probing media, loading transcript, and selecting evidence frames…")
            manifest = VideoDocumentPipeline(
                PipelineConfig(
                    artifacts_dir=Path("artifacts"),
                    demo_mode=demo_mode,
                    max_frames=max_frames,
                    periodic_interval=interval,
                    transcript_path=transcript_path,
                    ocr_mode="tesseract" if ocr_enabled else "off",
                )
            ).run(video_path)
            status.update(label="Documentation generated", state="complete")
        st.session_state["manifest"] = manifest
        st.session_state.pop("reviewed_manifest", None)
    except Exception as exc:
        st.exception(exc)
    finally:
        for path in temporary_paths:
            path.unlink(missing_ok=True)

manifest = st.session_state.get("manifest")
if manifest is not None:
    job_key = manifest.source_video.parent.name
    st.video(manifest.source_video.read_bytes())
    st.caption(
        f"Transcript source: {manifest.transcript_source} · "
        f"{len(manifest.transcript)} segments · {len(manifest.frames)} candidate frames · "
        f"OCR: {manifest.ocr_engine or 'off'}"
    )

    st.header("Review generated moments")
    st.write("Accept, reject, or edit content below. Video timestamps and frame paths remain fixed; transcript-span edits are audited.")
    decisions: list[ReviewDecision] = []
    with st.form(f"review-{job_key}"):
        reviewed_title = st.text_input("Document title", value=manifest.document.title)
        reviewed_overview = st.text_area("Overview", value=manifest.document.overview)
        for index, moment in enumerate(manifest.document.moments):
            st.divider()
            left, right = st.columns([2, 3])
            with left:
                st.image(str(moment.frame_path), caption=format_timestamp(moment.timestamp))
                accepted = st.checkbox("Include this moment", value=True, key=f"accept-{job_key}-{index}")
                kind = st.selectbox(
                    "Type",
                    KINDS,
                    index=KINDS.index(moment.kind),
                    key=f"kind-{job_key}-{index}",
                )
            with right:
                title = st.text_input("Title", value=moment.title, key=f"title-{job_key}-{index}")
                summary = st.text_area(
                    "Summary", value=moment.summary, key=f"summary-{job_key}-{index}"
                )
                commands = st.text_area(
                    "Commands (one per line)",
                    value="\n".join(moment.commands),
                    key=f"commands-{job_key}-{index}",
                )
                visible_text = st.text_area(
                    "Visible text", value=moment.visible_text, key=f"visible-{job_key}-{index}"
                )
                observation = next(
                    (
                        item
                        for item in manifest.ocr
                        if item.frame_path.resolve() == moment.frame_path.resolve()
                    ),
                    None,
                )
                if observation and observation.text:
                    st.code(observation.text, language="text")
                    agreement = (
                        f" · command agreement {moment.command_ocr_agreement:.0%}"
                        if moment.command_ocr_agreement is not None
                        else ""
                    )
                    st.caption(
                        f"Tesseract mean word confidence {observation.mean_confidence:.0%}{agreement}"
                    )
                transcript_quote = st.text_area(
                    "Transcript quotation",
                    value=moment.transcript_quote,
                    key=f"quote-{job_key}-{index}",
                )
                span_left, span_right = st.columns(2)
                with span_left:
                    transcript_start = st.number_input(
                        "Transcript start (seconds)",
                        min_value=0.0,
                        value=float(moment.transcript_start),
                        step=0.1,
                        key=f"span-start-{job_key}-{index}",
                    )
                with span_right:
                    transcript_end = st.number_input(
                        "Transcript end (seconds)",
                        min_value=0.0,
                        value=float(moment.transcript_end),
                        step=0.1,
                        key=f"span-end-{job_key}-{index}",
                    )
                st.caption(
                    f"Immutable video evidence: {format_timestamp(moment.timestamp)}"
                )
            decisions.append(
                ReviewDecision(
                    original_index=index,
                    accepted=accepted,
                    title=title,
                    kind=kind,
                    summary=summary,
                    transcript_start=transcript_start,
                    transcript_end=transcript_end,
                    transcript_quote=transcript_quote,
                    visible_text=visible_text,
                    commands=commands.splitlines(),
                )
            )
        submitted = st.form_submit_button("Save reviewed document", type="primary")

    if submitted:
        review = ReviewRecord(
            title=reviewed_title,
            overview=reviewed_overview,
            decisions=decisions,
        )
        st.session_state["reviewed_manifest"] = persist_review(manifest, review)
        st.success(f"Saved {sum(decision.accepted for decision in decisions)} accepted moments.")

    export_manifest = st.session_state.get("reviewed_manifest", manifest)
    label = "reviewed" if export_manifest is not manifest else "original"
    st.subheader(f"Export {label} document")
    st.download_button(
        "Download Markdown",
        data=export_manifest.markdown_path.read_bytes(),
        file_name="video-runbook.md",
        mime="text/markdown",
    )
    st.download_button(
        "Download HTML",
        data=export_manifest.html_path.read_bytes(),
        file_name="video-runbook.html",
        mime="text/html",
    )
    if export_manifest.document.limitations:
        st.warning("\n".join(export_manifest.document.limitations))
