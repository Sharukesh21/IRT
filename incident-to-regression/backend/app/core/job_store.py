"""In-memory job store for tracking background task progress.

Provides a simple PENDING → RUNNING → COMPLETED/FAILED lifecycle.
For production multi-process deployments, replace with a Redis or DB-backed store.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Job:
    job_id: str
    job_type: str
    status: JobStatus = JobStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "elapsed_seconds": round(time.time() - self.created_at, 2),
        }


class InMemoryJobStore:
    """Thread-safe in-memory job store with automatic eviction of old jobs."""

    def __init__(self, max_jobs: int = 500) -> None:
        self._jobs: dict[str, Job] = {}
        self._max_jobs = max_jobs

    def create(self, job_type: str) -> Job:
        """Create and register a new job."""
        if len(self._jobs) >= self._max_jobs:
            # Evict the 50 oldest jobs
            oldest = sorted(self._jobs.values(), key=lambda j: j.created_at)[:50]
            for j in oldest:
                del self._jobs[j.job_id]
        job = Job(job_id=str(uuid.uuid4()), job_type=job_type)
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        **kwargs: Any,
    ) -> None:
        job = self._jobs.get(job_id)
        if job:
            job.status = status
            for k, v in kwargs.items():
                setattr(job, k, v)


# Process-level singleton
job_store = InMemoryJobStore()
