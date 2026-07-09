"""Structured logging setup."""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(*, json_logs: bool = False, filter_str: str = "info") -> None:
    level = logging.getLevelName(filter_str.split(",")[0].upper())
    if not isinstance(level, int):
        level = logging.INFO

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
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
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(level=level, stream=sys.stderr)
