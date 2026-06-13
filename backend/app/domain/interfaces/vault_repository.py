from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime


class VaultRepository(ABC):
    @abstractmethod
    async def save_backup(self, job_id: str, table_name: str, record_pk: str, original_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_backups_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete_backups_for_job(self, job_id: str) -> None:
        pass

    @abstractmethod
    async def encrypt_value(self, value: str) -> str:
        pass

    @abstractmethod
    async def decrypt_value(self, encrypted: str) -> str:
        pass

    @abstractmethod
    async def bulk_save_backups(self, records: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    async def bulk_delete_backups(self, backup_ids: List[str]) -> None:
        pass

    @abstractmethod
    async def set_retention_policy(self, days: int) -> None:
        pass

    @abstractmethod
    async def purge_expired(self, before: datetime) -> int:
        pass
