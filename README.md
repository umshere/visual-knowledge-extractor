# Visual Knowledge Extractor (PPTX MVP)

MVP web app to upload a `.pptx`, extract slide text, speaker notes, images, run OCR, and produce a structured knowledge document JSON + downloadable Markdown file.

This repo is named/structured to grow into a **general visual knowledge extractor** (PPT today; PDFs, diagrams, and other visual docs next).

## Project structure

- `frontend` - Next.js (TypeScript)
- `backend` - FastAPI (Python)
- `README.md` - setup and usage

## Prerequisites

- Node.js 18+
- Python 3.10+
- macOS: install OCR + conversion tools (optional but recommended)

```bash
brew install tesseract poppler
brew install --cask libreoffice
```

If Tesseract is not installed, the backend will skip OCR and continue.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Makefile

```bash
make dev-backend
make dev-frontend
```

Or use the combined helper (runs both in one shell):

```bash
make dev
```

## API

- `POST /api/upload` (multipart) -> `{ jobId }`
- `GET /api/job/{jobId}` -> job status + partial results
- `GET /api/job/{jobId}/download` -> generated Markdown file

## Notes

- Job data is stored in-memory for dev; the job store is isolated so it can be swapped to Redis later.
- Uploaded files and outputs are stored under `/tmp/ppt-knowledge-doc/{jobId}` by default.

## OpenClaw skill (optional)

This repo also includes an OpenClaw skill at `skills/ppt-knowledge-doc/`.

**Install (manual):**
1. Copy `skills/ppt-knowledge-doc` into your OpenClaw skills folder (commonly `~/.openclaw/skills/`)
2. Restart the OpenClaw gateway

**Package for sharing:**
```bash
python3 /usr/local/lib/node_modules/clawdbot/skills/skill-creator/scripts/package_skill.py \
  skills/ppt-knowledge-doc dist
# produces: dist/ppt-knowledge-doc.skill
```

Anyone can then install by dropping the `.skill` file into their OpenClaw/skills install flow (or unpacking it into their skills directory).
