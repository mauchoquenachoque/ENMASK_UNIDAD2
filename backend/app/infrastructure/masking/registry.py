from typing import Dict, Optional, Type

from app.domain.interfaces.masking_strategy import MaskingStrategy
from app.domain.value_objects.masking_algorithm import MaskingAlgorithm


class StrategyRegistry:
    def __init__(self):
        self._strategies: Dict[str, Type[MaskingStrategy]] = {}
        self._instances: Dict[str, MaskingStrategy] = {}

    def register(self, name: str, strategy_class: Type[MaskingStrategy]) -> None:
        if not (isinstance(strategy_class, type) and issubclass(strategy_class, MaskingStrategy)):
            raise TypeError(f"{strategy_class} is not a MaskingStrategy subclass")
        self._strategies[name] = strategy_class
        self._instances.pop(name, None)

    def register_enum(self, algorithm: MaskingAlgorithm, strategy_class: Type[MaskingStrategy]) -> None:
        self.register(algorithm.value, strategy_class)

    def get(self, name: str) -> MaskingStrategy:
        if name not in self._strategies:
            raise KeyError(f"No strategy registered for '{name}'")
        if name not in self._instances:
            self._instances[name] = self._strategies[name]()
        return self._instances[name]

    def has(self, name: str) -> bool:
        return name in self._strategies

    def list_all(self) -> Dict[str, Type[MaskingStrategy]]:
        return dict(self._strategies)

    def list_names(self) -> list:
        return list(self._strategies.keys())

    def unregister(self, name: str) -> None:
        self._strategies.pop(name, None)
        self._instances.pop(name, None)

    def clear(self) -> None:
        self._strategies.clear()
        self._instances.clear()


global_registry = StrategyRegistry()
