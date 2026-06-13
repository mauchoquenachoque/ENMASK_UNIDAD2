from datetime import datetime, timezone
from typing import Any, Dict, List

from workers.celery_app import celery_app
from app.core.logging import logger


@celery_app.task(name="workers.tasks.schedule_tasks.check_and_run_scheduled_jobs")
def check_and_run_scheduled_jobs() -> Dict[str, Any]:
    import asyncio

    async def _run() -> Dict[str, Any]:
        from app.api.deps import get_job_repository
        from app.domain.entities.masking_job import JobStatus

        job_repo = await get_job_repository()
        all_jobs = await job_repo.get_all()

        pending_jobs = [j for j in all_jobs if j.status == JobStatus.PENDING and j.scheduled_at]

        now = datetime.now(timezone.utc)
        triggered = 0

        for job in pending_jobs:
            if job.scheduled_at and job.scheduled_at <= now:
                from workers.tasks.masking_tasks import execute_masking_job
                execute_masking_job.delay(
                    job_id=job.id,
                    connection_id=job.connection_id,
                    rule_ids=job.rule_ids,
                    owner_id=job.owner_id or "",
                )
                triggered += 1
                logger.info("Triggered scheduled job %s", job.id)

        return {"checked": len(pending_jobs), "triggered": triggered}

    try:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_run())
        finally:
            loop.close()
    except Exception as exc:
        logger.error("Schedule check failed: %s", str(exc))
        return {"error": str(exc), "checked": 0, "triggered": 0}
