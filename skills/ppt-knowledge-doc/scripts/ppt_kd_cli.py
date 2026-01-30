#!/usr/bin/env python3
"""ppt_kd_cli.py

Local CLI pipeline:
- Extract slide text + speaker notes
- Extract embedded images
- OCR images (if tesseract available)
- Generate knowledge.json + knowledge.md

Usage:
  python ppt_kd_cli.py deck.pptx --out /tmp/out
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from ppt_extract import extract_pptx
from render_md import render_markdown


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx", help="Path to .pptx file")
    ap.add_argument("--out", required=True, help="Output directory")
    args = ap.parse_args()

    pptx_path = Path(args.pptx).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    job_dir = out_dir
    data: Dict[str, Any] = extract_pptx(pptx_path=pptx_path, out_dir=job_dir)

    (job_dir / "knowledge.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    md = render_markdown(data)
    (job_dir / "knowledge.md").write_text(md, encoding="utf-8")

    print(f"Wrote: {job_dir / 'knowledge.json'}")
    print(f"Wrote: {job_dir / 'knowledge.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
