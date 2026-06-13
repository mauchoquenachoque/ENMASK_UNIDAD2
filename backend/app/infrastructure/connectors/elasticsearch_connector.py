from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

from elasticsearch import AsyncElasticsearch

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class ElasticsearchConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._client: Optional[AsyncElasticsearch] = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.ELASTICSEARCH

    async def _do_connect(self) -> None:
        scheme = "https" if self.ssl else "http"
        url = f"{scheme}://{self.host}:{self.port}"
        kwargs: Dict[str, Any] = {}
        if self.username and self.password:
            kwargs["basic_auth"] = (self.username, self.password)
        self._client = AsyncElasticsearch(url, request_timeout=self.query_timeout, **kwargs)

    async def _do_disconnect(self) -> None:
        if self._client:
            await self._client.close()

    async def _do_health_check(self) -> None:
        await self._client.ping()

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Use index-specific methods for Elasticsearch")

    async def get_schema(self) -> Dict[str, List[str]]:
        indices = await self._client.indices.get(index="*")
        schema: Dict[str, List[str]] = {}
        for index_name, index_data in indices.items():
            if index_name.startswith("."):
                continue
            mappings = index_data.get("mappings", {}).get("properties", {})
            schema[index_name] = list(mappings.keys())
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        return ["_id"]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        resp = await self._client.search(
            index=table, body={"query": {"match_all": {}}, "from": offset, "size": limit}
        )
        return [{**hit["_source"], "_id": hit["_id"]} for hit in resp["hits"]["hits"]]

    async def count_records(self, table: str) -> int:
        resp = await self._client.count(index=table)
        return resp["count"]

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        body: Dict[str, Any] = {"query": filters.get("query", {"match_all": {}}) if filters else {"match_all": {}}}
        if limit is not None:
            body["size"] = limit
        resp = await self._client.search(index=table, body=body)
        return [{**hit["_source"], "_id": hit["_id"]} for hit in resp["hits"]["hits"]]

    async def fetch_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        doc_id = filters.get("_id")
        if doc_id:
            try:
                resp = await self._client.get(index=table, id=doc_id)
                return {**resp["_source"], "_id": resp["_id"]}
            except Exception:
                return None
        results = await self.fetch_all(table, filters, limit=1)
        return results[0] if results else None

    async def update(
        self, table: str, filters: Dict[str, Any], values: Dict[str, Any]
    ) -> int:
        doc_id = filters.get("_id")
        if doc_id:
            await self._client.update(index=table, id=doc_id, body={"doc": values})
            return 1
        query = filters.get("query", {"match_all": {}})
        body = {
            "query": query,
            "script": {
                "source": "; ".join([f"ctx._source.{k} = params.{k}" for k in values]),
                "params": values,
            },
        }
        resp = await self._client.update_by_query(index=table, body=body)
        return resp.get("updated", 0)

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        actions = []
        for record in updates:
            doc_id = record.get("_id")
            if not doc_id:
                continue
            doc = {k: v for k, v in record.items() if k != "_id"}
            actions.append({"update": {"_index": table, "_id": doc_id}})
            actions.append({"doc": doc})
        if not actions:
            return 0
        resp = await self._client.bulk(body=actions)
        return sum(1 for item in resp["items"] if item["update"]["status"] == 200)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[ElasticsearchConnector]:
        yield self
