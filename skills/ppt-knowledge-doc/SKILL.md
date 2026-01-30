---
name: ppt-knowledge-doc
description: Turn PowerPoint files (.pptx/.ppt) into a structured knowledge document (Markdown + JSON). Use when you need to extract slide text, speaker notes, and images; OCR text inside screenshots/diagrams; and generate an executive summary, key points, glossary, and slide-by-slide notes.
---

# ppt-knowledge-doc

Convert a PowerPoint deck into a **knowledge document**.

This skill is optimized for a repeatable, local CLI pipeline (no UI required):
- Extract slide text + speaker notes
- Extract embedded images
- OCR images (diagrams/screenshots)
- Produce:
  - `knowledge.json` (structured)
  - `knowledge.md` (download/share)

## Quick start (CLI)

```bash
# From the repo root:
cd skills/ppt-knowledge-doc/scripts
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python ppt_kd_cli.py /path/to/deck.pptx --out /tmp/ppt-kd-out
# outputs: /tmp/ppt-kd-out/knowledge.json and knowledge.md
```

## What it generates

- Executive summary
- Key concepts / glossary (heuristic)
- Processes / steps (best-effort from OCR text)
- Slide-by-slide notes:
  - slide title
  - extracted text
  - speaker notes
  - OCR text from images

## Notes / Dependencies

- OCR uses **Tesseract** if installed.
- Optional conversions (for hard PPTs): **LibreOffice** (`soffice`) and **Poppler** (`pdftoppm`).

See `references/system-capabilities.md`.
