from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.value_objects.database_type import DatabaseType


class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class ConnectionConfig(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    additional_options: Optional[Dict[str, Any]] = None
    owner_id: Optional[str] = None
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    connection_pool_size: int = 5
    timeout_seconds: int = 30
    last_tested_at: Optional[datetime] = None
    status: ConnectionStatus = ConnectionStatus.INACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


Connection = ConnectionConfig
