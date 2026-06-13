from __future__ import annotations

import ssl as ssl_mod
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import asyncpg

from app.core.exceptions import ConnectionError as EnmaskConnectionError
from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class PostgresConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._conn: Optional[asyncpg.Connection] = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.POSTGRES

    async def _do_connect(self) -> None:
        ssl_ctx: Optional[ssl_mod.SSLContext] = None
        if self.ssl:
            ssl_ctx = ssl_mod.create_default_context()
        self._pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.username,
            password=self.password,
            ssl=ssl_ctx,
            min_size=self.pool_min_size,
            max_size=self.pool_max_size,
            command_timeout=self.query_timeout,
        )

    async def _do_disconnect(self) -> None:
        if self._pool:
            await self._pool.close()

    async def _do_health_check(self) -> None:
        async with self._pool.acquire() as conn:
            await conn.fetchval("SELECT 1")

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        async with self._pool.acquire() as conn:
            if params:
                columns = list(params.keys())
                positional_query = query
                for idx, col in enumerate(columns, 1):
                    positional_query = positional_query.replace(f":{col}", f"${idx}")
                return await conn.fetch(positional_query, *[params[c] for c in columns])
            return await conn.fetch(query)

    async def get_schema(self) -> Dict[str, List[str]]:
        query = """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """
        rows = await self.execute(query)
        schema: Dict[str, List[str]] = {}
        for row in rows:
            table = row["table_name"]
            col = row["column_name"]
            schema.setdefault(table, []).append(col)
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        query = """
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = 'public'
                AND tc.table_name = $1
            ORDER BY kcu.ordinal_position
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, table)
        return [row["column_name"] for row in rows]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f'SELECT * FROM "{table}" LIMIT $1 OFFSET $2', limit, offset
            )
        return [dict(r) for r in rows]

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        query = f'SELECT * FROM "{table}"'
        params: List[Any] = []
        if filters:
            conditions = []
            for idx, (col, val) in enumerate(filters.items(), 1):
                self._validate_identifier(col)
                conditions.append(f'"{col}" = ${idx}')
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        return [dict(r) for r in rows]

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
        idx = 1
        for col, val in values.items():
            self._validate_identifier(col)
            set_parts.append(f'"{col}" = ${idx}')
            params.append(val)
            idx += 1
        where_parts = []
        for col, val in filters.items():
            self._validate_identifier(col)
            where_parts.append(f'"{col}" = ${idx}')
            params.append(val)
            idx += 1
        query = f'UPDATE "{table}" SET {", ".join(set_parts)} WHERE {" AND ".join(where_parts)}'
        async with self._pool.acquire() as conn:
            result = await conn.execute(query, *params)
        return int(result.split()[-1])

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        total = 0
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                for record in updates:
                    filters = {k: record[k] for k in key_columns if k in record}
                    values = {k: v for k, v in record.items() if k not in key_columns}
                    if not values:
                        continue
                    set_parts = []
                    params: List[Any] = []
                    idx = 1
                    for col, val in values.items():
                        self._validate_identifier(col)
                        set_parts.append(f'"{col}" = ${idx}')
                        params.append(val)
                        idx += 1
                    where_parts = []
                    for col, val in filters.items():
                        self._validate_identifier(col)
                        where_parts.append(f'"{col}" = ${idx}')
                        params.append(val)
                        idx += 1
                    query = (
                        f'UPDATE "{table}" SET {", ".join(set_parts)} '
                        f'WHERE {" AND ".join(where_parts)}'
                    )
                    result = await conn.execute(query, *params)
                    total += int(result.split()[-1])
        return total

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[PostgresConnector]:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                old_conn = self._conn
                self._conn = conn
                try:
                    yield self
                finally:
                    self._conn = old_conn
