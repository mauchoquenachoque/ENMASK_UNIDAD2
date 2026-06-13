from typing import Any, Callable, Dict, List, Optional, Type

from app.domain.interfaces.masking_strategy import MaskingStrategy
from app.domain.value_objects.masking_algorithm import MaskingAlgorithm
from app.infrastructure.masking.registry import StrategyRegistry, global_registry
from app.infrastructure.masking.strategies import (
    AddressStrategy,
    ConsistentMaskingStrategy,
    CreditCardStrategy,
    DateShiftStrategy,
    DifferentialPrivacyStrategy,
    EmailStrategy,
    EncryptionStrategy,
    FPEStrategy,
    HashingSHA256Strategy,
    HashingSHA512Strategy,
    IPAddressStrategy,
    NameStrategy,
    NullificationStrategy,
    PerturbationStrategy,
    PhoneNumberStrategy,
    PseudonymizationStrategy,
    RedactionStrategy,
    SSNStrategy,
    ShufflingStrategy,
    SubstitutionStrategy,
    SyntheticDataStrategy,
    TokenizationStrategy,
)
from app.infrastructure.masking.validators import validate_options


_DEFAULT_STRATEGY_MAP: Dict[MaskingAlgorithm, Type[MaskingStrategy]] = {
    MaskingAlgorithm.SUBSTITUTION: SubstitutionStrategy,
    MaskingAlgorithm.HASHING: HashingSHA256Strategy,
    MaskingAlgorithm.HASHING_SHA256: HashingSHA256Strategy,
    MaskingAlgorithm.HASHING_SHA512: HashingSHA512Strategy,
    MaskingAlgorithm.REDACTION: RedactionStrategy,
    MaskingAlgorithm.NULLIFICATION: NullificationStrategy,
    MaskingAlgorithm.TOKENIZATION: TokenizationStrategy,
    MaskingAlgorithm.PSEUDONYMIZATION: PseudonymizationStrategy,
    MaskingAlgorithm.SHUFFLING: ShufflingStrategy,
    MaskingAlgorithm.ENCRYPTION: EncryptionStrategy,
    MaskingAlgorithm.FPE: FPEStrategy,
    MaskingAlgorithm.FORMAT_PRESERVING: FPEStrategy,
    MaskingAlgorithm.PERTURBATION: PerturbationStrategy,
    MaskingAlgorithm.SYNTHETIC_DATA: SyntheticDataStrategy,
    MaskingAlgorithm.DIFFERENTIAL_PRIVACY: DifferentialPrivacyStrategy,
    MaskingAlgorithm.CONSISTENT_MASKING: ConsistentMaskingStrategy,
    MaskingAlgorithm.DATE_SHIFT: DateShiftStrategy,
    MaskingAlgorithm.PHONE_NUMBER: PhoneNumberStrategy,
    MaskingAlgorithm.EMAIL: EmailStrategy,
    MaskingAlgorithm.CREDIT_CARD: CreditCardStrategy,
    MaskingAlgorithm.IP_ADDRESS: IPAddressStrategy,
    MaskingAlgorithm.SSN: SSNStrategy,
    MaskingAlgorithm.ADDRESS: AddressStrategy,
    MaskingAlgorithm.NAME: NameStrategy,
}


class MaskingEngine:
    def __init__(self, registry: Optional[StrategyRegistry] = None):
        self._registry = registry or global_registry
        self._register_defaults()

    def _register_defaults(self) -> None:
        for alg, cls in _DEFAULT_STRATEGY_MAP.items():
            if not self._registry.has(alg.value):
                self._registry.register_enum(alg, cls)

    def get_strategy(self, algorithm: MaskingAlgorithm) -> MaskingStrategy:
        return self._registry.get(algorithm.value)

    def get_strategy_by_name(self, name: str) -> MaskingStrategy:
        return self._registry.get(name)

    def mask_value(self, value: Any, algorithm: MaskingAlgorithm, options: Optional[Dict[str, Any]] = None) -> Any:
        opts = options or {}
        is_valid, errors = validate_options(algorithm.value, opts)
        if not is_valid:
            raise ValueError(f"Invalid options for {algorithm.value}: {'; '.join(errors)}")
        strategy = self.get_strategy(algorithm)
        return strategy.mask(value, **opts)

    def mask_batch(
        self,
        records: List[Dict[str, Any]],
        rules: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        rule_map: Dict[str, Dict[str, Any]] = {}
        for rule in rules:
            column = rule["column"]
            rule_map[column] = rule

        result = []
        for record in records:
            masked = dict(record)
            for column, rule in rule_map.items():
                if column not in masked:
                    continue
                algorithm = rule["algorithm"]
                if isinstance(algorithm, str):
                    algorithm = MaskingAlgorithm(algorithm)
                opts = rule.get("options", {})
                masked[column] = self.mask_value(masked[column], algorithm, opts)
            result.append(masked)
        return result

    def register_custom_strategy(self, name: str, strategy: MaskingStrategy) -> None:
        if not isinstance(strategy, MaskingStrategy):
            raise TypeError(f"Expected MaskingStrategy instance, got {type(strategy).__name__}")
        self._registry.register(name, type(strategy))
        self._registry._instances[name] = strategy

    def register_custom_strategy_class(self, name: str, strategy_class: Type[MaskingStrategy]) -> None:
        self._registry.register(name, strategy_class)

    def list_algorithms(self) -> List[str]:
        return self._registry.list_names()


_engine: Optional[MaskingEngine] = None


def get_masking_engine() -> MaskingEngine:
    global _engine
    if _engine is None:
        _engine = MaskingEngine()
    return _engine
