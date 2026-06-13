from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import aiohttp

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class CouchDBConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url: str = ""

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.COUCHDB

    async def _do_connect(self) -> None:
        scheme = "https" if self.ssl else "http"
        self._base_url = f"{scheme}://{self.host}:{self.port}"
        auth = aiohttp.BasicAuth(self.username, self.password) if self.username else None
        self._session = aiohttp.ClientSession(auth=auth)

    async def _do_disconnect(self) -> None:
        if self._session:
            await self._session.close()

    async def _do_health_check(self) -> None:
        async with self._session.get(f"{self._base_url}/") as resp:
            resp.raise_for_status()

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Use document-specific methods for CouchDB")

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self._base_url}{path}"
        async with self._session.request(method, url, **kwargs) as resp:
            if resp.status == 404:
                return None
            resp.raise_for_status()
            if resp.content_type == "application/json":
                return await resp.json()
            return await resp.text()

    async def get_schema(self) -> Dict[str, List[str]]:
        resp = await self._request("GET", "/_all_dbs")
        databases = resp or []
        schema: Dict[str, List[str]] = {}
        for db_name in databases:
            if db_name.startswith("_"):
                continue
            info = await self._request("GET", f"/{db_name}")
            if info:
                doc_count = info.get("doc_count", 0)
                if doc_count > 0:
                    all_docs = await self._request(
                        "GET", f"/{db_name}/_all_docs", params={"include_docs": "true", "limit": 1}
                    )
                    if all_docs and all_docs.get("rows"):
                        doc = all_docs["rows"][0].get("doc", {})
                        schema[db_name] = [k for k in doc.keys() if k not in ("_id", "_rev")]
                    else:
                        schema[db_name] = []
                else:
                    schema[db_name] = []
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        return ["_id"]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        params = {"include_docs": "true", "limit": limit, "skip": offset}
        resp = await self._request("GET", f"/{table}/_all_docs", params=params)
        if not resp:
            return []
        return [row["doc"] for row in resp.get("rows", [])]

    async def count_records(self, table: str) -> int:
        info = await self._request("GET", f"/{table}")
        return info.get("doc_count", 0) if info else 0

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"include_docs": "true"}
        if limit is not None:
            params["limit"] = limit
        if filters and "selector" in filters:
            resp = await self._request("POST", f"/{table}/_find", json=filters)
            return resp.get("docs", []) if resp else []
        resp = await self._request("GET", f"/{table}/_all_docs", params=params)
        if not resp:
            return []
        return [row["doc"] for row in resp.get("rows", [])]

    async def fetch_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        doc_id = filters.get("_id")
        if doc_id:
            return await self._request("GET", f"/{table}/{doc_id}")
        resp = await self._request(
            "POST", f"/{table}/_find", json={"selector": filters, "limit": 1}
        )
        if resp and resp.get("docs"):
            return resp["docs"][0]
        return None

    async def update(
        self, table: str, filters: Dict[str, Any], values: Dict[str, Any]
    ) -> int:
        doc_id = filters.get("_id")
        if doc_id:
            existing = await self._request("GET", f"/{table}/{doc_id}")
            if existing:
                values["_id"] = doc_id
                values["_rev"] = existing["_rev"]
                await self._request("PUT", f"/{table}/{doc_id}", json=values)
                return 1
        resp = await self._request(
            "POST", f"/{table}/_find", json={"selector": filters}
        )
        docs = resp.get("docs", []) if resp else []
        count = 0
        for doc in docs:
            doc.update(values)
            await self._request("PUT", f"/{table}/{doc['_id']}", json=doc)
            count += 1
        return count

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        docs = []
        for record in updates:
            doc_id = record.get("_id") or record.get(key_columns[0])
            if not doc_id:
                continue
            existing = await self._request("GET", f"/{table}/{doc_id}")
            if existing:
                record["_id"] = doc_id
                record["_rev"] = existing["_rev"]
                docs.append(record)
        if docs:
            await self._request("POST", f"/{table}/_bulk_docs", json={"docs": docs})
        return len(docs)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[CouchDBConnector]:
        yield self
