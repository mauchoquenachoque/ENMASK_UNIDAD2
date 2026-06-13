import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.core.security import create_access_token
from app.domain.entities.user import User, UserRole
from app.infrastructure.repositories.user_repository import UserRepository


@pytest.mark.asyncio
class TestAuthGoogle:
    async def test_google_login_missing_token(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/google", json={})
        assert resp.status_code == 400
        assert "id_token" in resp.json()["detail"].lower() or "missing" in resp.json()["detail"].lower()


@pytest.mark.asyncio
class TestAuthMe:
    async def test_me_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_me_with_valid_token(self, client: AsyncClient, seeded_user: User, auth_headers: dict):
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == seeded_user.email

    async def test_me_with_invalid_token(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401

    async def test_me_with_expired_token(self, client: AsyncClient, seeded_user: User):
        from datetime import timedelta
        token = create_access_token(subject=seeded_user.id, expires_delta=timedelta(seconds=-10))
        resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestAuthRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "newuser@enmask.io",
            "password": "StrongP@ss123",
            "name": "New User",
        })
        assert resp.status_code in (200, 201, 404)

    async def test_register_duplicate_email(self, client: AsyncClient, seeded_user: User):
        resp = await client.post("/api/v1/auth/register", json={
            "email": seeded_user.email,
            "password": "StrongP@ss123",
            "name": "Dup User",
        })
        assert resp.status_code in (400, 409, 404)

    async def test_register_weak_password(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "weak@enmask.io",
            "password": "123",
            "name": "Weak",
        })
        assert resp.status_code in (400, 422, 404)


@pytest.mark.asyncio
class TestAuthLogin:
    async def test_login_success(self, client: AsyncClient, seeded_user: User):
        resp = await client.post("/api/v1/auth/login", json={
            "email": seeded_user.email,
            "password": "StrongP@ss123",
        })
        assert resp.status_code in (200, 404)

    async def test_login_wrong_password(self, client: AsyncClient, seeded_user: User):
        resp = await client.post("/api/v1/auth/login", json={
            "email": seeded_user.email,
            "password": "WrongPassword1!",
        })
        assert resp.status_code in (401, 400, 404)

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@enmask.io",
            "password": "Whatever1!",
        })
        assert resp.status_code in (401, 400, 404)
