from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import oracledb

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class OracleConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._conn: Optional[oracledb.AsyncConnection] = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.ORACLE

    async def _do_connect(self) -> None:
        self._pool = await oracledb.create_pool_async(
            user=self.username,
            password=self.password,
            dsn=f"{self.host}:{self.port}/{self.database}",
            min=self.pool_min_size,
            max=self.pool_max_size,
        )

    async def _do_disconnect(self) -> None:
        if self._pool:
            await self._pool.close()

    async def _do_health_check(self) -> None:
        conn = await self._pool.acquire()
        try:
            cursor = conn.cursor()
            await cursor.execute("SELECT 1 FROM DUAL")
            await cursor.close()
        finally:
            await self._pool.release(conn)

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        conn = await self._pool.acquire()
        try:
            cursor = conn.cursor()
            if params:
                await cursor.execute(query, params)
            else:
                await cursor.execute(query)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = await cursor.fetchall()
                rows = [self._convert_lob(row) for row in rows]
                return [dict(zip(columns, row)) for row in rows]
            await conn.commit()
            return cursor.rowcount
        finally:
            await self._pool.release(conn)

    async def get_schema(self) -> Dict[str, List[str]]:
        query = """
            SELECT table_name, column_name
            FROM user_tab_columns
            ORDER BY table_name, column_id
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
            SELECT cols.column_name
            FROM all_constraints cons
            JOIN all_cons_columns cols
                ON cons.constraint_name = cols.constraint_name
                AND cons.owner = cols.owner
            WHERE cons.constraint_type = 'P'
                AND cons.table_name = :table_name
                AND cons.owner = USER
            ORDER BY cols.position
        """
        conn = await self._pool.acquire()
        try:
            cursor = conn.cursor()
            await cursor.execute(query, {"table_name": table.upper()})
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            await self._pool.release(conn)

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        query = (
            f'SELECT * FROM (SELECT t.*, ROW_NUMBER() OVER (ORDER BY ROWID) AS rn '
            f'FROM "{table}" t) WHERE rn > :offset AND rn <= :endrow'
        )
        conn = await self._pool.acquire()
        try:
            cursor = conn.cursor()
            await cursor.execute(query, {"offset": offset, "endrow": offset + limit})
            if not cursor.description:
                return []
            columns = [desc[0] for desc in cursor.description]
            rows = await cursor.fetchall()
            rows = [self._convert_lob(row) for row in rows]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            await self._pool.release(conn)

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        params: Dict[str, Any] = {}
        if filters:
            conditions = []
            for col, val in filters.items():
                self._validate_identifier(col)
                param_name = f"f_{col}"
                conditions.append(f'"{col}" = :{param_name}')
                params[param_name] = val
            where_clause = " AND ".join(conditions)
            if limit is not None:
                query = f'SELECT * FROM (SELECT * FROM "{table}" WHERE {where_clause}) WHERE ROWNUM <= :_limit'
                params["_limit"] = limit
            else:
                query = f'SELECT * FROM "{table}" WHERE {where_clause}'
        else:
            if limit is not None:
                query = f'SELECT * FROM "{table}" WHERE ROWNUM <= :_limit'
                params["_limit"] = limit
            else:
                query = f'SELECT * FROM "{table}"'
        conn = await self._pool.acquire()
        try:
            cursor = conn.cursor()
            await cursor.execute(query, params)
            if not cursor.description:
                return []
            columns = [desc[0] for desc in cursor.description]
            rows = await cursor.fetchall()
            rows = [self._convert_lob(row) for row in rows]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            await self._pool.release(conn)

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
        params: Dict[str, Any] = {}
        for col, val in values.items():
            self._validate_identifier(col)
            param_name = f"s_{col}"
            set_parts.append(f'"{col}" = :{param_name}')
            params[param_name] = val
        where_parts = []
        for col, val in filters.items():
            self._validate_identifier(col)
            param_name = f"w_{col}"
            where_parts.append(f'"{col}" = :{param_name}')
            params[param_name] = val
        query = f'UPDATE "{table}" SET {", ".join(set_parts)} WHERE {" AND ".join(where_parts)}'
        conn = await self._pool.acquire()
        try:
            cursor = conn.cursor()
            await cursor.execute(query, params)
            await conn.commit()
            return cursor.rowcount
        finally:
            await self._pool.release(conn)

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        total = 0
        conn = await self._pool.acquire()
        try:
            for record in updates:
                filters = {k: record[k] for k in key_columns if k in record}
                vals = {k: v for k, v in record.items() if k not in key_columns}
                if not vals:
                    continue
                set_parts = []
                params: Dict[str, Any] = {}
                for col, val in vals.items():
                    self._validate_identifier(col)
                    p = f"s_{col}"
                    set_parts.append(f'"{col}" = :{p}')
                    params[p] = val
                where_parts = []
                for col, val in filters.items():
                    self._validate_identifier(col)
                    p = f"w_{col}"
                    where_parts.append(f'"{col}" = :{p}')
                    params[p] = val
                q = (
                    f'UPDATE "{table}" SET {", ".join(set_parts)} '
                    f'WHERE {" AND ".join(where_parts)}'
                )
                cursor = conn.cursor()
                await cursor.execute(q, params)
                total += cursor.rowcount
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await self._pool.release(conn)
        return total

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[OracleConnector]:
        conn = await self._pool.acquire()
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
            await self._pool.release(conn)

    @staticmethod
    def _convert_lob(row: tuple) -> tuple:
        converted = []
        for val in row:
            if isinstance(val, oracledb.LOB):
                converted.append(val.read())
            else:
                converted.append(val)
        return tuple(converted)
