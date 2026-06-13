import time
import pytest
from app.core.security import (
    create_access_token,
    decode_token,
    verify_token_type,
    hash_password,
    verify_password,
    validate_password_strength,
)
from app.core.config import settings


class TestJWTToken:
    def test_create_and_verify(self):
        token = create_access_token(subject="user123", extra_claims={"email": "test@test.com"})
        payload = decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@test.com"
        assert payload["type"] == "access"

    def test_token_expiration(self):
        from datetime import timedelta
        token = create_access_token(subject="user123", expires_delta=timedelta(seconds=-1))
        with pytest.raises(Exception):
            decode_token(token)

    def test_invalid_token_signature(self):
        token = create_access_token(subject="user123")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(Exception):
            decode_token(tampered)

    def test_verify_token_type_valid(self):
        token = create_access_token(subject="user123")
        payload = decode_token(token)
        verify_token_type(payload, "access")

    def test_verify_token_type_invalid(self):
        token = create_access_token(subject="user123")
        payload = decode_token(token)
        with pytest.raises(Exception):
            verify_token_type(payload, "refresh")

    def test_token_contains_jti(self):
        token = create_access_token(subject="user123")
        payload = decode_token(token)
        assert "jti" in payload

    def test_different_tokens_differ(self):
        t1 = create_access_token(subject="user123")
        t2 = create_access_token(subject="user123")
        assert t1 != t2


class TestPasswordStrength:
    def test_valid_password(self):
        validate_password_strength("StrongP@ss123")

    def test_too_short(self):
        with pytest.raises(Exception):
            validate_password_strength("Sh1!")

    def test_no_uppercase(self):
        with pytest.raises(Exception):
            validate_password_strength("lowercase1!")

    def test_no_lowercase(self):
        with pytest.raises(Exception):
            validate_password_strength("UPPERCASE1!")

    def test_no_digit(self):
        with pytest.raises(Exception):
            validate_password_strength("NoDigitHere!")

    def test_no_special(self):
        with pytest.raises(Exception):
            validate_password_strength("NoSpecial123")


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "MySecureP@ss1"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        password = "MySecureP@ss1"
        hashed = hash_password(password)
        assert verify_password("WrongPassword1!", hashed) is False

    def test_different_hashes(self):
        password = "MySecureP@ss1"
        h1 = hash_password(password)
        h2 = hash_password(password)
        assert h1 != h2

    def test_verify_none_hash(self):
        assert verify_password("test", None) is False

    def test_verify_empty_hash(self):
        assert verify_password("test", "") is False
