"""Render generated documents as Markdown and portable HTML."""

from __future__ import annotations

import html
from pathlib import Path

from .media import format_timestamp
from .models import GeneratedDocument


def render_markdown(document: GeneratedDocument, video_path: Path, output_path: Path) -> Path:
    lines = [f"# {document.title}", "", document.overview, ""]
    for index, moment in enumerate(document.moments, start=1):
        timestamp = format_timestamp(moment.timestamp)
        image_ref = Path("frames") / moment.frame_path.name
        lines.extend(
            [
                f"## {index}. {moment.title}",
                "",
                f"**Type:** {moment.kind}  ",
                f"**Source:** [{timestamp}]({video_path.name}#t={moment.timestamp:.3f})  ",
                f"**Confidence:** {moment.confidence:.0%}",
                "",
                moment.summary,
                "",
                f"![Evidence at {timestamp}]({image_ref.as_posix()})",
                "",
            ]
        )
        if moment.commands:
            lines.extend(["### Commands", "", "```sh", *moment.commands, "```", ""])
        if moment.visible_text:
            lines.extend(["### Visible text", "", "```text", moment.visible_text, "```", ""])
        if moment.transcript_quote:
            lines.extend(
                [
                    "### Transcript evidence",
                    "",
                    f"> {moment.transcript_quote}",
                    "",
                    f"Span: {format_timestamp(moment.transcript_start)}–{format_timestamp(moment.transcript_end)}",
                    "",
                ]
            )
    if document.limitations:
        lines.extend(["## Limitations", ""])
        lines.extend(f"- {item}" for item in document.limitations)
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def render_html(document: GeneratedDocument, video_path: Path, output_path: Path) -> Path:
    sections: list[str] = []
    for index, moment in enumerate(document.moments, start=1):
        timestamp = format_timestamp(moment.timestamp)
        commands = "".join(f"<code>{html.escape(command)}</code>" for command in moment.commands)
        sections.append(
            f"""<article>
<h2>{index}. {html.escape(moment.title)}</h2>
<p><span>{html.escape(moment.kind)}</span> · <a href="{html.escape(video_path.name)}#t={moment.timestamp:.3f}">{timestamp}</a> · confidence {moment.confidence:.0%}</p>
<p>{html.escape(moment.summary)}</p>
<img src="frames/{html.escape(moment.frame_path.name)}" alt="Evidence at {timestamp}">
{f'<h3>Commands</h3><pre>{commands}</pre>' if commands else ''}
{f'<h3>Visible text</h3><pre>{html.escape(moment.visible_text)}</pre>' if moment.visible_text else ''}
{f'<h3>Transcript evidence</h3><blockquote>{html.escape(moment.transcript_quote)}</blockquote>' if moment.transcript_quote else ''}
</article>"""
        )
    limitations = "".join(f"<li>{html.escape(item)}</li>" for item in document.limitations)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(document.title)}</title></head>
<body><main><h1>{html.escape(document.title)}</h1><p>{html.escape(document.overview)}</p>
<video controls preload="metadata" width="900" src="{html.escape(video_path.name)}"></video>
{''.join(sections)}
{f'<h2>Limitations</h2><ul>{limitations}</ul>' if limitations else ''}
</main></body></html>"""
    output_path.write_text(page, encoding="utf-8")
    return output_path

