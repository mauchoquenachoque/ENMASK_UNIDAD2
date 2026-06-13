from typing import List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.domain.interfaces.vault_repository import VaultRepository


class MemoryVaultRepository(VaultRepository):
    def __init__(self):
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._retention_days: int = 90

    async def save_backup(self, job_id: str, table_name: str, record_pk: str, original_data: Dict[str, Any]) -> None:
        if job_id not in self._data:
            self._data[job_id] = []
        self._data[job_id].append({
            "job_id": job_id,
            "table_name": table_name,
            "record_pk": record_pk,
            "original_data": original_data,
            "created_at": datetime.utcnow().isoformat(),
        })

    async def get_backups_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        return self._data.get(job_id, [])

    async def delete_backups_for_job(self, job_id: str) -> None:
        self._data.pop(job_id, None)

    async def encrypt_value(self, value: str) -> str:
        return value

    async def decrypt_value(self, encrypted: str) -> str:
        return encrypted

    async def bulk_save_backups(self, records: List[Dict[str, Any]]) -> None:
        for rec in records:
            await self.save_backup(
                rec["job_id"], rec["table_name"], rec["record_pk"], rec["original_data"]
            )

    async def bulk_delete_backups(self, backup_ids: List[str]) -> None:
        for job_id in list(self._data):
            self._data[job_id] = [b for b in self._data[job_id] if b.get("record_pk") not in backup_ids]

    async def set_retention_policy(self, days: int) -> None:
        self._retention_days = days

    async def purge_expired(self, before: datetime) -> int:
        count = 0
        for job_id in list(self._data):
            original_len = len(self._data[job_id])
            self._data[job_id] = [
                b for b in self._data[job_id]
                if datetime.fromisoformat(b.get("created_at", before.isoformat())) >= before
            ]
            count += original_len - len(self._data[job_id])
        return count


class MongoVaultRepository(VaultRepository):
    def __init__(self, uri: str, database_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database_name]
        self.collection = self.db["vault_backups"]

    async def save_backup(self, job_id: str, table_name: str, record_pk: str, original_data: Dict[str, Any]) -> None:
        doc = {
            "job_id": job_id,
            "table_name": table_name,
            "record_pk": record_pk,
            "original_data": original_data,
            "created_at": datetime.utcnow(),
        }
        await self.collection.insert_one(doc)

    async def get_backups_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"job_id": job_id})
        results = []
        async for document in cursor:
            document.pop("_id", None)
            results.append(document)
        return results

    async def delete_backups_for_job(self, job_id: str) -> None:
        await self.collection.delete_many({"job_id": job_id})

    async def encrypt_value(self, value: str) -> str:
        return value

    async def decrypt_value(self, encrypted: str) -> str:
        return encrypted

    async def bulk_save_backups(self, records: List[Dict[str, Any]]) -> None:
        if records:
            await self.collection.insert_many(records)

    async def bulk_delete_backups(self, backup_ids: List[str]) -> None:
        await self.collection.delete_many({"record_pk": {"$in": backup_ids}})

    async def set_retention_policy(self, days: int) -> None:
        self._retention_days = days

    async def purge_expired(self, before: datetime) -> int:
        result = await self.collection.delete_many({"created_at": {"$lt": before}})
        return result.deleted_count


memory_vault_repository = MemoryVaultRepository()
