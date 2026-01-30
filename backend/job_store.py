from __future__ import annotations

import threading
from typing import Dict, Optional

from .models import JobStatus


class InMemoryJobStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: Dict[str, JobStatus] = {}

    def create(self, job: JobStatus) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    def get(self, job_id: str) -> Optional[JobStatus]:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs) -> Optional[JobStatus]:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            updated = job.model_copy(update=kwargs)
            self._jobs[job_id] = updated
            return updated

    def set(self, job: JobStatus) -> None:
        with self._lock:
            self._jobs[job.job_id] = job
