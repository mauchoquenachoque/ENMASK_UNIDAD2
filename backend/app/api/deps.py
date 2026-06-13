from typing import Callable, List

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.security import api_key_header, bearer_scheme
from app.core.rbac import Permission, check_permission
from app.application.services.auth_service import AuthService
from app.application.services.connection_service import ConnectionService
from app.application.services.job_orchestrator import JobOrchestrator
from app.application.services.masking_service import MaskingService
from app.domain.entities.user import User, UserRole
from app.domain.interfaces.repository import (
    ConnectionRepository,
    JobRepository,
    RuleRepository,
    UserRepository,
    AuditLogRepository,
    ScheduleRepository,
    PluginRepository,
)
from app.infrastructure.repositories.job_repo import MongoJobRepository
from app.infrastructure.repositories.mongodb_connection_repo import MongoDBConnectionRepository
from app.infrastructure.repositories.memory_repository import (
    connection_repository,
    job_repository,
    rule_repository,
)
from app.infrastructure.repositories.postgres_connection_repo import PostgresConnectionRepository
from app.infrastructure.repositories.user_repository import user_repository
from app.infrastructure.repositories.mongo_user_repo import MongoUserRepository
from app.infrastructure.repositories.audit_repo import MongoAuditRepository
from app.domain.interfaces.vault_repository import VaultRepository
from app.infrastructure.repositories.vault_repo import MongoVaultRepository, memory_vault_repository


async def get_connection_repository() -> ConnectionRepository:
    if settings.REPOSITORY_BACKEND == "postgres":
        return PostgresConnectionRepository(settings.POSTGRES_META_DSN)
    if settings.REPOSITORY_BACKEND == "mongodb":
        return MongoDBConnectionRepository(settings.MONGODB_META_URI, settings.METADATA_DATABASE)
    return connection_repository


async def get_rule_repository() -> RuleRepository:
    return rule_repository


async def get_job_repository() -> JobRepository:
    if settings.REPOSITORY_BACKEND == "mongodb":
        return MongoJobRepository(settings.MONGODB_META_URI, settings.METADATA_DATABASE)
    return job_repository


async def get_user_repository() -> UserRepository:
    if settings.REPOSITORY_BACKEND == "mongodb":
        return MongoUserRepository(settings.MONGODB_META_URI, settings.METADATA_DATABASE)
    return user_repository


async def get_audit_repository() -> AuditLogRepository:
    if settings.REPOSITORY_BACKEND == "mongodb":
        return MongoAuditRepository(settings.MONGODB_META_URI, settings.METADATA_DATABASE)
    return None


async def get_vault_repository() -> VaultRepository:
    if settings.REPOSITORY_BACKEND == "mongodb":
        return MongoVaultRepository(settings.MONGODB_META_URI, settings.METADATA_DATABASE)
    return memory_vault_repository


async def get_connection_service(
    repository: ConnectionRepository = Depends(get_connection_repository),
) -> ConnectionService:
    return ConnectionService(repository)


async def get_masking_service(
    repository: RuleRepository = Depends(get_rule_repository),
    connection_repository: ConnectionRepository = Depends(get_connection_repository),
) -> MaskingService:
    return MaskingService(repository, connection_repository)


async def get_job_orchestrator(
    connection_repository: ConnectionRepository = Depends(get_connection_repository),
    rule_repository: RuleRepository = Depends(get_rule_repository),
    job_repository: JobRepository = Depends(get_job_repository),
    audit_repository: AuditLogRepository = Depends(get_audit_repository),
    user_repository_instance: UserRepository = Depends(get_user_repository),
    vault_repository: VaultRepository = Depends(get_vault_repository),
) -> JobOrchestrator:
    return JobOrchestrator(
        connection_repository=connection_repository,
        rule_repository=rule_repository,
        job_repository=job_repository,
        audit_repository=audit_repository,
        user_repository=user_repository_instance,
        vault_repository=vault_repository,
    )


async def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


async def get_authorization_token(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> str:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_authorization_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        return await auth_service.get_current_user(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


def _validate_domain(email: str) -> None:
    allowed = settings.allowed_domains_list()
    if not allowed:
        return
    domain = email.split("@")[-1].lower()
    if domain not in [d.lower() for d in allowed]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Domain '{domain}' is not allowed.",
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    _validate_domain(current_user.email)
    return current_user


def require_role(roles: List[str]) -> Callable:
    async def dependency(user: User = Depends(get_current_active_user)) -> User:
        user_role = user.role.value if isinstance(user.role, UserRole) else str(user.role)
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role}' not in required roles: {', '.join(roles)}",
            )
        return user
    return dependency


def require_permission(permission: Permission) -> Callable:
    async def dependency(user: User = Depends(get_current_active_user)) -> User:
        user_role = user.role.value if isinstance(user.role, UserRole) else str(user.role)
        if not check_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: requires {permission.value}",
            )
        return user
    return dependency


async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    if not settings.API_KEY:
        return ""
    if api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key.",
    )
