import json
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_str_list(raw: str) -> List[str]:
    if raw is None or not str(raw).strip():
        return []
    s = str(raw).strip()
    if s.startswith("["):
        return [str(x).strip() for x in json.loads(s) if str(x).strip()]
    return [part.strip() for part in s.split(",") if part.strip()]


_DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:3000,http://127.0.0.1:3000,"
    "http://localhost:4173,http://127.0.0.1:4173"
)

_DEFAULT_CORS_ORIGIN_REGEX = (
    r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|0\.0\.0\.0):\d{1,5}$"
)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Enmask SDM Platform"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = _DEFAULT_CORS_ORIGINS
    BACKEND_CORS_ORIGIN_REGEX: str = _DEFAULT_CORS_ORIGIN_REGEX
    API_KEY: str = ""
    SECRET_KEY: str = "changemeplease"
    ADMIN_EMAILS: str = ""
    REPOSITORY_BACKEND: str = "memory"
    POSTGRES_META_DSN: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/enmask_meta"
    MONGODB_META_URI: str = "mongodb://mongodb:27017"
    METADATA_DATABASE: str = "enmask_meta"
    GOOGLE_CLIENT_ID: str = ""

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_MASKING: str = "20/minute"

    # Auth / allowed domains
    ALLOWED_DOMAINS: str = ""
    AUTH_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MFA
    MFA_ENABLED: bool = False
    MFA_ISSUER: str = "Enmask"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Observability
    PROMETHEUS_METRICS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Vault / encryption
    VAULT_ENCRYPTION_KEY: str = ""
    VAULT_RETENTION_DAYS: int = 90

    # Plugins
    PLUGIN_DIRECTORY: str = "./plugins"

    # CSRF
    CSRF_ENABLED: bool = True
    CSRF_SECRET: str = ""

    # Password policy
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    def cors_origins_list(self) -> List[str]:
        parsed = _parse_str_list(self.BACKEND_CORS_ORIGINS)
        return parsed if parsed else _parse_str_list(_DEFAULT_CORS_ORIGINS)

    def cors_origin_regex(self) -> Optional[str]:
        r = (self.BACKEND_CORS_ORIGIN_REGEX or "").strip()
        if not r or r.lower() in ("false", "0", "-", "no"):
            return None
        return r

    def admin_emails_list(self) -> List[str]:
        return _parse_str_list(self.ADMIN_EMAILS)

    def allowed_domains_list(self) -> List[str]:
        return _parse_str_list(self.ALLOWED_DOMAINS)


settings = Settings()
