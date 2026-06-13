from enum import Enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    SECURITY_OFFICER = "security_officer"
    AUDITOR = "auditor"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(BaseModel):
    id: Optional[str] = None
    email: str
    name: str
    picture: Optional[str] = None
    password_hash: Optional[str] = Field(default=None, repr=False)
    role: UserRole = UserRole.VIEWER
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = Field(default=None, repr=False)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
