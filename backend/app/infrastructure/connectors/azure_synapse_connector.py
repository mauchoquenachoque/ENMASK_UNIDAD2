from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import aioodbc

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.sqlserver_connector import SQLServerConnector


class AzureSynapseConnector(SQLServerConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.AZURE_SYNAPSE

    def _build_conn_str(self) -> str:
        parts = [
            "DRIVER={ODBC Driver 18 for SQL Server}",
            f"SERVER={self.host},{self.port}",
            f"DATABASE={self.database}",
            f"UID={self.username}",
            f"PWD={self.password}",
            "Encrypt=yes",
            "TrustServerCertificate=no",
        ]
        return ";".join(parts)

    async def get_schema(self) -> Dict[str, List[str]]:
        query = """
            SELECT t.name AS table_name, c.name AS column_name
            FROM sys.tables t
            JOIN sys.columns c ON t.object_id = c.object_id
            ORDER BY t.name, c.column_id
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
            SELECT c.name AS column_name
            FROM sys.indexes i
            JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            JOIN sys.tables t ON i.object_id = t.object_id
            WHERE i.is_primary_key = 1 AND t.name = ?
        """
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, [table])
                rows = await cur.fetchall()
        return [row[0] for row in rows]
