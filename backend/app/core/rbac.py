from enum import Enum
from typing import Set

from app.domain.entities.user import User


class Permission(str, Enum):
    CONNECTION_CREATE = "connection:create"
    CONNECTION_READ = "connection:read"
    CONNECTION_DELETE = "connection:delete"
    CONNECTION_TEST = "connection:test"

    RULE_CREATE = "rule:create"
    RULE_READ = "rule:read"
    RULE_UPDATE = "rule:update"
    RULE_DELETE = "rule:delete"

    JOB_CREATE = "job:create"
    JOB_READ = "job:read"
    JOB_RUN = "job:run"
    JOB_SHARE = "job:share"

    USER_MANAGE = "user:manage"
    SYSTEM_CONFIG = "system:config"
    AUDIT_READ = "audit:read"
    COMPLIANCE_VIEW = "compliance:view"


ROLE_PERMISSIONS: dict[str, Set[Permission]] = {
    "admin": set(Permission),
    "security_officer": {
        Permission.CONNECTION_READ,
        Permission.CONNECTION_TEST,
        Permission.RULE_READ,
        Permission.RULE_CREATE,
        Permission.RULE_UPDATE,
        Permission.RULE_DELETE,
        Permission.JOB_READ,
        Permission.USER_MANAGE,
        Permission.SYSTEM_CONFIG,
        Permission.AUDIT_READ,
        Permission.COMPLIANCE_VIEW,
    },
    "auditor": {
        Permission.CONNECTION_READ,
        Permission.RULE_READ,
        Permission.JOB_READ,
        Permission.AUDIT_READ,
        Permission.COMPLIANCE_VIEW,
    },
    "operator": {
        Permission.CONNECTION_CREATE,
        Permission.CONNECTION_READ,
        Permission.CONNECTION_DELETE,
        Permission.CONNECTION_TEST,
        Permission.RULE_CREATE,
        Permission.RULE_READ,
        Permission.RULE_UPDATE,
        Permission.RULE_DELETE,
        Permission.JOB_CREATE,
        Permission.JOB_READ,
        Permission.JOB_RUN,
        Permission.JOB_SHARE,
    },
    "viewer": {
        Permission.CONNECTION_READ,
        Permission.RULE_READ,
        Permission.JOB_READ,
    },
}


def check_permission(user_role: str, permission: Permission) -> bool:
    role_perms = ROLE_PERMISSIONS.get(user_role, set())
    return permission in role_perms


def get_user_permissions(user_role: str) -> Set[Permission]:
    return ROLE_PERMISSIONS.get(user_role, set())
