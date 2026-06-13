from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from pydantic import BaseModel

from app.api.deps import require_permission
from app.core.rbac import Permission
from app.domain.entities.user import User

router = APIRouter()

_schedule_store: dict = {}


class ScheduleCreate(BaseModel):
    masking_job_id: str
    cron_expression: str
    timezone: str = "UTC"
    max_retries: int = 3


class ScheduleUpdate(BaseModel):
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    max_retries: Optional[int] = None


class ScheduleResponse(BaseModel):
    id: str
    masking_job_id: str
    cron_expression: str
    timezone: str
    is_active: bool
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    max_retries: int
    retry_count: int
    created_at: Optional[str] = None


@router.get("/", response_model=List[ScheduleResponse])
async def list_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(require_permission(Permission.JOB_READ)),
):
    user_schedules = [
        s for s in _schedule_store.values()
        if s.get("owner_id") == user.id
    ]
    page = user_schedules[skip : skip + limit]
    return [
        ScheduleResponse(
            id=s["id"],
            masking_job_id=s["masking_job_id"],
            cron_expression=s["cron_expression"],
            timezone=s["timezone"],
            is_active=s["is_active"],
            last_run=s.get("last_run"),
            next_run=s.get("next_run"),
            max_retries=s["max_retries"],
            retry_count=s.get("retry_count", 0),
            created_at=s.get("created_at"),
        )
        for s in page
    ]


@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    body: ScheduleCreate,
    user: User = Depends(require_permission(Permission.JOB_CREATE)),
):
    import uuid
    from datetime import datetime

    schedule_id = uuid.uuid4().hex
    schedule = {
        "id": schedule_id,
        "masking_job_id": body.masking_job_id,
        "cron_expression": body.cron_expression,
        "timezone": body.timezone,
        "is_active": True,
        "max_retries": body.max_retries,
        "retry_count": 0,
        "owner_id": user.id,
        "created_at": datetime.utcnow().isoformat(),
    }
    _schedule_store[schedule_id] = schedule

    return ScheduleResponse(
        id=schedule["id"],
        masking_job_id=schedule["masking_job_id"],
        cron_expression=schedule["cron_expression"],
        timezone=schedule["timezone"],
        is_active=schedule["is_active"],
        max_retries=schedule["max_retries"],
        retry_count=schedule["retry_count"],
        created_at=schedule["created_at"],
    )


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    user: User = Depends(require_permission(Permission.JOB_READ)),
):
    schedule = _schedule_store.get(schedule_id)
    if not schedule or schedule.get("owner_id") != user.id:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return ScheduleResponse(
        id=schedule["id"],
        masking_job_id=schedule["masking_job_id"],
        cron_expression=schedule["cron_expression"],
        timezone=schedule["timezone"],
        is_active=schedule["is_active"],
        last_run=schedule.get("last_run"),
        next_run=schedule.get("next_run"),
        max_retries=schedule["max_retries"],
        retry_count=schedule.get("retry_count", 0),
        created_at=schedule.get("created_at"),
    )


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    body: ScheduleUpdate,
    user: User = Depends(require_permission(Permission.JOB_RUN)),
):
    schedule = _schedule_store.get(schedule_id)
    if not schedule or schedule.get("owner_id") != user.id:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if body.cron_expression is not None:
        schedule["cron_expression"] = body.cron_expression
    if body.timezone is not None:
        schedule["timezone"] = body.timezone
    if body.is_active is not None:
        schedule["is_active"] = body.is_active
    if body.max_retries is not None:
        schedule["max_retries"] = body.max_retries

    return ScheduleResponse(
        id=schedule["id"],
        masking_job_id=schedule["masking_job_id"],
        cron_expression=schedule["cron_expression"],
        timezone=schedule["timezone"],
        is_active=schedule["is_active"],
        last_run=schedule.get("last_run"),
        next_run=schedule.get("next_run"),
        max_retries=schedule["max_retries"],
        retry_count=schedule.get("retry_count", 0),
        created_at=schedule.get("created_at"),
    )


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: str,
    user: User = Depends(require_permission(Permission.JOB_RUN)),
):
    schedule = _schedule_store.get(schedule_id)
    if not schedule or schedule.get("owner_id") != user.id:
        raise HTTPException(status_code=404, detail="Schedule not found")
    del _schedule_store[schedule_id]


@router.post("/{schedule_id}/enable", response_model=ScheduleResponse)
async def enable_schedule(
    schedule_id: str,
    user: User = Depends(require_permission(Permission.JOB_RUN)),
):
    schedule = _schedule_store.get(schedule_id)
    if not schedule or schedule.get("owner_id") != user.id:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule["is_active"] = True

    return ScheduleResponse(
        id=schedule["id"],
        masking_job_id=schedule["masking_job_id"],
        cron_expression=schedule["cron_expression"],
        timezone=schedule["timezone"],
        is_active=schedule["is_active"],
        last_run=schedule.get("last_run"),
        next_run=schedule.get("next_run"),
        max_retries=schedule["max_retries"],
        retry_count=schedule.get("retry_count", 0),
        created_at=schedule.get("created_at"),
    )


@router.post("/{schedule_id}/disable", response_model=ScheduleResponse)
async def disable_schedule(
    schedule_id: str,
    user: User = Depends(require_permission(Permission.JOB_RUN)),
):
    schedule = _schedule_store.get(schedule_id)
    if not schedule or schedule.get("owner_id") != user.id:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule["is_active"] = False

    return ScheduleResponse(
        id=schedule["id"],
        masking_job_id=schedule["masking_job_id"],
        cron_expression=schedule["cron_expression"],
        timezone=schedule["timezone"],
        is_active=schedule["is_active"],
        last_run=schedule.get("last_run"),
        next_run=schedule.get("next_run"),
        max_retries=schedule["max_retries"],
        retry_count=schedule.get("retry_count", 0),
        created_at=schedule.get("created_at"),
    )
