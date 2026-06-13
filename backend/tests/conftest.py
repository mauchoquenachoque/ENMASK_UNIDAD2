import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.core.security import create_access_token
from app.domain.entities.connection import ConnectionConfig
from app.domain.entities.masking_job import MaskingJob, JobStatus
from app.domain.entities.masking_rule import MaskingRule
from app.domain.entities.user import User, UserRole
from app.domain.value_objects.database_type import DatabaseType
from app.domain.value_objects.masking_algorithm import MaskingAlgorithm
from app.infrastructure.repositories.memory_repository import (
    MemoryRepository,
    connection_repository,
    job_repository,
    rule_repository,
)
from app.infrastructure.repositories.user_repository import UserRepository


@pytest.fixture(autouse=True)
def _clear_repositories():
    connection_repository._data.clear()
    rule_repository._data.clear()
    job_repository._data.clear()


@pytest.fixture
def user_repo() -> UserRepository:
    repo = UserRepository()
    repo._data.clear()
    return repo


@pytest.fixture
def admin_user() -> User:
    return User(
        id=str(uuid.uuid4()),
        email="admin@enmask.io",
        name="Admin User",
        role=UserRole.ADMIN,
        password_hash="$2b$12$test_hash_placeholder",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def operator_user() -> User:
    return User(
        id=str(uuid.uuid4()),
        email="operator@enmask.io",
        name="Operator User",
        role=UserRole.OPERATOR,
        password_hash="$2b$12$test_hash_placeholder",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def viewer_user() -> User:
    return User(
        id=str(uuid.uuid4()),
        email="viewer@enmask.io",
        name="Viewer User",
        role=UserRole.VIEWER,
        password_hash="$2b$12$test_hash_placeholder",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def auditor_user() -> User:
    return User(
        id=str(uuid.uuid4()),
        email="auditor@enmask.io",
        name="Auditor User",
        role=UserRole.AUDITOR,
        password_hash="$2b$12$test_hash_placeholder",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def security_officer_user() -> User:
    return User(
        id=str(uuid.uuid4()),
        email="security@enmask.io",
        name="Security Officer",
        role=UserRole.SECURITY_OFFICER,
        password_hash="$2b$12$test_hash_placeholder",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def auth_headers(admin_user: User) -> dict[str, str]:
    token = create_access_token(subject=admin_user.id, extra_claims={"email": admin_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def operator_auth_headers(operator_user: User) -> dict[str, str]:
    token = create_access_token(subject=operator_user.id, extra_claims={"email": operator_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def viewer_auth_headers(viewer_user: User) -> dict[str, str]:
    token = create_access_token(subject=viewer_user.id, extra_claims={"email": viewer_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_connection(admin_user: User) -> ConnectionConfig:
    return ConnectionConfig(
        id=str(uuid.uuid4()),
        name="Test PG",
        type=DatabaseType.POSTGRESQL,
        host="localhost",
        port=5432,
        database="testdb",
        username="postgres",
        password="postgres",
        owner_id=admin_user.id,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_rule(sample_connection: ConnectionConfig, admin_user: User) -> MaskingRule:
    return MaskingRule(
        id=str(uuid.uuid4()),
        name="Mask email",
        connection_id=sample_connection.id,
        target_table="users",
        target_column="email",
        strategy=MaskingAlgorithm.SUBSTITUTION,
        strategy_options={"provider": "email"},
        owner_id=admin_user.id,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_job(sample_connection: ConnectionConfig, sample_rule: MaskingRule, admin_user: User) -> MaskingJob:
    return MaskingJob(
        id=str(uuid.uuid4()),
        connection_id=sample_connection.id,
        rule_ids=[sample_rule.id],
        status=JobStatus.PENDING,
        owner_id=admin_user.id,
        records_processed=0,
        created_at=datetime.now(timezone.utc),
    )


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def seeded_user(user_repo: UserRepository, admin_user: User) -> User:
    await user_repo.create(admin_user)
    return admin_user
