from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    UNMASKED = "unmasked"
    CANCELLED = "cancelled"


class MaskingJob(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    connection_id: str
    rule_ids: List[str]
    status: JobStatus = JobStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    execution_log: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    records_processed: int = 0
    owner_id: Optional[str] = None
    shared_with: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
