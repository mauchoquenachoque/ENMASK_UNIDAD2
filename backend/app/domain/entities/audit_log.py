from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.compliance_framework import ComplianceFramework


class AuditLog(BaseModel):
    id: Optional[str] = None
    job_id: Optional[str] = None
    user_id: str
    user_email: str
    user_role: str
    action: str = "query"
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    is_masked: bool = False
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = {}
    compliance_framework: Optional[ComplianceFramework] = None
    timestamp: datetime = None

    model_config = ConfigDict(from_attributes=True)
