"""sessionId 기반 로그 correlation (Relay MDC 와 동일 목적)."""
from __future__ import annotations

import contextvars
import logging

session_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("session_id", default="-")
registry_key_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("registry_key", default="-")


class LogContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.session_id = session_id_ctx.get()
        record.registry_key = registry_key_ctx.get()
        return True


def bind_session(session_id: str, registry_key: str | None = None) -> None:
    session_id_ctx.set(session_id or "-")
    if registry_key:
        registry_key_ctx.set(registry_key)
    else:
        registry_key_ctx.set(session_id or "-")


def clear_session() -> None:
    session_id_ctx.set("-")
    registry_key_ctx.set("-")


def configure_logging() -> None:
    root = logging.getLogger()
    log_format = "%(asctime)s [%(levelname)s] [session=%(session_id)s registry=%(registry_key)s] %(name)s - %(message)s"
    for handler in root.handlers:
        handler.addFilter(LogContextFilter())
        handler.setFormatter(logging.Formatter(log_format))
