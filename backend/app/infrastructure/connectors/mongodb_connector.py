from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional
from urllib.parse import quote_plus

import motor.motor_asyncio
from bson import ObjectId

from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.connectors.base import BaseConnector


class MongoDBConnector(BaseConnector):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._db: Any = None

    def get_database_type(self) -> DatabaseType:
        return DatabaseType.MONGODB

    def _build_uri(self) -> str:
        enc_user = quote_plus(self.username)
        enc_pass = quote_plus(self.password)
        host = self.host.strip()
        if host.startswith("mongodb+srv://") or host.startswith("mongodb://"):
            scheme, endpoint = host.split("://", 1)
            return f"{scheme}://{enc_user}:{enc_pass}@{endpoint}"
        if host.endswith(".mongodb.net"):
            return f"mongodb+srv://{enc_user}:{enc_pass}@{host}"
        if ":" in host:
            return f"mongodb://{enc_user}:{enc_pass}@{host}"
        return f"mongodb://{enc_user}:{enc_pass}@{host}:{self.port}"

    async def _do_connect(self) -> None:
        uri = self._build_uri()
        kwargs: Dict[str, Any] = {}
        if self.ssl:
            kwargs["tls"] = True
        self._pool = motor.motor_asyncio.AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=int(self.query_timeout * 1000),
            minPoolSize=self.pool_min_size,
            maxPoolSize=self.pool_max_size,
            **kwargs,
        )
        self._db = self._pool[self.database]

    async def _do_disconnect(self) -> None:
        if self._pool:
            self._pool.close()

    async def _do_health_check(self) -> None:
        await self._db.command("ping")

    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Use collection-specific methods for MongoDB")

    async def get_schema(self) -> Dict[str, List[str]]:
        collections = await self._db.list_collection_names()
        schema: Dict[str, List[str]] = {}
        for coll_name in collections:
            collection = self._db[coll_name]
            sample = await collection.find_one()
            if sample:
                keys = [k for k in sample.keys() if k != "_id"]
                schema[coll_name] = keys
            else:
                schema[coll_name] = []
        return schema

    async def get_primary_keys(self, table: str) -> List[str]:
        collection = self._db[table]
        index_info = await collection.index_information()
        for idx in index_info.values():
            if idx.get("unique"):
                return [key[0] for key in idx["key"]]
        return ["_id"]

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        collection = self._db[table]
        cursor = collection.find().skip(offset).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._serialize(doc) for doc in docs]

    async def count_records(self, table: str) -> int:
        collection = self._db[table]
        return await collection.count_documents({})

    async def fetch_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        collection = self._db[table]
        query = filters or {}
        cursor = collection.find(query)
        if limit is not None:
            cursor = cursor.limit(limit)
        docs = await cursor.to_list(length=limit or 0)
        return [self._serialize(doc) for doc in docs]

    async def fetch_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        collection = self._db[table]
        doc = await collection.find_one(filters)
        return self._serialize(doc) if doc else None

    async def update(
        self, table: str, filters: Dict[str, Any], values: Dict[str, Any]
    ) -> int:
        collection = self._db[table]
        result = await collection.update_many(filters, {"$set": values})
        return result.modified_count

    async def update_record(self, table: str, pk_column: str, pk_value: Any, updates: Dict[str, Any]) -> None:
        collection = self._db[table]
        if pk_column == "_id" and isinstance(pk_value, str) and len(pk_value) == 24:
            try:
                pk_value = ObjectId(pk_value)
            except Exception:
                pass
        await collection.update_one({pk_column: pk_value}, {"$set": updates})

    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        from pymongo import UpdateOne

        collection = self._db[table]
        ops = []
        for record in updates:
            filter_doc = {k: record[k] for k in key_columns if k in record}
            update_doc = {k: v for k, v in record.items() if k not in key_columns}
            if update_doc:
                ops.append(UpdateOne(filter_doc, {"$set": update_doc}))
        if not ops:
            return 0
        result = await collection.bulk_write(ops)
        return result.modified_count

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[MongoDBConnector]:
        async with await self._pool.start_session() as session:
            async with session.start_transaction():
                old_db = self._db
                try:
                    yield self
                finally:
                    self._db = old_db

    @staticmethod
    def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
        if "_id" in doc and isinstance(doc["_id"], ObjectId):
            doc["_id"] = str(doc["_id"])
        return doc
