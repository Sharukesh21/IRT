"""Jobs API — poll background task status."""

from fastapi import APIRouter, HTTPException

from app.core.job_store import job_store

router = APIRouter()


@router.get("/{job_id}", summary="Get background job status")
async def get_job_status(job_id: str) -> dict:
    """Return the current status of a background job.

    Poll this endpoint after starting a long-running operation (e.g. incident
    detection, regression suite run) until status is COMPLETED or FAILED.
    """
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()
