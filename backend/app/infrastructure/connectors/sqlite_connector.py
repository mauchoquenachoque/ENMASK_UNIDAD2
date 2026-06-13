from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import aiosqlite

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class SQLiteConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        kwargs.setdefault("host", "")
        kwargs.setdefault("port", 0)
        super().__init__(**kwargs)
        self._db_path = kwargs.get("db_path") or self.database
        self._conn: Optional[aiosqlite.Connection] = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.SQLITE

    async def _do_connect(self) -> None:
        self._conn = await aiosqlite.connect(self._db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")

    async def _do_disconnect(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def _do_health_check(self) -> None:
        await self._conn.execute("SELECT 1")

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if params:
            formatted = query
            values = []
            for col, val in params.items():
                formatted = formatted.replace(f":{col}", "?")
                values.append(val)
            cursor = await self._conn.execute(formatted, values)
        else:
            cursor = await self._conn.execute(query)
        if cursor.description:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        await self._conn.commit()
        return cursor.rowcount

    async def get_schema(self) -> Dict[str, List[str]]:
        cursor = await self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row["name"] for row in await cursor.fetchall()]
        schema: Dict[str, List[str]] = {}
        for table in tables:
            cursor = await self._conn.execute(f'PRAGMA table_info("{table}")')
            columns = [row["name"] for row in await cursor.fetchall()]
            schema[table] = columns
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        cursor = await self._conn.execute(f'PRAGMA table_info("{table}")')
        rows = await cursor.fetchall()
        return [row["name"] for row in rows if row["pk"] > 0]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        cursor = await self._conn.execute(
            f'SELECT * FROM "{table}" LIMIT ? OFFSET ?', [limit, offset]
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def count_records(self, table: str) -> int:
        self._validate_identifier(table)
        cursor = await self._conn.execute(f'SELECT COUNT(*) AS cnt FROM "{table}"')
        row = await cursor.fetchone()
        return row["cnt"]

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
            for col, val in filters.items():
                self._validate_identifier(col)
                conditions.append(f'"{col}" = ?')
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        cursor = await self._conn.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

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
            set_parts.append(f'"{col}" = ?')
            params.append(val)
        where_parts = []
        for col, val in filters.items():
            self._validate_identifier(col)
            where_parts.append(f'"{col}" = ?')
            params.append(val)
        query = f'UPDATE "{table}" SET {", ".join(set_parts)} WHERE {" AND ".join(where_parts)}'
        cursor = await self._conn.execute(query, params)
        await self._conn.commit()
        return cursor.rowcount

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        total = 0
        try:
            await self._conn.execute("BEGIN")
            for record in updates:
                filters = {k: record[k] for k in key_columns if k in record}
                vals = {k: v for k, v in record.items() if k not in key_columns}
                if not vals:
                    continue
                count = await self.update(table, filters, vals)
                total += count
            await self._conn.execute("COMMIT")
        except Exception:
            await self._conn.execute("ROLLBACK")
            raise
        return total

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[SQLiteConnector]:
        await self._conn.execute("BEGIN")
        try:
            yield self
            await self._conn.execute("COMMIT")
        except Exception:
            await self._conn.execute("ROLLBACK")
            raise
