import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestV2ConnectionsPagination:
    async def test_pagination_default(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v2/connections/", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

    async def test_pagination_params(self, client: AsyncClient, auth_headers: dict):
        for i in range(3):
            await client.post("/api/v1/connections/", json={
                "name": f"Conn {i}", "type": "postgresql", "host": "localhost",
                "port": 5432, "database": "db", "username": "u", "password": "p",
            }, headers=auth_headers)
        resp = await client.get("/api/v2/connections/?skip=0&limit=2", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 2
        assert data["limit"] == 2

    async def test_pagination_skip(self, client: AsyncClient, auth_headers: dict):
        for i in range(3):
            await client.post("/api/v1/connections/", json={
                "name": f"Skip {i}", "type": "postgresql", "host": "localhost",
                "port": 5432, "database": "db", "username": "u", "password": "p",
            }, headers=auth_headers)
        resp = await client.get("/api/v2/connections/?skip=2&limit=50", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["skip"] == 2


@pytest.mark.asyncio
class TestV2ConnectionsFiltering:
    async def test_filter_by_type(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/v1/connections/", json={
            "name": "PG", "type": "postgresql", "host": "localhost",
            "port": 5432, "database": "db", "username": "u", "password": "p",
        }, headers=auth_headers)
        resp = await client.get("/api/v2/connections/?conn_type=postgresql", headers=auth_headers)
        assert resp.status_code == 200

    async def test_filter_by_status(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/v2/connections/?status=inactive", headers=auth_headers)
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestV2ConnectionsSorting:
    async def test_sort_by_name_asc(self, client: AsyncClient, auth_headers: dict):
        for name in ["Charlie", "Alpha", "Bravo"]:
            await client.post("/api/v1/connections/", json={
                "name": name, "type": "postgresql", "host": "localhost",
                "port": 5432, "database": "db", "username": "u", "password": "p",
            }, headers=auth_headers)
        resp = await client.get("/api/v2/connections/?sort_by=name&sort_order=asc", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["name"] for i in items]
        assert names == sorted(names)

    async def test_sort_by_name_desc(self, client: AsyncClient, auth_headers: dict):
        for name in ["Charlie", "Alpha", "Bravo"]:
            await client.post("/api/v1/connections/", json={
                "name": name, "type": "postgresql", "host": "localhost",
                "port": 5432, "database": "db", "username": "u", "password": "p",
            }, headers=auth_headers)
        resp = await client.get("/api/v2/connections/?sort_by=name&sort_order=desc", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["name"] for i in items]
        assert names == sorted(names, reverse=True)
