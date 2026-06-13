from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "enmask_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_soft_time_limit=3600,
    task_time_limit=7200,
    result_expires=86400,
    beat_schedule={
        "check-scheduled-jobs": {
            "task": "workers.tasks.schedule_tasks.check_and_run_scheduled_jobs",
            "schedule": crontab(minute="*/5"),
        },
    },
)

celery_app.autodiscover_tasks(["workers.tasks"])
