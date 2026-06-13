import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCreateJob:
    async def test_create_job(self, client: AsyncClient, auth_headers: dict):
        conn_resp = await client.post("/api/v1/connections/", json={
            "name": "Job Conn", "type": "postgresql", "host": "localhost",
            "port": 5432, "database": "db", "username": "u", "password": "p",
        }, headers=auth_headers)
        conn_id = conn_resp.json()["id"]
        rule_resp = await client.post("/api/v1/rules/", json={
            "name": "JR", "connection_id": conn_id,
            "target_table": "t", "target_column": "c",
            "strategy": "substitution",
        }, headers=auth_headers)
        rule_id = rule_resp.json()["id"]
        resp = await client.post("/api/v1/jobs/", json={
            "connection_id": conn_id,
            "rule_ids": [rule_id],
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["connection_id"] == conn_id
        assert data["status"] in ("pending", "PENDING")
        assert "id" in data

    async def test_create_job_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/v1/jobs/", json={
            "connection_id": "x", "rule_ids": ["y"],
        })
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestListJobs:
    async def test_list_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/jobs/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestGetJob:
    async def test_get_nonexistent(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v1/jobs/nonexistent", headers=auth_headers)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestRunJob:
    async def test_run_nonexistent(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/v1/jobs/nonexistent/run", headers=auth_headers)
        assert resp.status_code == 404

    async def test_run_existing(self, client: AsyncClient, auth_headers: dict):
        conn_resp = await client.post("/api/v1/connections/", json={
            "name": "RunConn", "type": "postgresql", "host": "localhost",
            "port": 5432, "database": "db", "username": "u", "password": "p",
        }, headers=auth_headers)
        conn_id = conn_resp.json()["id"]
        rule_resp = await client.post("/api/v1/rules/", json={
            "name": "RR", "connection_id": conn_id,
            "target_table": "t", "target_column": "c",
            "strategy": "substitution",
        }, headers=auth_headers)
        rule_id = rule_resp.json()["id"]
        job_resp = await client.post("/api/v1/jobs/", json={
            "connection_id": conn_id, "rule_ids": [rule_id],
        }, headers=auth_headers)
        job_id = job_resp.json()["id"]
        resp = await client.post(f"/api/v1/jobs/{job_id}/run", headers=auth_headers)
        assert resp.status_code == 200
        assert "message" in resp.json()


@pytest.mark.asyncio
class TestShareJob:
    async def test_share_nonexistent(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/v1/jobs/nonexistent/share", json={
            "email": "share@example.com",
        }, headers=auth_headers)
        assert resp.status_code == 404

    async def test_share_existing(self, client: AsyncClient, auth_headers: dict):
        conn_resp = await client.post("/api/v1/connections/", json={
            "name": "ShareConn", "type": "postgresql", "host": "localhost",
            "port": 5432, "database": "db", "username": "u", "password": "p",
        }, headers=auth_headers)
        conn_id = conn_resp.json()["id"]
        rule_resp = await client.post("/api/v1/rules/", json={
            "name": "SR", "connection_id": conn_id,
            "target_table": "t", "target_column": "c",
            "strategy": "substitution",
        }, headers=auth_headers)
        rule_id = rule_resp.json()["id"]
        job_resp = await client.post("/api/v1/jobs/", json={
            "connection_id": conn_id, "rule_ids": [rule_id],
        }, headers=auth_headers)
        job_id = job_resp.json()["id"]
        resp = await client.post(f"/api/v1/jobs/{job_id}/share", json={
            "email": "share@example.com",
        }, headers=auth_headers)
        assert resp.status_code == 200
