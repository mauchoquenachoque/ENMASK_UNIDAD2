from __future__ import annotations

import ssl as ssl_mod
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class CassandraConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._session: Any = None
        self._cluster: Any = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.CASSANDRA

    async def _do_connect(self) -> None:
        auth_provider = PlainTextAuthProvider(
            username=self.username, password=self.password
        )
        ssl_context: Optional[ssl_mod.SSLContext] = None
        if self.ssl:
            ssl_context = ssl_mod.create_default_context()
        self._cluster = Cluster(
            contact_points=[self.host],
            port=self.port,
            auth_provider=auth_provider,
            ssl_context=ssl_context,
            load_balancing_policy=DCAwareRoundRobinPolicy(),
        )
        self._session = self._cluster.connect(self.database)

    async def _do_disconnect(self) -> None:
        if self._cluster:
            self._cluster.shutdown()

    async def _do_health_check(self) -> None:
        self._session.execute("SELECT release_version FROM system.local")

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        from cassandra.query import SimpleStatement

        statement = SimpleStatement(query)
        if params:
            rows = self._session.execute(statement, params)
        else:
            rows = self._session.execute(statement)
        if rows.column_names:
            return [dict(row._asdict()) for row in rows]
        return None

    async def get_schema(self) -> Dict[str, List[str]]:
        rows = self._session.execute(
            "SELECT table_name FROM system_schema.tables WHERE keyspace_name = %s",
            [self.database],
        )
        schema: Dict[str, List[str]] = {}
        for row in rows:
            table = row.table_name
            col_rows = self._session.execute(
                "SELECT column_name FROM system_schema.columns "
                "WHERE keyspace_name = %s AND table_name = %s",
                [self.database, table],
            )
            schema[table] = [cr.column_name for cr in col_rows]
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        rows = self._session.execute(
            "SELECT column_name FROM system_schema.columns "
            "WHERE keyspace_name = %s AND table_name = %s AND kind = 'partition_key'",
            [self.database, table],
        )
        return [row.column_name for row in rows]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        query = f'SELECT * FROM "{table}" LIMIT {int(limit)}'
        from cassandra.query import SimpleStatement
        statement = SimpleStatement(query)
        rows = self._session.execute(statement)
        return [dict(row._asdict()) for row in rows]

    async def count_records(self, table: str) -> int:
        self._validate_identifier(table)
        rows = self._session.execute(f'SELECT COUNT(*) FROM "{table}"')
        return rows.one()[0]

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        query = f'SELECT * FROM "{table}"'
        params: Dict[str, Any] = {}
        if filters:
            conditions = []
            for col, val in filters.items():
                self._validate_identifier(col)
                conditions.append(f'"{col}" = %({col})s')
                params[col] = val
            query += " WHERE " + " AND ".join(conditions)
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        from cassandra.query import SimpleStatement
        statement = SimpleStatement(query)
        rows = self._session.execute(statement, params) if params else self._session.execute(statement)
        return [dict(row._asdict()) for row in rows]

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
            set_parts.append(f'"{col}" = %({col})s')
            params[col] = val
        where_parts = []
        for col, val in filters.items():
            key = f"w_{col}"
            self._validate_identifier(col)
            where_parts.append(f'"{col}" = %({key})s')
            params[key] = val
        query = f'UPDATE "{table}" SET {", ".join(set_parts)} WHERE {" AND ".join(where_parts)}'
        self._session.execute(query, params)
        return 1

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        total = 0
        for record in updates:
            filters = {k: record[k] for k in key_columns if k in record}
            vals = {k: v for k, v in record.items() if k not in key_columns}
            if vals:
                await self.update(table, filters, vals)
                total += 1
        return total

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[CassandraConnector]:
        yield self
