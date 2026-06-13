from __future__ import annotations

import ssl as ssl_mod
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import aiomysql

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class MySQLConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._conn: Optional[aiomysql.Connection] = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.MYSQL

    async def _do_connect(self) -> None:
        ssl_ctx: Optional[ssl_mod.SSLContext] = None
        if self.ssl:
            ssl_ctx = ssl_mod.create_default_context()
        self._pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            db=self.database,
            user=self.username,
            password=self.password,
            ssl=ssl_ctx,
            minsize=self.pool_min_size,
            maxsize=self.pool_max_size,
            autocommit=True,
        )

    async def _do_disconnect(self) -> None:
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()

    async def _do_health_check(self) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if params:
                    formatted = query
                    values = []
                    for col, val in params.items():
                        formatted = formatted.replace(f":{col}", "%s")
                        values.append(val)
                    await cur.execute(formatted, values)
                else:
                    await cur.execute(query)
                if cur.description:
                    return await cur.fetchall()
                return cur.rowcount

    async def get_schema(self) -> Dict[str, List[str]]:
        query = """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
            ORDER BY table_name, ordinal_position
        """
        rows = await self.execute(query)
        schema: Dict[str, List[str]] = {}
        for row in rows:
            table = row["TABLE_NAME"]
            col = row["COLUMN_NAME"]
            schema.setdefault(table, []).append(col)
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        query = """
            SELECT column_name
            FROM information_schema.key_column_usage
            WHERE table_schema = DATABASE()
                AND table_name = %s
                AND constraint_name = 'PRIMARY'
            ORDER BY ordinal_position
        """
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, [table])
                rows = await cur.fetchall()
        return [row["column_name"] for row in rows]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(f"SELECT * FROM `{table}` LIMIT %s OFFSET %s", [limit, offset])
                return await cur.fetchall()

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        query = f"SELECT * FROM `{table}`"
        params: List[Any] = []
        if filters:
            conditions = []
            for col, val in filters.items():
                self._validate_identifier(col)
                conditions.append(f"`{col}` = %s")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchall()

    async def fetch_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        results = await self.fetch_all(table, filters, limit=1)
        return results[0] if results else None

    async def update(
        self, table: str, filters: Dict[str, Any], values: Dict[str, Any]
    ) -> int:
        self._validate_identifier(table)
        set_parts = []
        params: List[Any] = []
        for col, val in values.items():
            self._validate_identifier(col)
            set_parts.append(f"`{col}` = %s")
            params.append(val)
        where_parts = []
        for col, val in filters.items():
            self._validate_identifier(col)
            where_parts.append(f"`{col}` = %s")
            params.append(val)
        query = f"UPDATE `{table}` SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return cur.rowcount

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        total = 0
        async with self._pool.acquire() as conn:
            await conn.begin()
            try:
                async with conn.cursor() as cur:
                    for record in updates:
                        filters = {k: record[k] for k in key_columns if k in record}
                        vals = {k: v for k, v in record.items() if k not in key_columns}
                        if not vals:
                            continue
                        set_parts = []
                        params: List[Any] = []
                        for col, val in vals.items():
                            self._validate_identifier(col)
                            set_parts.append(f"`{col}` = %s")
                            params.append(val)
                        where_parts = []
                        for col, val in filters.items():
                            self._validate_identifier(col)
                            where_parts.append(f"`{col}` = %s")
                            params.append(val)
                        q = (
                            f"UPDATE `{table}` SET {', '.join(set_parts)} "
                            f"WHERE {' AND '.join(where_parts)}"
                        )
                        await cur.execute(q, params)
                        total += cur.rowcount
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise
        return total

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[MySQLConnector]:
        async with self._pool.acquire() as conn:
            await conn.begin()
            old_conn = self._conn
            self._conn = conn
            try:
                yield self
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise
            finally:
                self._conn = old_conn
