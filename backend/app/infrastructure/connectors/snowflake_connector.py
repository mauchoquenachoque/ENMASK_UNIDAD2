from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import snowflake.connector
from snowflake.connector import DictCursor

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class SnowflakeConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._conn: Any = None
        self._warehouse = kwargs.get("warehouse") or self.extra_options.get("warehouse")
        self._schema = kwargs.get("schema") or self.extra_options.get("schema", "PUBLIC")
        self._role = kwargs.get("role") or self.extra_options.get("role")

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.SNOWFLAKE

    async def _do_connect(self) -> None:
        kwargs: Dict[str, Any] = {
            "user": self.username,
            "password": self.password,
            "account": self.host,
            "database": self.database,
            "schema": self._schema,
        }
        if self._warehouse:
            kwargs["warehouse"] = self._warehouse
        if self._role:
            kwargs["role"] = self._role
        self._conn = await asyncio.to_thread(snowflake.connector.connect, **kwargs)

    async def _do_disconnect(self) -> None:
        if self._conn:
            await asyncio.to_thread(self._conn.close)

    async def _do_health_check(self) -> None:
        cursor = await asyncio.to_thread(self._conn.cursor, DictCursor)
        await asyncio.to_thread(cursor.execute, "SELECT 1")
        await asyncio.to_thread(cursor.fetchall)
        await asyncio.to_thread(cursor.close)

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        cursor = await asyncio.to_thread(self._conn.cursor, DictCursor)
        if params:
            formatted = query
            values = []
            for col, val in params.items():
                formatted = formatted.replace(f":{col}", "%s")
                values.append(val)
            await asyncio.to_thread(cursor.execute, formatted, values)
        else:
            await asyncio.to_thread(cursor.execute, query)
        if cursor.description:
            return await asyncio.to_thread(cursor.fetchall)
        await asyncio.to_thread(self._conn.commit)
        return cursor.rowcount

    async def get_schema(self) -> Dict[str, List[str]]:
        query = """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = %s
            ORDER BY table_name, ordinal_position
        """
        cursor = await asyncio.to_thread(self._conn.cursor, DictCursor)
        await asyncio.to_thread(cursor.execute, query, [self._schema])
        rows = await asyncio.to_thread(cursor.fetchall)
        await asyncio.to_thread(cursor.close)
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
            WHERE table_schema = %s
                AND table_name = %s
                AND constraint_name IN (
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE constraint_type = 'PRIMARY KEY'
                        AND table_schema = %s
                        AND table_name = %s
                )
            ORDER BY ordinal_position
        """
        cursor = await asyncio.to_thread(self._conn.cursor, DictCursor)
        await asyncio.to_thread(
            cursor.execute, query, [self._schema, table, self._schema, table]
        )
        rows = await asyncio.to_thread(cursor.fetchall)
        await asyncio.to_thread(cursor.close)
        return [row["COLUMN_NAME"] for row in rows]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        cursor = await asyncio.to_thread(self._conn.cursor, DictCursor)
        await asyncio.to_thread(
            cursor.execute,
            f'SELECT * FROM "{table}" LIMIT %s OFFSET %s',
            [limit, offset],
        )
        rows = await asyncio.to_thread(cursor.fetchall)
        await asyncio.to_thread(cursor.close)
        return rows

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
                conditions.append(f'"{col}" = %s')
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        cursor = await asyncio.to_thread(self._conn.cursor, DictCursor)
        await asyncio.to_thread(cursor.execute, query, params)
        rows = await asyncio.to_thread(cursor.fetchall)
        await asyncio.to_thread(cursor.close)
        return rows

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
            set_parts.append(f'"{col}" = %s')
            params.append(val)
        where_parts = []
        for col, val in filters.items():
            self._validate_identifier(col)
            where_parts.append(f'"{col}" = %s')
            params.append(val)
        query = f'UPDATE "{table}" SET {", ".join(set_parts)} WHERE {" AND ".join(where_parts)}'
        cursor = await asyncio.to_thread(self._conn.cursor)
        await asyncio.to_thread(cursor.execute, query, params)
        count = cursor.rowcount
        await asyncio.to_thread(self._conn.commit)
        await asyncio.to_thread(cursor.close)
        return count

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        total = 0
        for record in updates:
            filters = {k: record[k] for k in key_columns if k in record}
            vals = {k: v for k, v in record.items() if k not in key_columns}
            if vals:
                total += await self.update(table, filters, vals)
        return total

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[SnowflakeConnector]:
        await asyncio.to_thread(self._conn.autocommit, False)
        try:
            yield self
            await asyncio.to_thread(self._conn.commit)
        except Exception:
            await asyncio.to_thread(self._conn.rollback)
            raise
        finally:
            await asyncio.to_thread(self._conn.autocommit, True)
