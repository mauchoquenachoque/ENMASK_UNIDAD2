from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional

import aioboto3

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class DynamoDBConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._session: Any = None
        self._client: Any = None
        self._region = kwargs.get("region") or self.extra_options.get("region", "us-east-1")

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.DYNAMODB

    async def _do_connect(self) -> None:
        self._session = aioboto3.Session()
        self._client = await self._session.client(
            "dynamodb",
            region_name=self._region,
            aws_access_key_id=self.username or None,
            aws_secret_access_key=self.password or None,
            endpoint_url=self.extra_options.get("endpoint_url"),
        ).__aenter__()

    async def _do_disconnect(self) -> None:
        if self._client:
            await self._client.__aexit__(None, None, None)

    async def _do_health_check(self) -> None:
        await self._client.list_tables(Limit=1)

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Use table-specific methods for DynamoDB")

    async def get_schema(self) -> Dict[str, List[str]]:
        schema: Dict[str, List[str]] = {}
        last_evaluated = None
        while True:
            kwargs: Dict[str, Any] = {"Limit": 100}
            if last_evaluated:
                kwargs["ExclusiveStartTableName"] = last_evaluated
            resp = await self._client.list_tables(**kwargs)
            for table_name in resp.get("TableNames", []):
                desc = await self._client.describe_table(TableName=table_name)
                attrs = desc["Table"].get("AttributeDefinitions", [])
                schema[table_name] = [a["AttributeName"] for a in attrs]
            last_evaluated = resp.get("LastEvaluatedTableName")
            if not last_evaluated:
                break
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        desc = await self._client.describe_table(TableName=table)
        key_schema = desc["Table"]["KeySchema"]
        return [k["AttributeName"] for k in key_schema]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        return await self.fetch_all(table, limit=limit)

    async def count_records(self, table: str) -> int:
        desc = await self._client.describe_table(TableName=table)
        return desc["Table"]["ItemCount"]

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {"TableName": table}
        if limit is not None:
            kwargs["Limit"] = limit
        if filters:
            expr_parts = []
            expr_values = {}
            expr_names = {}
            for idx, (key, val) in enumerate(filters.items()):
                alias = f"#f{idx}"
                placeholder = f":v{idx}"
                expr_parts.append(f"{alias} = {placeholder}")
                expr_names[alias] = key
                expr_values[placeholder] = self._to_dynamo_value(val)
            kwargs["FilterExpression"] = " AND ".join(expr_parts)
            kwargs["ExpressionAttributeNames"] = expr_names
            kwargs["ExpressionAttributeValues"] = expr_values
        items: List[Dict[str, Any]] = []
        while True:
            resp = await self._client.scan(**kwargs)
            items.extend(resp.get("Items", []))
            last_key = resp.get("LastEvaluatedKey")
            if not last_key or (limit and len(items) >= limit):
                break
            kwargs["ExclusiveStartKey"] = last_key
        if limit:
            items = items[:limit]
        return [self._from_dynamo_item(item) for item in items]

    async def fetch_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        key = {k: self._to_dynamo_value(v) for k, v in filters.items()}
        resp = await self._client.get_item(TableName=table, Key=key)
        item = resp.get("Item")
        return self._from_dynamo_item(item) if item else None

    async def update(
        self, table: str, filters: Dict[str, Any], values: Dict[str, Any]
    ) -> int:
        key = {k: self._to_dynamo_value(v) for k, v in filters.items()}
        expr_parts = []
        expr_values = {}
        expr_names = {}
        for idx, (k, v) in enumerate(values.items()):
            alias = f"#u{idx}"
            placeholder = f":u{idx}"
            expr_parts.append(f"{alias} = {placeholder}")
            expr_names[alias] = k
            expr_values[placeholder] = self._to_dynamo_value(v)
        await self._client.update_item(
            TableName=table,
            Key=key,
            UpdateExpression="SET " + ", ".join(expr_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
        )
        return 1

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        total = 0
        for i in range(0, len(updates), 25):
            batch = updates[i: i + 25]
            write_requests = []
            for record in batch:
                key = {k: self._to_dynamo_value(record[k]) for k in key_columns if k in record}
                vals = {k: v for k, v in record.items() if k not in key_columns}
                expr_parts = []
                expr_values = {}
                expr_names = {}
                for idx, (k, v) in enumerate(vals.items()):
                    alias = f"#u{idx}"
                    placeholder = f":u{idx}"
                    expr_parts.append(f"{alias} = {placeholder}")
                    expr_names[alias] = k
                    expr_values[placeholder] = self._to_dynamo_value(v)
                write_requests.append({
                    "Update": {
                        "Key": key,
                        "UpdateExpression": "SET " + ", ".join(expr_parts),
                        "ExpressionAttributeNames": expr_names,
                        "ExpressionAttributeValues": expr_values,
                    }
                })
            await self._client.transact_write_items(
                TransactItems=[{"TableName": table, **req} for req in write_requests]
            )
            total += len(batch)
        return total

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[DynamoDBConnector]:
        yield self

    @staticmethod
    def _to_dynamo_value(val: Any) -> Any:
        if isinstance(val, bool):
            return {"BOOL": val}
        if isinstance(val, int):
            return {"N": str(val)}
        if isinstance(val, float):
            return {"N": str(val)}
        if isinstance(val, list):
            return {"L": [DynamoDBConnector._to_dynamo_value(v) for v in val]}
        if isinstance(val, dict):
            return {"M": {k: DynamoDBConnector._to_dynamo_value(v) for k, v in val.items()}}
        if val is None:
            return {"NULL": True}
        return {"S": str(val)}

    @staticmethod
    def _from_dynamo_item(item: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for key, val in item.items():
            if "S" in val:
                result[key] = val["S"]
            elif "N" in val:
                num = val["N"]
                result[key] = int(num) if "." not in num else float(num)
            elif "BOOL" in val:
                result[key] = val["BOOL"]
            elif "NULL" in val:
                result[key] = None
            elif "L" in val:
                result[key] = [DynamoDBConnector._from_dynamo_value(v) for v in val["L"]]
            elif "M" in val:
                result[key] = DynamoDBConnector._from_dynamo_item(val["M"])
        return result

    @staticmethod
    def _from_dynamo_value(val: Any) -> Any:
        if isinstance(val, dict):
            return DynamoDBConnector._from_dynamo_item({"_": val})["_"]
        return val
