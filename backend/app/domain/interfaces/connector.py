from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List

from app.domain.value_objects.database_type import DatabaseType


class DatabaseConnector(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        pass

    @abstractmethod
    async def get_schema(self) -> Dict[str, List[str]]:
        pass

    @abstractmethod
    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_record(self, table: str, pk_column: str, pk_value: Any, updates: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def count_records(self, table: str) -> int:
        pass

    @abstractmethod
    async def get_primary_key(self, table: str) -> str:
        pass

    @abstractmethod
    def get_database_type(self) -> DatabaseType:
        pass

    @abstractmethod
    async def get_primary_keys(self, table: str) -> List[str]:
        pass

    @abstractmethod
    async def fetch_all(
        self,
        table: str,
        filters: Dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def fetch_one(
        self, table: str, filters: Dict[str, Any]
    ) -> Dict[str, Any] | None:
        pass

    @abstractmethod
    async def update(
        self, table: str, filters: Dict[str, Any], values: Dict[str, Any]
    ) -> int:
        pass

    @abstractmethod
    async def bulk_update(
        self, table: str, updates: List[Dict[str, Any]], key_columns: List[str]
    ) -> int:
        pass

    @abstractmethod
    async def execute(self, query: str, params: Dict[str, Any] | None = None) -> Any:
        pass

    @abstractmethod
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["DatabaseConnector"]:
        pass

    async def close(self) -> None:
        await self.disconnect()
