from __future__ import annotations

from typing import Any, Dict, List


def render_markdown(doc: Dict[str, Any]) -> str:
    src = doc.get("source_file", "")
    slide_count = doc.get("slide_count", 0)
    summary = doc.get("summary", {}) or {}

    out: List[str] = []
    out.append(f"# Knowledge Doc\n")
    out.append(f"**Source:** `{src}`  ")
    out.append(f"**Slides:** {slide_count}\n")

    exec_sum = summary.get("executive_summary", "")
    if exec_sum:
        out.append("## Executive summary\n")
        out.append(exec_sum + "\n")

    key_points = summary.get("key_points", []) or []
    if key_points:
        out.append("## Key points\n")
        for kp in key_points:
            out.append(f"- {kp}")
        out.append("")

    out.append("## Slide-by-slide\n")
    for s in doc.get("slides", []) or []:
        idx = s.get("index")
        out.append(f"### Slide {idx}\n")

        text = (s.get("text") or "").strip()
        if text:
            out.append("**Text**\n")
            out.append(text + "\n")

        notes = (s.get("notes") or "").strip()
        if notes:
            out.append("**Speaker notes**\n")
            out.append(notes + "\n")

        images = s.get("images", []) or []
        if images:
            out.append("**Images**\n")
            for im in images:
                if not isinstance(im, dict):
                    continue
                if im.get("file"):
                    out.append(f"- File: `{im['file']}`")
                ocr = (im.get("ocr_text") or "").strip()
                if ocr:
                    out.append("  - OCR:")
                    for line in ocr.splitlines():
                        if line.strip():
                            out.append(f"    - {line.strip()}")
            out.append("")

    return "\n".join(out).strip() + "\n"
