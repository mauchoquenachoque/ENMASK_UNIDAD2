from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

from app.domain.entities.connection import ConnectionConfig
from app.domain.entities.masking_job import MaskingJob
from app.domain.entities.masking_rule import MaskingRule
from app.domain.entities.user import User
from app.domain.entities.audit_log import AuditLog
from app.domain.entities.scheduled_job import ScheduledJob

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int


class Repository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self, page: int = 1, page_size: int = 50) -> PaginatedResult[T]:
        pass

    @abstractmethod
    async def update(self, id: str, entity: T) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass


class ConnectionRepository(Repository[ConnectionConfig], ABC):
    pass


class RuleRepository(Repository[MaskingRule], ABC):
    pass


class JobRepository(Repository[MaskingJob], ABC):
    pass


class AuditLogRepository(Repository[AuditLog], ABC):
    @abstractmethod
    async def get_by_job_id(self, job_id: str) -> List[AuditLog]:
        pass


class UserRepository(Repository[User], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass


class ScheduleRepository(Repository[ScheduledJob], ABC):
    @abstractmethod
    async def get_due_jobs(self) -> List[ScheduledJob]:
        pass

    @abstractmethod
    async def deactivate(self, id: str) -> bool:
        pass


class PluginRepository(ABC):
    @abstractmethod
    async def register(self, name: str, version: str, config: dict) -> None:
        pass

    @abstractmethod
    async def get_config(self, name: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def list_plugins(self) -> List[dict]:
        pass

    @abstractmethod
    async def unregister(self, name: str) -> bool:
        pass


class ComplianceReportRepository(ABC):
    @abstractmethod
    async def generate_report(self, framework: str, start_date: str, end_date: str) -> dict:
        pass

    @abstractmethod
    async def get_report(self, report_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def list_reports(self, framework: Optional[str] = None) -> List[dict]:
        pass
