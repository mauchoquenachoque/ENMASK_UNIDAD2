from __future__ import annotations

import re
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import redis.asyncio as aioredis

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class RedisConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._client: Optional[aioredis.Redis] = None
        self._pipe: Any = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.REDIS

    async def _do_connect(self) -> None:
        self._client = aioredis.Redis(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            db=int(self.database) if self.database.isdigit() else 0,
            ssl=self.ssl,
            socket_timeout=self.query_timeout,
            max_connections=self.pool_max_size,
            decode_responses=True,
        )

    async def _do_disconnect(self) -> None:
        if self._client:
            await self._client.aclose()

    async def _do_health_check(self) -> None:
        await self._client.ping()

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Use type-specific methods for Redis")

    async def get_schema(self) -> Dict[str, List[str]]:
        schema: Dict[str, List[str]] = {}
        cursor = 0
        while True:
            cursor, keys = await self._client.scan(cursor, count=100)
            for key in keys:
                key_type = await self._client.type(key)
                pattern = self._extract_pattern(key)
                if pattern not in schema:
                    schema[pattern] = []
                if key_type == "hash":
                    fields = await self._client.hkeys(key)
                    for f in fields:
                        if f not in schema[pattern]:
                            schema[pattern].append(f)
                elif key_type == "string":
                    if "value" not in schema[pattern]:
                        schema[pattern].append("value")
                elif key_type == "list":
                    if "element" not in schema[pattern]:
                        schema[pattern].append("element")
                elif key_type in ("set", "zset"):
                    if "member" not in schema[pattern]:
                        schema[pattern].append("member")
                    if key_type == "zset" and "score" not in schema[pattern]:
                        schema[pattern].append("score")
            if cursor == 0:
                break
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        return ["key"]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        return await self.fetch_all(table, limit=limit)

    async def count_records(self, table: str) -> int:
        keys = await self.scan_keys(table)
        return len(keys)

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        pattern = filters.get("pattern", table) if filters else table
        results: List[Dict[str, Any]] = []
        cursor = 0
        count = limit or 100
        while True:
            cursor, keys = await self._client.scan(cursor, match=pattern, count=count)
            for key in keys:
                item = await self._read_key(key)
                if item:
                    results.append(item)
                if limit and len(results) >= limit:
                    return results
            if cursor == 0:
                break
        return results

    async def fetch_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        key = filters.get("key") or table
        return await self._read_key(key)

    async def update(
        self, table: str, filters: Dict[str, Any], values: Dict[str, Any]
    ) -> int:
        key = filters.get("key") or table
        key_type = await self._client.type(key)
        if key_type == "hash":
            await self._client.hset(key, mapping=values)
        elif key_type == "string" and "value" in values:
            await self._client.set(key, values["value"])
        return 1

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        pipe = self._client.pipeline()
        for record in updates:
            key = record.get("key") or record.get(key_columns[0])
            if not key:
                continue
            key_type = await self._client.type(key)
            vals = {k: v for k, v in record.items() if k != "key" and k not in key_columns}
            if key_type == "hash" and vals:
                pipe.hset(key, mapping=vals)
            elif key_type == "string" and "value" in vals:
                pipe.set(key, vals["value"])
        await pipe.execute()
        return len(updates)

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[RedisConnector]:
        pipe = self._client.pipeline(transaction=True)
        self._pipe = pipe
        try:
            yield self
            await pipe.execute()
        except Exception:
            await pipe.reset()
            raise
        finally:
            self._pipe = None

    async def scan_keys(self, pattern: str = "*", count: int = 100) -> List[str]:
        all_keys: List[str] = []
        cursor = 0
        while True:
            cursor, keys = await self._client.scan(cursor, match=pattern, count=count)
            all_keys.extend(keys)
            if cursor == 0:
                break
        return all_keys

    async def _read_key(self, key: str) -> Optional[Dict[str, Any]]:
        key_type = await self._client.type(key)
        result: Dict[str, Any] = {"key": key, "type": key_type}
        if key_type == "string":
            result["value"] = await self._client.get(key)
        elif key_type == "hash":
            result.update(await self._client.hgetall(key))
        elif key_type == "list":
            result["elements"] = await self._client.lrange(key, 0, -1)
        elif key_type == "set":
            result["members"] = list(await self._client.smembers(key))
        elif key_type == "zset":
            result["members"] = await self._client.zrange(key, 0, -1, withscores=True)
        else:
            return None
        return result

    @staticmethod
    def _extract_pattern(key: str) -> str:
        return re.sub(r":[^:]+$", ":*", key) if ":" in key else key
