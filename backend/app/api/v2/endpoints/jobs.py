from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from pydantic import BaseModel

from app.api.deps import get_job_orchestrator, get_job_repository, require_permission
from app.application.schemas import JobCreate, JobResponse
from app.application.services.job_orchestrator import JobOrchestrator
from app.core.exceptions import ResourceNotFoundError
from app.core.rbac import Permission
from app.domain.entities.user import User
from app.domain.entities.masking_job import JobStatus
from app.domain.interfaces.repository import JobRepository

router = APIRouter()


class PaginatedJobResponse(BaseModel):
    items: List[JobResponse]
    total: int
    skip: int
    limit: int


class CancelResponse(BaseModel):
    job_id: str
    status: str
    message: str


@router.get("/", response_model=PaginatedJobResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[JobStatus] = Query(None, alias="status"),
    user: User = Depends(require_permission(Permission.JOB_READ)),
    repository: JobRepository = Depends(get_job_repository),
):
    all_jobs = await repository.get_all()
    filtered = [j for j in all_jobs if getattr(j, "owner_id", None) == user.id]

    if status_filter:
        filtered = [j for j in filtered if j.status == status_filter]

    filtered.sort(key=lambda j: j.created_at or "", reverse=True)

    total = len(filtered)
    page = filtered[skip : skip + limit]
    items = [JobResponse.model_validate(j.model_dump()) for j in page]

    return PaginatedJobResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    user: User = Depends(require_permission(Permission.JOB_CREATE)),
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
):
    try:
        return await orchestrator.create_job(data, user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    user: User = Depends(require_permission(Permission.JOB_READ)),
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
):
    try:
        return await orchestrator.get_job(job_id, user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{job_id}/run")
async def run_job(
    job_id: str,
    user: User = Depends(require_permission(Permission.JOB_RUN)),
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
):
    try:
        await orchestrator.get_job(job_id, user.id)
        from fastapi import BackgroundTasks
        orchestrator_ref = orchestrator
        import asyncio
        asyncio.create_task(orchestrator_ref.run_job(job_id, user.id))
        return {"message": "Job execution started", "job_id": job_id}
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{job_id}/cancel", response_model=CancelResponse)
async def cancel_job(
    job_id: str,
    user: User = Depends(require_permission(Permission.JOB_RUN)),
    repository: JobRepository = Depends(get_job_repository),
):
    job = await repository.get_by_id(job_id)
    if not job or getattr(job, "owner_id", None) != user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in (JobStatus.PENDING, JobStatus.RUNNING):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status '{job.status.value}'",
        )
    job.status = JobStatus.CANCELLED
    await repository.update(job_id, job)
    return CancelResponse(job_id=job_id, status="cancelled", message="Job cancelled successfully")


@router.get("/{job_id}/history")
async def job_history(
    job_id: str,
    user: User = Depends(require_permission(Permission.JOB_READ)),
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
):
    try:
        audit_logs = await orchestrator.get_audit_log(job_id, user.id)
        return [
            {
                "id": log.id,
                "action": log.action,
                "user_email": log.user_email,
                "is_masked": log.is_masked,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in audit_logs
        ]
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
