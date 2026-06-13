import pytest
from app.domain.services.pii_detector import PIIDetector, SuggestedRule
from app.domain.value_objects.data_type import DataType
from app.domain.value_objects.masking_algorithm import MaskingAlgorithm


@pytest.fixture
def detector() -> PIIDetector:
    return PIIDetector()


class TestPIIDetectorColumnDetection:
    def test_email_column(self, detector: PIIDetector):
        results = detector.discover({"users": ["email"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.EMAIL
        assert results[0].target_column == "email"

    def test_phone_column(self, detector: PIIDetector):
        results = detector.discover({"contacts": ["phone_number"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.PHONE

    def test_password_column(self, detector: PIIDetector):
        results = detector.discover({"users": ["password"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.SECRET
        assert results[0].strategy == MaskingAlgorithm.HASHING_SHA256

    def test_credit_card_column(self, detector: PIIDetector):
        results = detector.discover({"payments": ["credit_card"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.CREDIT_CARD

    def test_ssn_column(self, detector: PIIDetector):
        results = detector.discover({"employees": ["ssn"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.SSN

    def test_address_column(self, detector: PIIDetector):
        results = detector.discover({"users": ["address"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.ADDRESS

    def test_first_name_column(self, detector: PIIDetector):
        results = detector.discover({"users": ["first_name"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.NAME

    def test_last_name_column(self, detector: PIIDetector):
        results = detector.discover({"users": ["last_name"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.SURNAME

    def test_unknown_column_returns_none(self, detector: PIIDetector):
        results = detector.discover({"users": ["transaction_count"]})
        assert len(results) == 0

    def test_schema_discovery_multiple_tables(self, detector: PIIDetector):
        schema = {
            "users": ["id", "email", "first_name", "last_name", "password"],
            "orders": ["id", "credit_card", "amount"],
            "logs": ["id", "message"],
        }
        results = detector.discover(schema)
        columns_found = {r.target_column for r in results}
        assert "email" in columns_found
        assert "first_name" in columns_found
        assert "password" in columns_found
        assert "credit_card" in columns_found
        assert "message" not in columns_found

    def test_ip_address_column(self, detector: PIIDetector):
        results = detector.discover({"servers": ["ip_address"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.IP_ADDRESS

    def test_token_column(self, detector: PIIDetector):
        results = detector.discover({"sessions": ["token"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.TOKEN
        assert results[0].strategy == MaskingAlgorithm.NULLIFICATION

    def test_api_key_column(self, detector: PIIDetector):
        results = detector.discover({"integrations": ["api_key"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.API_KEY

    def test_medical_column(self, detector: PIIDetector):
        results = detector.discover({"patients": ["medical_record"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.MEDICAL_RECORD

    def test_biometric_column(self, detector: PIIDetector):
        results = detector.discover({"users": ["biometric"]})
        assert len(results) == 1
        assert results[0].data_type == DataType.BIOMETRIC


class TestPIIDetectorValuePatterns:
    def test_email_value_detection(self, detector: PIIDetector):
        result = detector.analyze_sample_data("users", "col", ["user@example.com", "test@domain.org"])
        assert result is not None
        assert result.data_type == DataType.EMAIL

    def test_ssn_value_detection(self, detector: PIIDetector):
        result = detector.analyze_sample_data("users", "col", ["123-45-6789", "987-65-4321"])
        assert result is not None
        assert result.data_type == DataType.SSN

    def test_credit_card_value_detection(self, detector: PIIDetector):
        result = detector.analyze_sample_data("payments", "col", ["4111 1111 1111 1111"])
        assert result is not None
        assert result.data_type == DataType.CREDIT_CARD

    def test_ip_value_detection(self, detector: PIIDetector):
        result = detector.analyze_sample_data("logs", "col", ["192.168.1.1", "10.0.0.1"])
        assert result is not None
        assert result.data_type == DataType.IP_ADDRESS

    def test_unknown_value_returns_none(self, detector: PIIDetector):
        result = detector.analyze_sample_data("t", "col", ["hello", "world"])
        assert result is None

    def test_empty_samples(self, detector: PIIDetector):
        result = detector.analyze_sample_data("t", "col", [])
        assert result is None


class TestPIIDetectorCompliance:
    def test_email_has_compliance_frameworks(self, detector: PIIDetector):
        frameworks = detector.get_compliance_frameworks(DataType.EMAIL)
        assert len(frameworks) > 0

    def test_ssn_has_compliance_frameworks(self, detector: PIIDetector):
        frameworks = detector.get_compliance_frameworks(DataType.SSN)
        assert len(frameworks) >= 3
