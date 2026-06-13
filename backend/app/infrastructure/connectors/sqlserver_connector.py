from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import aioodbc

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class SQLServerConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._conn: Optional[aioodbc.Connection] = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.SQLSERVER

    def _build_conn_str(self) -> str:
        parts = [
            "DRIVER={ODBC Driver 18 for SQL Server}",
            f"SERVER={self.host},{self.port}",
            f"DATABASE={self.database}",
            f"UID={self.username}",
            f"PWD={self.password}",
        ]
        if self.ssl:
            parts.append("Encrypt=yes")
            parts.append("TrustServerCertificate=no")
        else:
            parts.append("Encrypt=no")
        return ";".join(parts)

    async def _do_connect(self) -> None:
        conn_str = self._build_conn_str()
        self._pool = await aioodbc.create_pool(
            conn_str,
            minsize=self.pool_min_size,
            maxsize=self.pool_max_size,
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
            async with conn.cursor() as cur:
                if params:
                    formatted = query
                    values = []
                    for col, val in params.items():
                        formatted = formatted.replace(f":{col}", "?")
                        values.append(val)
                    await cur.execute(formatted, values)
                else:
                    await cur.execute(query)
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    rows = await cur.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                return cur.rowcount

    async def get_schema(self) -> Dict[str, List[str]]:
        query = """
            SELECT TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'dbo'
            ORDER BY TABLE_NAME, ORDINAL_POSITION
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
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'dbo'
                AND TABLE_NAME = ?
                AND CONSTRAINT_NAME IN (
                    SELECT CONSTRAINT_NAME
                    FROM TABLE_CONSTRAINTS
                    WHERE CONSTRAINT_TYPE = 'PRIMARY KEY'
                        AND TABLE_SCHEMA = 'dbo'
                        AND TABLE_NAME = ?
                )
            ORDER BY ORDINAL_POSITION
        """
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, [table, table])
                rows = await cur.fetchall()
        return [row[0] for row in rows]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        query = f"SELECT * FROM [{table}] ORDER BY (SELECT NULL) OFFSET {int(offset)} ROWS FETCH NEXT {int(limit)} ROWS ONLY"
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                if not cur.description:
                    return []
                columns = [desc[0] for desc in cur.description]
                rows = await cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        if limit is not None:
            query = f"SELECT TOP {int(limit)} * FROM [{table}]"
        else:
            query = f"SELECT * FROM [{table}]"
        params: List[Any] = []
        if filters:
            conditions = []
            for col, val in filters.items():
                self._validate_identifier(col)
                conditions.append(f"[{col}] = ?")
                params.append(val)
            query += " WHERE " + " AND ".join(conditions)
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                if not cur.description:
                    return []
                columns = [desc[0] for desc in cur.description]
                rows = await cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]

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
            set_parts.append(f"[{col}] = ?")
            params.append(val)
        where_parts = []
        for col, val in filters.items():
            self._validate_identifier(col)
            where_parts.append(f"[{col}] = ?")
            params.append(val)
        query = f"UPDATE [{table}] SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return cur.rowcount

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        total = 0
        async with self._pool.acquire() as conn:
            await conn.autocommit(False)
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
                            set_parts.append(f"[{col}] = ?")
                            params.append(val)
                        where_parts = []
                        for col, val in filters.items():
                            self._validate_identifier(col)
                            where_parts.append(f"[{col}] = ?")
                            params.append(val)
                        q = (
                            f"UPDATE [{table}] SET {', '.join(set_parts)} "
                            f"WHERE {' AND '.join(where_parts)}"
                        )
                        await cur.execute(q, params)
                        total += cur.rowcount
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise
            finally:
                await conn.autocommit(True)
        return total

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[SQLServerConnector]:
        async with self._pool.acquire() as conn:
            await conn.autocommit(False)
            old_conn = self._conn
            self._conn = conn
            try:
                yield self
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise
            finally:
                await conn.autocommit(True)
                self._conn = old_conn
