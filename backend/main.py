from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .job_store import InMemoryJobStore
from .models import JobStatus, KnowledgeDoc, SlideInfo
from .processing import extract_knowledge_doc, generate_markdown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ppt-knowledge-doc")

BASE_DIR = Path(__file__).resolve().parent
TMP_ROOT = Path(os.environ.get("PPT_KNOWLEDGE_TMP", "/tmp/ppt-knowledge-doc"))
TMP_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ppt-knowledge-doc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_store = InMemoryJobStore()


def _job_dir(job_id: str) -> Path:
    return TMP_ROOT / job_id


def _write_upload(job_id: str, upload: UploadFile) -> Path:
    job_dir = _job_dir(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    pptx_path = job_dir / upload.filename
    with pptx_path.open("wb") as f:
        f.write(upload.file.read())
    return pptx_path


def _process_job(job_id: str, pptx_path: Path) -> None:
    logger.info("Processing job %s", job_id)
    job_store.update(job_id, status="running", message="Extracting slides", progress=0.1)
    try:
        def on_slide(slides, slide_index, total_slides):
            progress = min(0.85, 0.1 + (slide_index / max(total_slides, 1)) * 0.75)
            partial_doc = KnowledgeDoc(
                source_filename=pptx_path.name,
                slide_count=total_slides,
                slides=[SlideInfo.model_validate(slide) for slide in slides],
            )
            job_store.update(
                job_id,
                status="running",
                message=f"Processed slide {slide_index} of {total_slides}",
                progress=progress,
                result=partial_doc,
            )

        doc = extract_knowledge_doc(pptx_path, _job_dir(job_id), on_slide=on_slide)
        job_store.update(job_id, status="running", message="Generating markdown", progress=0.9)
        markdown = generate_markdown(doc)
        md_path = _job_dir(job_id) / "knowledge_doc.md"
        md_path.write_text(markdown, encoding="utf-8")
        job_store.update(job_id, status="completed", message="Done", progress=1.0, result=doc)
    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        job_store.update(job_id, status="failed", error=str(exc), message="Failed", progress=1.0)


@app.post("/api/upload")
async def upload_pptx(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Only .pptx files are supported.")

    job_id = str(uuid.uuid4())
    job_store.create(
        JobStatus(job_id=job_id, status="queued", message="Queued", progress=0.0)
    )
    pptx_path = _write_upload(job_id, file)
    background_tasks.add_task(_process_job, job_id, pptx_path)
    return {"jobId": job_id}


@app.get("/api/job/{job_id}")
async def get_job(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/job/{job_id}/download")
async def download_markdown(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    md_path = _job_dir(job_id) / "knowledge_doc.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Markdown not found")

    return FileResponse(
        path=md_path,
        media_type="text/markdown",
        filename=f"knowledge_doc_{job_id}.md",
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}
