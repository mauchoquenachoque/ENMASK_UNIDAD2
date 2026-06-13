import pytest
from app.infrastructure.masking.strategies import (
    SubstitutionStrategy,
    HashingSHA256Strategy,
    HashingSHA512Strategy,
    RedactionStrategy,
    NullificationStrategy,
    FPEStrategy,
    PerturbationStrategy,
    ShufflingStrategy,
    EmailStrategy,
    CreditCardStrategy,
    PhoneNumberStrategy,
    SSNStrategy,
    IPAddressStrategy,
    DateShiftStrategy,
    NameStrategy,
)


class TestSubstitutionStrategy:
    def test_deterministic(self):
        s = SubstitutionStrategy()
        r1 = s.mask("hello", provider="name")
        r2 = s.mask("hello", provider="name")
        assert r1 == r2

    def test_none_passthrough(self):
        s = SubstitutionStrategy()
        assert s.mask(None, provider="name") is None

    def test_different_providers(self):
        s = SubstitutionStrategy()
        name = s.mask("test", provider="name")
        email = s.mask("test", provider="email")
        assert isinstance(name, str)
        assert isinstance(email, str)
        assert "@" in email

    def test_invalid_provider_fallback(self):
        s = SubstitutionStrategy()
        result = s.mask("test", provider="nonexistent_provider_xyz")
        assert isinstance(result, str)

    def test_validate_options_valid(self):
        s = SubstitutionStrategy()
        ok, errors = s.validate_options({"provider": "name"})
        assert ok is True
        assert errors == []

    def test_validate_options_invalid(self):
        s = SubstitutionStrategy()
        ok, errors = s.validate_options({"provider": "nonexistent_provider_xyz"})
        assert ok is False
        assert len(errors) == 1


class TestHashingSHA256Strategy:
    def test_deterministic(self):
        s = HashingSHA256Strategy()
        assert s.mask("hello") == s.mask("hello")

    def test_different_values_differ(self):
        s = HashingSHA256Strategy()
        assert s.mask("hello") != s.mask("world")

    def test_salt_changes_output(self):
        s = HashingSHA256Strategy()
        no_salt = s.mask("hello")
        with_salt = s.mask("hello", salt="pepper")
        assert no_salt != with_salt

    def test_none_passthrough(self):
        s = HashingSHA256Strategy()
        assert s.mask(None) is None

    def test_output_is_hex(self):
        s = HashingSHA256Strategy()
        result = s.mask("test")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_validate_options(self):
        s = HashingSHA256Strategy()
        ok, _ = s.validate_options({"salt": "abc"})
        assert ok is True
        ok, errors = s.validate_options({"salt": 123})
        assert ok is False


class TestHashingSHA512Strategy:
    def test_deterministic(self):
        s = HashingSHA512Strategy()
        assert s.mask("hello") == s.mask("hello")

    def test_output_is_128_hex(self):
        s = HashingSHA512Strategy()
        result = s.mask("test")
        assert len(result) == 128

    def test_none_passthrough(self):
        s = HashingSHA512Strategy()
        assert s.mask(None) is None

    def test_salt_changes_output(self):
        s = HashingSHA512Strategy()
        assert s.mask("x", salt="a") != s.mask("x", salt="b")


class TestRedactionStrategy:
    def test_default_mask(self):
        s = RedactionStrategy()
        assert s.mask("abcdef") == "******"

    def test_visible_first(self):
        s = RedactionStrategy()
        assert s.mask("abcdef", visible_first=2) == "ab****"

    def test_visible_last(self):
        s = RedactionStrategy()
        assert s.mask("abcdef", visible_last=2) == "****ef"

    def test_visible_both(self):
        s = RedactionStrategy()
        assert s.mask("abcdef", visible_first=1, visible_last=1) == "a****f"

    def test_custom_mask_char(self):
        s = RedactionStrategy()
        assert s.mask("abcdef", mask_char="#") == "######"

    def test_none_passthrough(self):
        s = RedactionStrategy()
        assert s.mask(None) is None

    def test_visible_exceeds_length(self):
        s = RedactionStrategy()
        result = s.mask("abc", visible_first=5, visible_last=5)
        assert result == "***"

    def test_validate_options(self):
        s = RedactionStrategy()
        ok, _ = s.validate_options({"visible_first": 2, "visible_last": 1, "mask_char": "*"})
        assert ok is True
        ok, errors = s.validate_options({"visible_first": -1})
        assert ok is False
        ok, errors = s.validate_options({"mask_char": "ab"})
        assert ok is False


class TestNullificationStrategy:
    def test_always_returns_none(self):
        s = NullificationStrategy()
        assert s.mask("anything") is None
        assert s.mask(123) is None
        assert s.mask(None) is None
        assert s.mask("") is None

    def test_validate_options(self):
        s = NullificationStrategy()
        ok, _ = s.validate_options({})
        assert ok is True


class TestFPEStrategy:
    def test_digits_stay_digits(self):
        s = FPEStrategy()
        result = s.mask("12345")
        assert result.isdigit()
        assert len(result) == 5

    def test_letters_stay_letters(self):
        s = FPEStrategy()
        result = s.mask("abcDE")
        assert result.isalpha()
        assert len(result) == 5

    def test_mixed_preserves_format(self):
        s = FPEStrategy()
        result = s.mask("ab12")
        assert len(result) == 4
        assert result[0:2].isalpha()
        assert result[2:4].isdigit()

    def test_special_chars_preserved(self):
        s = FPEStrategy()
        result = s.mask("a-b")
        assert result[1] == "-"
        assert len(result) == 3

    def test_none_passthrough(self):
        s = FPEStrategy()
        assert s.mask(None) is None

    def test_deterministic(self):
        s = FPEStrategy()
        assert s.mask("test123") == s.mask("test123")


class TestPerturbationStrategy:
    def test_numeric_perturbation(self):
        s = PerturbationStrategy()
        result = s.mask(100, variance_type="percentage", variance_value=10)
        assert isinstance(result, int)
        assert 85 <= result <= 115

    def test_none_passthrough(self):
        s = PerturbationStrategy()
        assert s.mask(None) is None

    def test_string_numeric(self):
        s = PerturbationStrategy()
        result = s.mask("100", variance_type="percentage", variance_value=5)
        assert isinstance(result, int)

    def test_validate_options(self):
        s = PerturbationStrategy()
        ok, _ = s.validate_options({"variance_type": "percentage", "variance_value": 10})
        assert ok is True
        ok, errors = s.validate_options({"variance_type": "invalid"})
        assert ok is False


class TestShufflingStrategy:
    def test_same_elements(self):
        s = ShufflingStrategy()
        result = s.mask("abcde")
        assert sorted(result) == sorted("abcde")

    def test_none_passthrough(self):
        s = ShufflingStrategy()
        assert s.mask(None) is None

    def test_deterministic(self):
        s = ShufflingStrategy()
        assert s.mask("hello", seed="s1") == s.mask("hello", seed="s1")


class TestEmailStrategy:
    def test_valid_email_format(self):
        s = EmailStrategy()
        result = s.mask("john@example.com")
        assert "@" in result
        local, domain = result.rsplit("@", 1)
        assert len(local) > 0
        assert "." in domain

    def test_deterministic(self):
        s = EmailStrategy()
        assert s.mask("test@x.com") == s.mask("test@x.com")

    def test_none_passthrough(self):
        s = EmailStrategy()
        assert s.mask(None) is None

    def test_preserve_domain(self):
        s = EmailStrategy()
        result = s.mask("user@example.com", preserve_domain=True)
        assert result.endswith("@example.com")

    def test_validate_options(self):
        s = EmailStrategy()
        ok, _ = s.validate_options({"preserve_domain": True})
        assert ok is True
        ok, errors = s.validate_options({"preserve_domain": "yes"})
        assert ok is False


class TestCreditCardStrategy:
    def test_luhn_valid_visa(self):
        s = CreditCardStrategy()
        result = s.mask("4111111111111111")
        assert len(result) == 16
        assert result.startswith("4")
        assert _luhn_valid(result)

    def test_card_type_preservation(self):
        s = CreditCardStrategy()
        mc = s.mask("5111111111111118", card_type="mastercard")
        assert mc[0] == "5"
        assert len(mc) == 16
        assert _luhn_valid(mc)

    def test_amex_length(self):
        s = CreditCardStrategy()
        result = s.mask("341111111111111", card_type="amex")
        assert len(result) == 15
        assert _luhn_valid(result)

    def test_none_passthrough(self):
        s = CreditCardStrategy()
        assert s.mask(None) is None

    def test_deterministic(self):
        s = CreditCardStrategy()
        assert s.mask("4111111111111111") == s.mask("4111111111111111")

    def test_validate_options(self):
        s = CreditCardStrategy()
        ok, _ = s.validate_options({"card_type": "visa"})
        assert ok is True
        ok, errors = s.validate_options({"card_type": "diners"})
        assert ok is False


class TestPhoneNumberStrategy:
    def test_format_preservation(self):
        s = PhoneNumberStrategy()
        result = s.mask("+1 (555) 123-4567")
        assert result[0] == "+"
        assert result[2] == " "
        assert result[3] == "("
        assert result[7] == ")"

    def test_none_passthrough(self):
        s = PhoneNumberStrategy()
        assert s.mask(None) is None

    def test_deterministic(self):
        s = PhoneNumberStrategy()
        assert s.mask("555-1234") == s.mask("555-1234")

    def test_digits_only(self):
        s = PhoneNumberStrategy()
        result = s.mask("5551234567")
        assert result.isdigit()
        assert len(result) == 10


class TestSSNStrategy:
    def test_format_preservation(self):
        s = SSNStrategy()
        result = s.mask("123-45-6789")
        assert result[3] == "-"
        assert result[6] == "-"
        assert len(result) == 11
        digits_only = result.replace("-", "")
        assert digits_only.isdigit()

    def test_none_passthrough(self):
        s = SSNStrategy()
        assert s.mask(None) is None

    def test_deterministic(self):
        s = SSNStrategy()
        assert s.mask("123-45-6789") == s.mask("123-45-6789")

    def test_no_separators(self):
        s = SSNStrategy()
        result = s.mask("123456789")
        assert result.isdigit() and len(result) == 9


class TestIPAddressStrategy:
    def test_class_preservation(self):
        s = IPAddressStrategy()
        result = s.mask("192.168.1.100")
        parts = result.split(".")
        assert parts[0] == "192"
        assert parts[1] == "168"
        assert parts[2] == "1"

    def test_class_a_preservation(self):
        s = IPAddressStrategy()
        result = s.mask("10.0.0.1")
        parts = result.split(".")
        assert parts[0] == "10"

    def test_none_passthrough(self):
        s = IPAddressStrategy()
        assert s.mask(None) is None

    def test_deterministic(self):
        s = IPAddressStrategy()
        assert s.mask("192.168.1.1") == s.mask("192.168.1.1")


class TestDateShiftStrategy:
    def test_date_validity(self):
        s = DateShiftStrategy()
        result = s.mask("2024-01-15")
        parts = result.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4
        assert 1 <= int(parts[1]) <= 12
        assert 1 <= int(parts[2]) <= 31

    def test_none_passthrough(self):
        s = DateShiftStrategy()
        assert s.mask(None) is None

    def test_deterministic(self):
        s = DateShiftStrategy()
        assert s.mask("2024-06-15") == s.mask("2024-06-15")

    def test_validate_options(self):
        s = DateShiftStrategy()
        ok, _ = s.validate_options({"max_shift_days": 30})
        assert ok is True
        ok, errors = s.validate_options({"max_shift_days": -1})
        assert ok is False


class TestNameStrategy:
    def test_deterministic(self):
        s = NameStrategy()
        assert s.mask("John") == s.mask("John")

    def test_none_passthrough(self):
        s = NameStrategy()
        assert s.mask(None) is None

    def test_full_name(self):
        s = NameStrategy()
        result = s.mask("John Doe")
        parts = result.split()
        assert len(parts) >= 2

    def test_gender_option(self):
        s = NameStrategy()
        result = s.mask("Jane", gender="male")
        assert isinstance(result, str) and len(result) > 0

    def test_validate_options(self):
        s = NameStrategy()
        ok, _ = s.validate_options({"gender": "male"})
        assert ok is True
        ok, errors = s.validate_options({"gender": "other"})
        assert ok is False


def _luhn_valid(number_str: str) -> bool:
    digits = [int(d) for d in number_str]
    odd = digits[-1::-2]
    even = digits[-2::-2]
    total = sum(odd)
    for d in even:
        total += sum(divmod(d * 2, 10))
    return total % 10 == 0
