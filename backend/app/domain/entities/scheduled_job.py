from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScheduledJob(BaseModel):
    id: Optional[str] = None
    masking_job_id: str
    cron_expression: str
    timezone: str = "UTC"
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
