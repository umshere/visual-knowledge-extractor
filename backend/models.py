from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedImageInfo(BaseModel):
    image_id: str
    filename: str
    slide_index: int
    ocr_text: Optional[str] = None


class SlideInfo(BaseModel):
    slide_index: int
    title: Optional[str] = None
    text_items: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    images: List[ExtractedImageInfo] = Field(default_factory=list)


class KnowledgeDoc(BaseModel):
    source_filename: str
    slide_count: int
    slides: List[SlideInfo]


class JobStatus(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    progress: float = 0.0
    result: Optional[KnowledgeDoc] = None
    error: Optional[str] = None
