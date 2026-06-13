import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCreateRule:
    async def test_create_rule(self, client: AsyncClient, auth_headers: dict):
        conn_payload = {
            "name": "Rule Test Conn",
            "type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "postgres",
            "password": "postgres",
        }
        conn_resp = await client.post("/api/v1/connections/", json=conn_payload, headers=auth_headers)
        conn_id = conn_resp.json()["id"]

        rule_payload = {
            "name": "Mask email",
            "connection_id": conn_id,
            "target_table": "users",
            "target_column": "email",
            "strategy": "substitution",
            "strategy_options": {"provider": "email"},
        }
        resp = await client.post("/api/v1/rules/", json=rule_payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Mask email"
        assert data["strategy"] == "substitution"
        assert "id" in data

    async def test_create_rule_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/rules/", json={
            "name": "test",
            "connection_id": "x",
            "target_table": "t",
            "target_column": "c",
            "strategy": "substitution",
        })
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestListRules:
    async def test_list_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/rules/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_after_create(self, client: AsyncClient, auth_headers: dict):
        conn_resp = await client.post("/api/v1/connections/", json={
            "name": "RL", "type": "postgresql", "host": "localhost",
            "port": 5432, "database": "db", "username": "u", "password": "p",
        }, headers=auth_headers)
        conn_id = conn_resp.json()["id"]
        await client.post("/api/v1/rules/", json={
            "name": "R1", "connection_id": conn_id,
            "target_table": "t", "target_column": "c",
            "strategy": "substitution",
        }, headers=auth_headers)
        resp = await client.get("/api/v1/rules/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


@pytest.mark.asyncio
class TestGetRule:
    async def test_get_existing(self, client: AsyncClient, auth_headers: dict):
        conn_resp = await client.post("/api/v1/connections/", json={
            "name": "GR", "type": "postgresql", "host": "localhost",
            "port": 5432, "database": "db", "username": "u", "password": "p",
        }, headers=auth_headers)
        conn_id = conn_resp.json()["id"]
        rule_resp = await client.post("/api/v1/rules/", json={
            "name": "GetRule", "connection_id": conn_id,
            "target_table": "t", "target_column": "c",
            "strategy": "redaction",
        }, headers=auth_headers)
        rule_id = rule_resp.json()["id"]
        resp = await client.get(f"/api/v1/rules/{rule_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == rule_id

    async def test_get_nonexistent(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/rules/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestUpdateRule:
    async def test_update_rule(self, client: AsyncClient, auth_headers: dict):
        conn_resp = await client.post("/api/v1/connections/", json={
            "name": "UR", "type": "postgresql", "host": "localhost",
            "port": 5432, "database": "db", "username": "u", "password": "p",
        }, headers=auth_headers)
        conn_id = conn_resp.json()["id"]
        rule_resp = await client.post("/api/v1/rules/", json={
            "name": "UpdateMe", "connection_id": conn_id,
            "target_table": "t", "target_column": "c",
            "strategy": "redaction",
        }, headers=auth_headers)
        rule_id = rule_resp.json()["id"]
        resp = await client.put(f"/api/v1/rules/{rule_id}", json={
            "name": "Updated", "connection_id": conn_id,
            "target_table": "t", "target_column": "c",
            "strategy": "hashing_sha256",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["strategy"] == "hashing_sha256"


@pytest.mark.asyncio
class TestDeleteRule:
    async def test_delete_rule(self, client: AsyncClient, auth_headers: dict):
        conn_resp = await client.post("/api/v1/connections/", json={
            "name": "DR", "type": "postgresql", "host": "localhost",
            "port": 5432, "database": "db", "username": "u", "password": "p",
        }, headers=auth_headers)
        conn_id = conn_resp.json()["id"]
        rule_resp = await client.post("/api/v1/rules/", json={
            "name": "DeleteMe", "connection_id": conn_id,
            "target_table": "t", "target_column": "c",
            "strategy": "nullification",
        }, headers=auth_headers)
        rule_id = rule_resp.json()["id"]
        resp = await client.delete(f"/api/v1/rules/{rule_id}", headers=auth_headers)
        assert resp.status_code == 204
