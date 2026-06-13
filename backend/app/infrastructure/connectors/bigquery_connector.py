from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

from google.cloud import bigquery
from google.oauth2 import service_account

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class BigQueryConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._client: Optional[bigquery.Client] = None
        self._project = kwargs.get("project") or self.extra_options.get("project") or self.host
        self._location = kwargs.get("location") or self.extra_options.get("location", "US")

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.BIGQUERY

    async def _do_connect(self) -> None:
        credentials = None
        creds_path = self.extra_options.get("credentials_path")
        if creds_path:
            credentials = service_account.Credentials.from_service_account_file(creds_path)
        self._client = await asyncio.to_thread(
            bigquery.Client, project=self._project, credentials=credentials, location=self._location
        )

    async def _do_disconnect(self) -> None:
        if self._client:
            await asyncio.to_thread(self._client.close)

    async def _do_health_check(self) -> None:
        await asyncio.to_thread(list, self._client.list_datasets(max_results=1))

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        job_config = bigquery.QueryJobConfig()
        if params:
            from google.cloud.bigquery import ScalarQueryParameter
            query_params = [ScalarQueryParameter(k, "STRING", str(v)) for k, v in params.items()]
            job_config.query_parameters = query_params
        results = await asyncio.to_thread(self._client.query, query, job_config=job_config)
        rows = await asyncio.to_thread(results.result)
        return [dict(row) for row in rows]

    async def get_schema(self) -> Dict[str, List[str]]:
        schema: Dict[str, List[str]] = {}
        datasets = await asyncio.to_thread(list, self._client.list_datasets())
        for dataset in datasets:
            dataset_id = dataset.dataset_id
            tables = await asyncio.to_thread(list, self._client.list_tables(dataset_id))
            for table in tables:
                full_name = f"{dataset_id}.{table.table_id}"
                table_ref = await asyncio.to_thread(self._client.get_table, full_name)
                schema[full_name] = [field.name for field in table_ref.schema]
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        return []

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM `{self._project}.{table}` LIMIT {int(limit)} OFFSET {int(offset)}"
        return await self.execute(query)

    async def count_records(self, table: str) -> int:
        rows = await self.execute(f"SELECT COUNT(*) AS cnt FROM `{self._project}.{table}`")
        return rows[0]["cnt"] if rows else 0

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM `{self._project}.{table}`"
        params: Dict[str, Any] = {}
        if filters:
            conditions = []
            for col, val in filters.items():
                conditions.append(f"`{col}` = @{col}")
                params[col] = str(val)
            query += " WHERE " + " AND ".join(conditions)
        if limit is not None:
            query += f" LIMIT {int(limit)}"
        job_config = bigquery.QueryJobConfig()
        if params:
            from google.cloud.bigquery import ScalarQueryParameter
            job_config.query_parameters = [
                ScalarQueryParameter(k, "STRING", v) for k, v in params.items()
            ]
        results = await asyncio.to_thread(self._client.query, query, job_config=job_config)
        rows = await asyncio.to_thread(results.result)
        return [dict(row) for row in rows]

    async def fetch_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        results = await self.fetch_all(table, filters, limit=1)
        return results[0] if results else None

    async def update(
        self, table: str, filters: Dict[str, Any], values: Dict[str, Any]
    ) -> int:
        from google.cloud.bigquery import ScalarQueryParameter
        set_parts = []
        where_parts = []
        query_params = []
        for col, val in values.items():
            set_parts.append(f"`{col}` = @s_{col}")
            query_params.append(ScalarQueryParameter(f"s_{col}", "STRING", str(val)))
        for col, val in filters.items():
            where_parts.append(f"`{col}` = @w_{col}")
            query_params.append(ScalarQueryParameter(f"w_{col}", "STRING", str(val)))
        query = f"UPDATE `{self._project}.{table}` SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        results = await asyncio.to_thread(self._client.query, query, job_config=job_config)
        await asyncio.to_thread(results.result)
        return results.num_dml_affected_rows or 0

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
    async def transaction(self) -> AsyncIterator[BigQueryConnector]:
        yield self
