from typing import List, Dict, Optional, Any, Tuple
import re
from pydantic import BaseModel

from app.domain.value_objects.masking_algorithm import MaskingAlgorithm
from app.domain.value_objects.data_type import DataType
from app.domain.value_objects.compliance_framework import ComplianceFramework


class SuggestedRule(BaseModel):
    target_table: str
    target_column: str
    data_type: DataType
    strategy: MaskingAlgorithm
    strategy_options: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    compliance_frameworks: List[ComplianceFramework] = []


_COLUMN_PATTERNS: List[Tuple[re.Pattern, DataType, MaskingAlgorithm, Dict[str, Any], float]] = [
    (re.compile(r"email|correo|e_mail", re.IGNORECASE), DataType.EMAIL, MaskingAlgorithm.SUBSTITUTION, {"provider": "email"}, 0.9),
    (re.compile(r"password|passwd|clave|pwd|hash", re.IGNORECASE), DataType.SECRET, MaskingAlgorithm.HASHING_SHA256, {}, 0.95),
    (re.compile(r"phone|telefono|celular|mobile|tel", re.IGNORECASE), DataType.PHONE, MaskingAlgorithm.SUBSTITUTION, {"provider": "phone_number"}, 0.85),
    (re.compile(r"card|tarjeta|credit", re.IGNORECASE), DataType.CREDIT_CARD, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.85),
    (re.compile(r"ssn|social_security|seguro_social", re.IGNORECASE), DataType.SSN, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.9),
    (re.compile(r"dni|documento|identity|cedula", re.IGNORECASE), DataType.DNI, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.8),
    (re.compile(r"passport|pasaporte", re.IGNORECASE), DataType.PASSPORT, MaskingAlgorithm.REDACTION, {"mask_char": "*"}, 0.9),
    (re.compile(r"address|direccion|addr|street|domicilio", re.IGNORECASE), DataType.ADDRESS, MaskingAlgorithm.SUBSTITUTION, {"provider": "address"}, 0.8),
    (re.compile(r"first_name|firstname|nombre|given_name", re.IGNORECASE), DataType.NAME, MaskingAlgorithm.SUBSTITUTION, {"provider": "first_name"}, 0.85),
    (re.compile(r"last_name|lastname|apellido|surname|family_name", re.IGNORECASE), DataType.SURNAME, MaskingAlgorithm.SUBSTITUTION, {"provider": "last_name"}, 0.85),
    (re.compile(r"(^name$|^nombre$)", re.IGNORECASE), DataType.NAME, MaskingAlgorithm.SUBSTITUTION, {"provider": "name"}, 0.7),
    (re.compile(r"birth|nacimiento|dob|fecha_nac", re.IGNORECASE), DataType.DATE_OF_BIRTH, MaskingAlgorithm.SUBSTITUTION, {"provider": "date_of_birth"}, 0.85),
    (re.compile(r"iban|international_bank", re.IGNORECASE), DataType.IBAN, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.9),
    (re.compile(r"bank_account|cuenta_bancaria|account_number", re.IGNORECASE), DataType.BANK_ACCOUNT, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.85),
    (re.compile(r"ruc", re.IGNORECASE), DataType.RUC, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.85),
    (re.compile(r"rfc", re.IGNORECASE), DataType.RFC, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.85),
    (re.compile(r"curp", re.IGNORECASE), DataType.CURP, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.9),
    (re.compile(r"cpf", re.IGNORECASE), DataType.CPF, MaskingAlgorithm.FORMAT_PRESERVING, {}, 0.85),
    (re.compile(r"lat|lng|longitude|latitude|gps|coord", re.IGNORECASE), DataType.GPS_COORDINATES, MaskingAlgorithm.PERTURBATION, {"max_offset": 0.01}, 0.8),
    (re.compile(r"ip_address|ip_addr|ipv4|ipv6", re.IGNORECASE), DataType.IP_ADDRESS, MaskingAlgorithm.PERTURBATION, {}, 0.85),
    (re.compile(r"url|website|link", re.IGNORECASE), DataType.URL, MaskingAlgorithm.REDACTION, {"mask_char": "*"}, 0.7),
    (re.compile(r"token|jwt|session", re.IGNORECASE), DataType.TOKEN, MaskingAlgorithm.NULLIFICATION, {}, 0.8),
    (re.compile(r"api_key|apikey|secret_key|access_key", re.IGNORECASE), DataType.API_KEY, MaskingAlgorithm.NULLIFICATION, {}, 0.9),
    (re.compile(r"medical|diagnosis|icd|patient|health_record", re.IGNORECASE), DataType.MEDICAL_RECORD, MaskingAlgorithm.TOKENIZATION, {}, 0.85),
    (re.compile(r"biometric|fingerprint|face_id|iris", re.IGNORECASE), DataType.BIOMETRIC, MaskingAlgorithm.NULLIFICATION, {}, 0.9),
]

_VALUE_PATTERNS: List[Tuple[re.Pattern, DataType, float]] = [
    (re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"), DataType.EMAIL, 0.95),
    (re.compile(r"^\+?[\d\s\-\(\)]{7,20}$"), DataType.PHONE, 0.7),
    (re.compile(r"^\d{3}-\d{2}-\d{4}$"), DataType.SSN, 0.95),
    (re.compile(r"^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$"), DataType.CREDIT_CARD, 0.9),
    (re.compile(r"^[A-Z]{2}\d{2}[A-Z0-9]{4,30}$"), DataType.IBAN, 0.85),
    (re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"), DataType.CPF, 0.95),
    (re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"), DataType.IP_ADDRESS, 0.9),
    (re.compile(r"^\d{4}-\d{2}-\d{2}$"), DataType.DATE_OF_BIRTH, 0.6),
]

_COMPLIANCE_MAP: Dict[DataType, List[ComplianceFramework]] = {
    DataType.NAME: [ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.CCPA],
    DataType.SURNAME: [ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.CCPA],
    DataType.EMAIL: [ComplianceFramework.GDPR, ComplianceFramework.CCPA, ComplianceFramework.SOC2],
    DataType.PHONE: [ComplianceFramework.GDPR, ComplianceFramework.CCPA],
    DataType.ADDRESS: [ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.CCPA],
    DataType.DNI: [ComplianceFramework.GDPR, ComplianceFramework.CCPA],
    DataType.PASSPORT: [ComplianceFramework.GDPR, ComplianceFramework.CCPA],
    DataType.CREDIT_CARD: [ComplianceFramework.PCI_DSS, ComplianceFramework.GDPR],
    DataType.IBAN: [ComplianceFramework.PCI_DSS, ComplianceFramework.GDPR],
    DataType.BANK_ACCOUNT: [ComplianceFramework.PCI_DSS, ComplianceFramework.GDPR, ComplianceFramework.GLBA],
    DataType.RUC: [ComplianceFramework.GDPR],
    DataType.RFC: [ComplianceFramework.GDPR],
    DataType.CURP: [ComplianceFramework.GDPR],
    DataType.CPF: [ComplianceFramework.GDPR],
    DataType.SSN: [ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.CCPA, ComplianceFramework.GLBA],
    DataType.DATE_OF_BIRTH: [ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.CCPA],
    DataType.GPS_COORDINATES: [ComplianceFramework.GDPR, ComplianceFramework.CCPA],
    DataType.IP_ADDRESS: [ComplianceFramework.GDPR, ComplianceFramework.CCPA],
    DataType.URL: [ComplianceFramework.GDPR],
    DataType.TOKEN: [ComplianceFramework.SOC2, ComplianceFramework.ISO_27001],
    DataType.JWT: [ComplianceFramework.SOC2, ComplianceFramework.ISO_27001],
    DataType.API_KEY: [ComplianceFramework.SOC2, ComplianceFramework.ISO_27001],
    DataType.SECRET: [ComplianceFramework.SOC2, ComplianceFramework.ISO_27001, ComplianceFramework.PCI_DSS],
    DataType.MEDICAL_RECORD: [ComplianceFramework.HIPAA, ComplianceFramework.GDPR],
    DataType.BIOMETRIC: [ComplianceFramework.GDPR, ComplianceFramework.HIPAA, ComplianceFramework.CCPA],
}


class PIIDetector:
    def discover(self, schema: Dict[str, List[str]]) -> List[SuggestedRule]:
        suggestions = []
        for table, columns in schema.items():
            for column in columns:
                suggestion = self._analyze_column(table, column)
                if suggestion:
                    suggestions.append(suggestion)
        return suggestions

    def analyze_sample_data(self, table: str, column: str, samples: List[str]) -> Optional[SuggestedRule]:
        best_match: Optional[Tuple[DataType, float]] = None
        for value in samples:
            if not value:
                continue
            for pattern, data_type, confidence in _VALUE_PATTERNS:
                if pattern.match(str(value).strip()):
                    if best_match is None or confidence > best_match[1]:
                        best_match = (data_type, confidence)
        if best_match and best_match[1] >= 0.7:
            data_type, confidence = best_match
            strategy, options = self._strategy_for_type(data_type)
            return SuggestedRule(
                target_table=table,
                target_column=column,
                data_type=data_type,
                strategy=strategy,
                strategy_options=options,
                confidence=confidence,
                compliance_frameworks=_COMPLIANCE_MAP.get(data_type, []),
            )
        return None

    def _analyze_column(self, table: str, column: str) -> Optional[SuggestedRule]:
        for pattern, data_type, strategy, options, confidence in _COLUMN_PATTERNS:
            if pattern.search(column):
                return SuggestedRule(
                    target_table=table,
                    target_column=column,
                    data_type=data_type,
                    strategy=strategy,
                    strategy_options=options,
                    confidence=confidence,
                    compliance_frameworks=_COMPLIANCE_MAP.get(data_type, []),
                )
        return None

    def _strategy_for_type(self, data_type: DataType) -> Tuple[MaskingAlgorithm, Dict[str, Any]]:
        mapping: Dict[DataType, Tuple[MaskingAlgorithm, Dict[str, Any]]] = {
            DataType.EMAIL: (MaskingAlgorithm.SUBSTITUTION, {"provider": "email"}),
            DataType.PHONE: (MaskingAlgorithm.SUBSTITUTION, {"provider": "phone_number"}),
            DataType.NAME: (MaskingAlgorithm.SUBSTITUTION, {"provider": "first_name"}),
            DataType.SURNAME: (MaskingAlgorithm.SUBSTITUTION, {"provider": "last_name"}),
            DataType.ADDRESS: (MaskingAlgorithm.SUBSTITUTION, {"provider": "address"}),
            DataType.CREDIT_CARD: (MaskingAlgorithm.FORMAT_PRESERVING, {}),
            DataType.SSN: (MaskingAlgorithm.FORMAT_PRESERVING, {}),
            DataType.IBAN: (MaskingAlgorithm.FORMAT_PRESERVING, {}),
            DataType.CPF: (MaskingAlgorithm.FORMAT_PRESERVING, {}),
            DataType.DNI: (MaskingAlgorithm.FORMAT_PRESERVING, {}),
            DataType.DATE_OF_BIRTH: (MaskingAlgorithm.SUBSTITUTION, {"provider": "date_of_birth"}),
            DataType.IP_ADDRESS: (MaskingAlgorithm.PERTURBATION, {}),
            DataType.GPS_COORDINATES: (MaskingAlgorithm.PERTURBATION, {"max_offset": 0.01}),
            DataType.URL: (MaskingAlgorithm.REDACTION, {"mask_char": "*"}),
            DataType.TOKEN: (MaskingAlgorithm.NULLIFICATION, {}),
            DataType.JWT: (MaskingAlgorithm.NULLIFICATION, {}),
            DataType.API_KEY: (MaskingAlgorithm.NULLIFICATION, {}),
            DataType.SECRET: (MaskingAlgorithm.HASHING_SHA256, {}),
            DataType.MEDICAL_RECORD: (MaskingAlgorithm.TOKENIZATION, {}),
            DataType.BIOMETRIC: (MaskingAlgorithm.NULLIFICATION, {}),
        }
        return mapping.get(data_type, (MaskingAlgorithm.REDACTION, {"mask_char": "*"}))

    def get_compliance_frameworks(self, data_type: DataType) -> List[ComplianceFramework]:
        return _COMPLIANCE_MAP.get(data_type, [])


pii_detector = PIIDetector()
