from abc import ABC, abstractmethod
from typing import Dict, Type

from app.domain.interfaces.connector import DatabaseConnector
from app.domain.interfaces.masking_strategy import MaskingStrategy


class EnmaskPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def initialize(self) -> None: ...

    @abstractmethod
    def shutdown(self) -> None: ...

    def get_connectors(self) -> Dict[str, Type[DatabaseConnector]]:
        return {}

    def get_strategies(self) -> Dict[str, Type[MaskingStrategy]]:
        return {}
