from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class MaskingStrategy(ABC):
    @abstractmethod
    def mask(self, value: Any, **options) -> Any:
        pass

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []

    def get_name(self) -> str:
        return self.__class__.__name__

    def get_supported_data_types(self) -> List[str]:
        return []
