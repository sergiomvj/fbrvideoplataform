import structlog
from structlog.types import Processor
from typing import Any

from .context import get_context


def add_logging_context(logger: Any, method_name: str, event_dict: dict) -> dict:
    ctx = get_context()
    for key, value in ctx.items():
        if key not in event_dict:
            event_dict[key] = value
    return event_dict


def configure_logging(json_logs: bool = False) -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        add_logging_context,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)