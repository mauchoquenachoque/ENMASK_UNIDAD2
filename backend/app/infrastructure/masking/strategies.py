import hashlib
import secrets
import string
import struct
import random
import math
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional, Tuple

from faker import Faker

from app.domain.interfaces.masking_strategy import MaskingStrategy


def _seed_from_value(value: Any, extra: str = "") -> int:
    payload = f"{extra}:{value}".encode("utf-8")
    return int(hashlib.sha256(payload).hexdigest(), 16) % (2**32)


def _deterministic_faker(value: Any, seed_extra: str = "") -> Faker:
    seed_val = _seed_from_value(value, seed_extra)
    fake = Faker()
    fake.seed_instance(seed_val)
    return fake


def _luhn_checksum(number_str: str) -> int:
    digits = [int(d) for d in number_str]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10


def _generate_luhn(prefix: str, total_length: int, rng: random.Random) -> str:
    remaining = total_length - len(prefix) - 1
    body = prefix + "".join(str(rng.randint(0, 9)) for _ in range(remaining))
    check = _luhn_checksum(body + "0")
    check_digit = (10 - check) % 10
    return body + str(check_digit)


class SubstitutionStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        provider = options.get("provider", "name")
        fake = _deterministic_faker(value, provider)
        try:
            return getattr(fake, provider)()
        except AttributeError:
            return fake.word()

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        provider = options.get("provider", "name")
        fake = Faker()
        if not hasattr(fake, provider):
            return False, [f"Unknown Faker provider: {provider}"]
        return True, []


class HashingSHA256Strategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        salt = options.get("salt", "")
        payload = f"{value}{salt}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        salt = options.get("salt")
        if salt is not None and not isinstance(salt, str):
            return False, ["salt must be a string"]
        return True, []


class HashingSHA512Strategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        salt = options.get("salt", "")
        payload = f"{value}{salt}".encode("utf-8")
        return hashlib.sha512(payload).hexdigest()

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        salt = options.get("salt")
        if salt is not None and not isinstance(salt, str):
            return False, ["salt must be a string"]
        return True, []


class RedactionStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        mask_char = options.get("mask_char", "*")
        visible_first = options.get("visible_first", 0)
        visible_last = options.get("visible_last", 0)
        val_str = str(value)
        if visible_first + visible_last >= len(val_str):
            return mask_char * len(val_str)
        prefix = val_str[:visible_first]
        suffix = val_str[-visible_last:] if visible_last > 0 else ""
        masked_middle = mask_char * (len(val_str) - visible_first - visible_last)
        return prefix + masked_middle + suffix

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        for key in ("visible_first", "visible_last"):
            val = options.get(key, 0)
            if not isinstance(val, int) or val < 0:
                errors.append(f"{key} must be a non-negative integer")
        mask_char = options.get("mask_char", "*")
        if not isinstance(mask_char, str) or len(mask_char) != 1:
            errors.append("mask_char must be a single character")
        return (len(errors) == 0), errors


class NullificationStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        return None

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []


class TokenizationStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        prefix = options.get("prefix", "TOK")
        length = options.get("length", 16)
        token = f"{prefix}-{secrets.token_hex(length // 2)}"
        return token

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        length = options.get("length", 16)
        if not isinstance(length, int) or length < 4:
            errors.append("length must be an integer >= 4")
        prefix = options.get("prefix", "TOK")
        if not isinstance(prefix, str):
            errors.append("prefix must be a string")
        return (len(errors) == 0), errors


class PseudonymizationStrategy(MaskingStrategy):
    _ADJECTIVES = [
        "swift", "silent", "bright", "calm", "dark", "eager", "fair", "grand",
        "happy", "jolly", "keen", "lively", "merry", "noble", "proud", "quick",
        "sharp", "tall", "vivid", "warm", "bold", "cool", "dear", "fine",
        "gentle", "kind", "lush", "nice", "pure", "rare", "sage", "wise",
    ]
    _NOUNS = [
        "fox", "owl", "bear", "wolf", "hawk", "deer", "lion", "lynx",
        "seal", "duck", "crow", "hare", "moth", "wren", "dove", "pike",
        "crab", "toad", "fern", "moss", "pine", "rose", "sage", "vine",
        "brook", "cliff", "dune", "fjord", "glen", "hill", "lake", "peak",
    ]

    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        prefix = options.get("prefix", "")
        seed_val = _seed_from_value(value, "pseudonym")
        rng = random.Random(seed_val)
        adj = rng.choice(self._ADJECTIVES)
        noun = rng.choice(self._NOUNS)
        num = rng.randint(1, 999)
        pseudonym = f"{adj}_{noun}_{num}"
        if prefix:
            pseudonym = f"{prefix}_{pseudonym}"
        return pseudonym

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        prefix = options.get("prefix", "")
        if not isinstance(prefix, str):
            return False, ["prefix must be a string"]
        return True, []


class ShufflingStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        seed = options.get("seed", "default")
        seed_val = _seed_from_value(value, f"shuffle:{seed}")
        rng = random.Random(seed_val)
        chars = list(str(value))
        rng.shuffle(chars)
        return "".join(chars)

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []


class EncryptionStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        key_hex = options.get("key", "")
        if not key_hex:
            raise ValueError("Encryption key (hex) is required in options")
        key = bytes.fromhex(key_hex)
        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(key)
        plaintext = str(value).encode("utf-8")
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return (nonce + ciphertext).hex()

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        key = options.get("key")
        if not key:
            errors.append("key is required (hex-encoded 32-byte key)")
        elif not isinstance(key, str):
            errors.append("key must be a hex string")
        else:
            try:
                key_bytes = bytes.fromhex(key)
                if len(key_bytes) != 32:
                    errors.append("key must be exactly 32 bytes (64 hex chars)")
            except ValueError:
                errors.append("key must be a valid hex string")
        return (len(errors) == 0), errors


class FPEStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        seed = options.get("seed", "default")
        val_str = str(value)
        seed_val = _seed_from_value(value, f"fpe:{seed}")
        rng = random.Random(seed_val)
        result = []
        for char in val_str:
            if char.isdigit():
                result.append(str(rng.randint(0, 9)))
            elif char.isupper():
                result.append(rng.choice(string.ascii_uppercase))
            elif char.islower():
                result.append(rng.choice(string.ascii_lowercase))
            else:
                result.append(char)
        return "".join(result)

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []


class SyntheticDataStrategy(MaskingStrategy):
    def __init__(self):
        self._faker = Faker()

    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        data_type = options.get("data_type", "auto")
        seed_val = _seed_from_value(value, "synthetic")
        self._faker.seed_instance(seed_val)
        if data_type == "auto":
            data_type = self._infer_type(value)
        generators = {
            "name": lambda: self._faker.name(),
            "email": lambda: self._faker.email(),
            "phone": lambda: self._faker.phone_number(),
            "address": lambda: self._faker.address(),
            "text": lambda: self._faker.text(max_nb_chars=len(str(value))),
            "number": lambda: self._generate_similar_number(value),
            "date": lambda: self._faker.date_between(start_date="-10y", end_date="today"),
            "company": lambda: self._faker.company(),
            "url": lambda: self._faker.url(),
        }
        generator = generators.get(data_type, lambda: self._faker.word())
        return generator()

    def _infer_type(self, value: Any) -> str:
        val_str = str(value).strip()
        if "@" in val_str:
            return "email"
        try:
            datetime.fromisoformat(val_str.replace("Z", "+00:00"))
            return "date"
        except (ValueError, TypeError):
            pass
        if val_str.replace(".", "").replace("-", "").isdigit():
            return "number"
        if len(val_str) > 50:
            return "text"
        return "name"

    def _generate_similar_number(self, value: Any) -> Any:
        try:
            num = float(value)
            if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
                return self._faker.random_int(
                    min=max(0, int(num * 0.5)),
                    max=int(num * 1.5),
                )
            return round(self._faker.pyfloat(min_value=num * 0.5, max_value=num * 1.5), 4)
        except (ValueError, TypeError):
            return self._faker.pyint()

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        valid_types = {"auto", "name", "email", "phone", "address", "text", "number", "date", "company", "url"}
        data_type = options.get("data_type", "auto")
        if data_type not in valid_types:
            return False, [f"data_type must be one of: {', '.join(sorted(valid_types))}"]
        return True, []


class DifferentialPrivacyStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        epsilon = options.get("epsilon", 1.0)
        sensitivity = options.get("sensitivity", 1.0)
        data_type = options.get("data_type", "numeric")
        seed_val = _seed_from_value(value, "dp")
        rng = random.Random(seed_val)
        if data_type == "numeric":
            return self._add_laplace_noise(value, epsilon, sensitivity, rng)
        elif data_type == "categorical":
            categories = options.get("categories", [])
            if not categories:
                return value
            return self._randomized_response(value, categories, epsilon, rng)
        return value

    def _add_laplace_noise(self, value: Any, epsilon: float, sensitivity: float, rng: random.Random) -> Any:
        try:
            num = float(value)
        except (ValueError, TypeError):
            return value
        scale = sensitivity / epsilon
        u = rng.random() - 0.5
        # Inverse CDF of Laplace: -scale * sgn(u) * ln(1 - 2|u|)
        noise = -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))
        result = num + noise
        if isinstance(value, int) or (isinstance(value, str) and value.strip().isdigit()):
            return int(round(result))
        return round(result, 4)

    def _randomized_response(self, value: Any, categories: list, epsilon: float, rng: random.Random) -> Any:
        p = math.exp(epsilon) / (math.exp(epsilon) + len(categories) - 1)
        if rng.random() < p:
            return value
        others = [c for c in categories if c != value]
        return rng.choice(others) if others else value

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        epsilon = options.get("epsilon", 1.0)
        if not isinstance(epsilon, (int, float)) or epsilon <= 0:
            errors.append("epsilon must be a positive number")
        sensitivity = options.get("sensitivity", 1.0)
        if not isinstance(sensitivity, (int, float)) or sensitivity < 0:
            errors.append("sensitivity must be a non-negative number")
        data_type = options.get("data_type", "numeric")
        if data_type not in ("numeric", "categorical"):
            errors.append("data_type must be 'numeric' or 'categorical'")
        return (len(errors) == 0), errors


class ConsistentMaskingStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        namespace = options.get("namespace", "default")
        val_str = str(value)
        combined = f"{namespace}:{val_str}".encode("utf-8")
        h = hashlib.sha256(combined).hexdigest()
        return h[:min(len(h), len(val_str) + 8)]

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []


class DateShiftStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        max_shift_days = options.get("max_shift_days", 365)
        seed_val = _seed_from_value(value, "dateshift")
        rng = random.Random(seed_val)
        shift = rng.randint(-max_shift_days, max_shift_days)
        try:
            if isinstance(value, datetime):
                return value + timedelta(days=shift)
            if isinstance(value, date):
                return value + timedelta(days=shift)
            val_str = str(value).strip().replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(val_str)
            except ValueError:
                dt = datetime.strptime(val_str[:10], "%Y-%m-%d")
            shifted = dt + timedelta(days=shift)
            if "T" in val_str:
                return shifted.isoformat()
            return shifted.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            return value

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        max_shift = options.get("max_shift_days", 365)
        if not isinstance(max_shift, int) or max_shift < 1:
            errors.append("max_shift_days must be a positive integer")
        return (len(errors) == 0), errors


class PhoneNumberStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        val_str = str(value).strip()
        seed_val = _seed_from_value(value, "phone")
        rng = random.Random(seed_val)
        result = []
        for ch in val_str:
            if ch.isdigit():
                result.append(str(rng.randint(0, 9)))
            else:
                result.append(ch)
        return "".join(result)

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []


class EmailStrategy(MaskingStrategy):
    _DOMAINS = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com",
        "icloud.com", "aol.com", "mail.com", "zoho.com", "yandex.com",
        "fastmail.com", "gmx.com", "live.com", "msn.com", "mail.ru",
    ]

    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        val_str = str(value).strip()
        seed_val = _seed_from_value(value, "email")
        rng = random.Random(seed_val)
        preserve_domain = options.get("preserve_domain", False)
        if "@" in val_str:
            local_part, original_domain = val_str.rsplit("@", 1)
        else:
            local_part = val_str
            original_domain = "example.com"
        if preserve_domain:
            domain = original_domain
        else:
            domain = rng.choice(self._DOMAINS)
        fake = Faker()
        fake.seed_instance(seed_val)
        new_local = fake.user_name()
        return f"{new_local}@{domain}"

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        preserve = options.get("preserve_domain", False)
        if not isinstance(preserve, bool):
            errors.append("preserve_domain must be a boolean")
        return (len(errors) == 0), errors


class CreditCardStrategy(MaskingStrategy):
    _PREFIXES = {
        "visa": ["4"],
        "mastercard": ["51", "52", "53", "54", "55"],
        "amex": ["34", "37"],
        "discover": ["6011", "65"],
    }
    _LENGTHS = {
        "visa": 16,
        "mastercard": 16,
        "amex": 15,
        "discover": 16,
    }

    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        val_str = str(value).replace(" ", "").replace("-", "")
        card_type = options.get("card_type", self._detect_card_type(val_str))
        if card_type is None:
            card_type = "visa"
        card_type = card_type.lower()
        seed_val = _seed_from_value(value, "cc")
        rng = random.Random(seed_val)
        prefix = rng.choice(self._PREFIXES.get(card_type, ["4"]))
        length = self._LENGTHS.get(card_type, 16)
        return _generate_luhn(prefix, length, rng)

    def _detect_card_type(self, number: str) -> Optional[str]:
        if number.startswith("4"):
            return "visa"
        if any(number.startswith(p) for p in ("51", "52", "53", "54", "55")):
            return "mastercard"
        if number.startswith(("34", "37")):
            return "amex"
        if number.startswith(("6011", "65")):
            return "discover"
        return None

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        card_type = options.get("card_type")
        if card_type is not None:
            valid = {"visa", "mastercard", "amex", "discover"}
            if card_type.lower() not in valid:
                errors.append(f"card_type must be one of: {', '.join(sorted(valid))}")
        return (len(errors) == 0), errors


class IPAddressStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        val_str = str(value).strip()
        seed_val = _seed_from_value(value, "ip")
        rng = random.Random(seed_val)
        if ":" in val_str:
            return self._mask_ipv6(val_str, rng)
        return self._mask_ipv4(val_str, rng)

    def _mask_ipv4(self, ip: str, rng: random.Random) -> str:
        parts = ip.split(".")
        if len(parts) != 4:
            return ip
        first_octet = int(parts[0])
        if first_octet < 128:
            return f"{parts[0]}.{parts[1]}.{rng.randint(0, 255)}.{rng.randint(0, 255)}"
        elif first_octet < 192:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.{rng.randint(0, 255)}"
        else:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.{rng.randint(0, 255)}"

    def _mask_ipv6(self, ip: str, rng: random.Random) -> str:
        import ipaddress
        try:
            addr = ipaddress.ip_address(ip)
            addr_int = int(addr)
            masked_int = (addr_int & 0xFFFFFFFFFFFF0000) | rng.randint(0, 0xFFFF)
            return str(ipaddress.ip_address(masked_int))
        except ValueError:
            return ip

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []


class SSNStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        val_str = str(value).strip()
        seed_val = _seed_from_value(value, "ssn")
        rng = random.Random(seed_val)
        digits = [ch for ch in val_str if ch.isdigit()]
        separators = [ch for ch in val_str if not ch.isdigit()]
        if len(digits) != 9:
            return val_str
        new_digits = [str(rng.randint(0, 9)) for _ in range(9)]
        if separators:
            result = []
            d_idx = 0
            for ch in val_str:
                if ch.isdigit():
                    result.append(new_digits[d_idx])
                    d_idx += 1
                else:
                    result.append(ch)
            return "".join(result)
        return "".join(new_digits)

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []


class AddressStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        seed_val = _seed_from_value(value, "address")
        fake = Faker()
        fake.seed_instance(seed_val)
        return fake.address().replace("\n", ", ")

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return True, []


class NameStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        gender = options.get("gender")
        seed_val = _seed_from_value(value, "name")
        fake = Faker()
        fake.seed_instance(seed_val)
        if gender and gender.lower() in ("m", "male", "f", "female"):
            if gender.lower() in ("m", "male"):
                return fake.first_name_male()
            return fake.first_name_female()
        val_str = str(value).strip()
        parts = val_str.split()
        if len(parts) >= 2:
            return f"{fake.first_name()} {fake.last_name()}"
        return fake.first_name()

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        gender = options.get("gender")
        if gender is not None:
            valid = {"m", "male", "f", "female"}
            if gender.lower() not in valid:
                errors.append(f"gender must be one of: {', '.join(sorted(valid))}")
        return (len(errors) == 0), errors


class PerturbationStrategy(MaskingStrategy):
    def mask(self, value: Any, **options) -> Any:
        if value is None:
            return None
        variance_type = options.get("variance_type", "percentage")
        try:
            variance_value = float(options.get("variance_value", 10))
        except (ValueError, TypeError):
            variance_value = 10.0
        seed_val = _seed_from_value(value, "perturbation")
        rng = random.Random(seed_val)
        factor = rng.uniform(-variance_value, variance_value)
        if variance_type == "percentage":
            try:
                num = float(value)
                perturbed = num * (1 + factor / 100.0)
                if isinstance(value, int) or str(value).strip().isdigit():
                    return int(perturbed)
                return round(perturbed, 4)
            except ValueError:
                return value
        elif variance_type == "days":
            try:
                if isinstance(value, datetime):
                    dt = value
                else:
                    val_s = str(value).replace("Z", "+00:00")
                    try:
                        dt = datetime.fromisoformat(val_s)
                    except ValueError:
                        dt = datetime.strptime(val_s[:10], "%Y-%m-%d")
                perturbed_dt = dt + timedelta(days=factor)
                if isinstance(value, str):
                    if "T" in str(value):
                        return perturbed_dt.isoformat()
                    return perturbed_dt.strftime("%Y-%m-%d")
                return perturbed_dt
            except (ValueError, TypeError):
                return value
        return value

    def validate_options(self, options: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        vtype = options.get("variance_type", "percentage")
        if vtype not in ("percentage", "days"):
            errors.append("variance_type must be 'percentage' or 'days'")
        try:
            vval = float(options.get("variance_value", 10))
            if vval < 0:
                errors.append("variance_value must be non-negative")
        except (ValueError, TypeError):
            errors.append("variance_value must be a number")
        return (len(errors) == 0), errors