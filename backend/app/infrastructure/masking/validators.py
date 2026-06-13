from typing import Any, Dict, List, Tuple

from app.domain.value_objects.masking_algorithm import MaskingAlgorithm
from app.infrastructure.masking.registry import global_registry


_ALGORITHM_OPTION_VALIDATORS: Dict[str, "OptionValidator"] = {}


class OptionValidator:
    def __init__(self, required: List[str] = None, optional: Dict[str, type] = None):
        self._required = required or []
        self._optional = optional or {}

    def validate(self, options: Dict[str, Any]) -> List[str]:
        errors = []
        for key in self._required:
            if key not in options or options[key] is None:
                errors.append(f"Missing required option: {key}")
        for key, expected_type in self._optional.items():
            if key in options and options[key] is not None:
                if not isinstance(options[key], expected_type):
                    errors.append(f"Option '{key}' must be of type {expected_type.__name__}")
        return errors


def register_validator(algorithm: str, validator: OptionValidator) -> None:
    _ALGORITHM_OPTION_VALIDATORS[algorithm] = validator


def _init_validators() -> None:
    register_validator("substitution", OptionValidator(
        optional={"provider": str},
    ))
    register_validator("hashing", OptionValidator(
        optional={"salt": str},
    ))
    register_validator("hashing_sha256", OptionValidator(
        optional={"salt": str},
    ))
    register_validator("hashing_sha512", OptionValidator(
        optional={"salt": str},
    ))
    register_validator("redaction", OptionValidator(
        optional={"mask_char": str, "visible_first": int, "visible_last": int},
    ))
    register_validator("nullification", OptionValidator())
    register_validator("tokenization", OptionValidator(
        optional={"prefix": str, "length": int},
    ))
    register_validator("pseudonymization", OptionValidator(
        optional={"prefix": str},
    ))
    register_validator("shuffling", OptionValidator(
        optional={"seed": str},
    ))
    register_validator("encryption", OptionValidator(
        required=["key"],
        optional={"key": str},
    ))
    register_validator("fpe", OptionValidator(
        optional={"seed": str},
    ))
    register_validator("format_preserving", OptionValidator(
        optional={"seed": str},
    ))
    register_validator("perturbation", OptionValidator(
        optional={"variance_type": str, "variance_value": (int, float)},
    ))
    register_validator("synthetic_data", OptionValidator(
        optional={"data_type": str},
    ))
    register_validator("differential_privacy", OptionValidator(
        optional={"epsilon": (int, float), "sensitivity": (int, float), "data_type": str, "categories": list},
    ))
    register_validator("consistent_masking", OptionValidator(
        optional={"namespace": str},
    ))
    register_validator("date_shift", OptionValidator(
        optional={"max_shift_days": int},
    ))
    register_validator("phone_number", OptionValidator())
    register_validator("email", OptionValidator(
        optional={"preserve_domain": bool},
    ))
    register_validator("credit_card", OptionValidator(
        optional={"card_type": str},
    ))
    register_validator("ip_address", OptionValidator())
    register_validator("ssn", OptionValidator())
    register_validator("address", OptionValidator())
    register_validator("name", OptionValidator(
        optional={"gender": str},
    ))


_init_validators()


def validate_options(algorithm: str, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
    all_errors: List[str] = []

    validator = _ALGORITHM_OPTION_VALIDATORS.get(algorithm)
    if validator:
        all_errors.extend(validator.validate(options))

    if global_registry.has(algorithm):
        strategy = global_registry.get(algorithm)
        valid, errors = strategy.validate_options(options)
        if not valid:
            all_errors.extend(errors)

    return (len(all_errors) == 0), all_errors


def validate_options_for_algorithm(algorithm: MaskingAlgorithm, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
    return validate_options(algorithm.value, options)
