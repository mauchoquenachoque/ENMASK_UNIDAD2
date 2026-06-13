from __future__ import annotations

import ssl as ssl_mod
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import asyncpg

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.postgres_connector import PostgresConnector


class RedshiftConnector(PostgresConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.REDSHIFT

    async def _do_connect(self) -> None:
        ssl_ctx: Optional[ssl_mod.SSLContext] = None
        if self.ssl:
            ssl_ctx = ssl_mod.create_default_context()
        dsn = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        self._pool = await asyncpg.create_pool(
            dsn,
            ssl=ssl_ctx,
            min_size=self.pool_min_size,
            max_size=self.pool_max_size,
            command_timeout=self.query_timeout,
        )

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
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = $1::regclass AND i.indisprimary
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, table)
        return [row["attname"] for row in rows]
