import logging
import sys
import uuid
import json
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.config import settings

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    return _correlation_id.get("")


def set_correlation_id(cid: Optional[str] = None) -> str:
    cid = cid or uuid.uuid4().hex
    _correlation_id.set(cid)
    return cid


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        cid = _correlation_id.get("")
        if cid:
            log_entry["correlation_id"] = cid
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data
        return json.dumps(log_entry, default=str)


class _ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        cid = _correlation_id.get("")
        ts = self.formatTime(record, self.datefmt)
        prefix = f"[{cid}] " if cid else ""
        return f"{ts} {prefix}{record.levelname:8s} {record.name} - {record.getMessage()}"


def _build_formatter() -> logging.Formatter:
    if settings.LOG_FORMAT == "json":
        return _JsonFormatter()
    return _ConsoleFormatter()


def _create_handler() -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_build_formatter())
    return handler


def setup_logging() -> logging.Logger:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root = logging.getLogger("enmask")
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(_create_handler())
    root.propagate = False
    return root


def setup_audit_logger() -> logging.Logger:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    audit = logging.getLogger("enmask.audit")
    audit.setLevel(level)
    audit.handlers.clear()
    audit.addHandler(_create_handler())
    audit.propagate = False
    return audit


def setup_security_logger() -> logging.Logger:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    sec = logging.getLogger("enmask.security")
    sec.setLevel(level)
    sec.handlers.clear()
    sec.addHandler(_create_handler())
    sec.propagate = False
    return sec


logger = setup_logging()
audit_logger = setup_audit_logger()
security_logger = setup_security_logger()
