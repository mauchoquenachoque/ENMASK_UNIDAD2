import pytest
from httpx import AsyncClient
from app.domain.entities.user import User


@pytest.mark.asyncio
class TestCreateConnection:
    async def test_create_connection(self, client: AsyncClient, auth_headers: dict):
        payload = {
            "name": "Test DB",
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "postgres",
            "password": "postgres",
        }
        resp = await client.post("/api/v1/connections/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test DB"
        assert "id" in data

    async def test_create_connection_unauthorized(self, client: AsyncClient):
        payload = {
            "name": "Test DB",
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "postgres",
            "password": "postgres",
        }
        resp = await client.post("/api/v1/connections/", json=payload)
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestListConnections:
    async def test_list_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/connections/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_owner_isolation(self, client: AsyncClient, auth_headers: dict, operator_auth_headers: dict):
        payload = {
            "name": "Owner Conn",
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "postgres",
            "password": "postgres",
        }
        await client.post("/api/v1/connections/", json=payload, headers=auth_headers)
        resp = await client.get("/api/v1/connections/", headers=operator_auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 0


@pytest.mark.asyncio
class TestGetConnection:
    async def test_get_existing(self, client: AsyncClient, auth_headers: dict):
        payload = {
            "name": "Get Me",
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "postgres",
            "password": "postgres",
        }
        create_resp = await client.post("/api/v1/connections/", json=payload, headers=auth_headers)
        conn_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/connections/{conn_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == conn_id

    async def test_get_nonexistent(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/connections/nonexistent-id", headers=auth_headers)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestDeleteConnection:
    async def test_delete_existing(self, client: AsyncClient, auth_headers: dict):
        payload = {
            "name": "Delete Me",
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "postgres",
            "password": "postgres",
        }
        create_resp = await client.post("/api/v1/connections/", json=payload, headers=auth_headers)
        conn_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/v1/connections/{conn_id}", headers=auth_headers)
        assert resp.status_code == 204

    async def test_delete_nonexistent(self, client: AsyncClient, auth_headers: dict):
        resp = await client.delete("/api/v1/connections/nonexistent-id", headers=auth_headers)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestDiscoverPII:
    async def test_discover_pii(self, client: AsyncClient, auth_headers: dict):
        payload = {
            "name": "Discover Conn",
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "postgres",
            "password": "postgres",
        }
        create_resp = await client.post("/api/v1/connections/", json=payload, headers=auth_headers)
        conn_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/connections/{conn_id}/discover", headers=auth_headers)
        assert resp.status_code in (200, 400)
