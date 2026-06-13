import asyncio
from abc import abstractmethod
from typing import Any, Dict, List, Optional

from app.core.logging import logger
from app.domain.interfaces.connector import DatabaseConnector
from app.domain.value_objects.database_type import DatabaseType


class BaseConnector(DatabaseConnector):
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        ssl: bool = False,
        pool_min_size: int = 1,
        pool_max_size: int = 10,
        query_timeout: float = 30.0,
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        **kwargs: Any,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.ssl = ssl
        self.pool_min_size = pool_min_size
        self.pool_max_size = pool_max_size
        self.query_timeout = query_timeout
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.extra_options: Dict[str, Any] = kwargs
        self._connected = False
        self._pool: Any = None

    async def connect(self) -> None:
        for attempt in range(1, self.max_retries + 1):
            try:
                await self._do_connect()
                self._connected = True
                logger.info(f"Connected to {self.__class__.__name__} at {self.host}:{self.port}/{self.database}")
                return
            except Exception as exc:
                delay = self.retry_base_delay * (2 ** (attempt - 1))
                logger.warning(
                    f"Connection attempt {attempt}/{self.max_retries} failed for "
                    f"{self.__class__.__name__}: {exc}. Retrying in {delay:.1f}s"
                )
                if attempt < self.max_retries:
                    await asyncio.sleep(delay)
        raise ConnectionError(
            f"Failed to connect to {self.__class__.__name__} after {self.max_retries} attempts"
        )

    async def disconnect(self) -> None:
        if self._connected:
            try:
                await self._do_disconnect()
            except Exception as exc:
                logger.error(f"Error disconnecting {self.__class__.__name__}: {exc}")
            finally:
                self._connected = False
                self._pool = None

    async def test_connection(self) -> bool:
        if not self._connected:
            return False
        try:
            await asyncio.wait_for(self._do_health_check(), timeout=self.query_timeout)
            return True
        except Exception as exc:
            logger.warning(f"Health check failed for {self.__class__.__name__}: {exc}")
            return False

    async def execute_with_retry(
        self, operation_name: str, coro_func, *args, **kwargs
    ) -> Any:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await asyncio.wait_for(
                    coro_func(*args, **kwargs), timeout=self.query_timeout
                )
            except asyncio.TimeoutError:
                last_exc = TimeoutError(
                    f"{operation_name} timed out after {self.query_timeout}s"
                )
                logger.warning(f"{operation_name} timeout on attempt {attempt}")
            except Exception as exc:
                last_exc = exc
                logger.warning(f"{operation_name} failed on attempt {attempt}: {exc}")
            if attempt < self.max_retries:
                delay = self.retry_base_delay * (2 ** (attempt - 1))
                await asyncio.sleep(delay)
        raise last_exc  # type: ignore[misc]

    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self.execute_with_retry("execute", self._do_execute, query, params)

    async def fetch_records(self, table: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        self._validate_identifier(table)
        query = f'SELECT * FROM "{table}" LIMIT {int(limit)} OFFSET {int(offset)}'
        return await self.execute(query)

    async def update_record(self, table: str, pk_column: str, pk_value: Any, updates: Dict[str, Any]) -> None:
        await self.update(table, {pk_column: pk_value}, updates)

    async def count_records(self, table: str) -> int:
        self._validate_identifier(table)
        rows = await self.execute(f'SELECT COUNT(*) AS cnt FROM "{table}"')
        if rows and isinstance(rows, list):
            return rows[0].get("cnt", 0)
        return 0

    async def get_primary_key(self, table: str) -> str:
        keys = await self.get_primary_keys(table)
        return keys[0] if keys else "id"

    def get_database_type(self) -> DatabaseType:
        raise NotImplementedError

    @abstractmethod
    async def _do_connect(self) -> None:
        pass

    @abstractmethod
    async def _do_disconnect(self) -> None:
        pass

    @abstractmethod
    async def _do_health_check(self) -> None:
        pass

    @abstractmethod
    async def _do_execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        pass

    @staticmethod
    def _validate_identifier(name: str) -> None:
        if not name.replace("_", "").replace("-", "").replace(".", "").isalnum():
            raise ValueError(f"Invalid identifier: {name}")
