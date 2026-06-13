from typing import Optional, Dict, Any, List
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.masking_algorithm import MaskingAlgorithm
from app.domain.value_objects.data_type import DataType
from app.domain.value_objects.compliance_framework import ComplianceFramework


class MaskingRule(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    connection_id: str
    target_table: str
    target_column: str
    data_type: Optional[DataType] = None
    strategy: MaskingAlgorithm
    strategy_options: Optional[Dict[str, Any]] = None
    compliance_frameworks: List[ComplianceFramework] = []
    priority: int = 0
    is_active: bool = True
    owner_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
