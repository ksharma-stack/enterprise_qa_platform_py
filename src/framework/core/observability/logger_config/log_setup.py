"""Standard logging + handlers Logging module for structured log writing with hierarchical support."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional
import sys
from collections import OrderedDict
import structlog

from src.framework.core.utils.utils_generic import get_system_username, get_worker_id


# Custom processor to reorder fields
def reorder_fields(_, __, event_dict):
    """Re-orders format for structlog."""
    ordered = OrderedDict()
    # Fixed order first
    for key in ("timestamp", "level", "logger", "event"):
        if key in event_dict:
            ordered[key] = event_dict.pop(key)
    # Then any remaining fields
    for key, value in event_dict.items():
        ordered[key] = value
    return ordered


class LogFactory:
    """Factory for creating and retrieving configured loggers by name.

    Ensures hierarchical logging with structlog integration. Configure once via
    configure_logging(), then use get_logger(name) throughout the framework.
    """

    _configured = False

    @classmethod
    def configure_logging(
        cls, level: str = "INFO", log_file: Optional[str] = None
    ) -> None:
        """Configure logging once for the entire application.
        Safe for pytest-xdist (one process = one config).

        Args:
            level: Logging level (e.g., 'INFO', 'DEBUG').
            log_file: Optional path to log file. If None, logs only to console.
        """

        root_logger = logging.getLogger()

        # if getattr(root_logger, "_configured", False):
        #     return

        if cls._configured:
            return  # Avoid re-configuration

        # # Append worker ID to log file for parallel tests
        if log_file:
            user = get_system_username()
            wid = get_worker_id()
            if wid != "local":
                user = f"{user}_{wid}"
            log_file = log_file.replace(".log", f"_{user}.log")
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        # 1. Configure standard logging (root logger) - set level and add console handler
        root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Add console handler if not already present
        if not root_logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
            console_formatter = logging.Formatter("%(message)s")
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

        # if os.getenv("PYTEST_JSON_LOGS", "true").lower() == "true":
        #     renderer = structlog.processors.JSONRenderer()
        # else:
        #     renderer = structlog.dev.ConsoleRenderer(colors=True)

        # 2. Configure structlog
        structlog_processors = [
            structlog.contextvars.merge_contextvars,  # ✅ critical for parallel tests
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            reorder_fields,
            structlog.processors.JSONRenderer(),
        ]

        structlog.configure(
            processors=structlog_processors,
            context_class=dict,
            wrapper_class=structlog.make_filtering_bound_logger(
                logging.getLevelName(logging.getLogger().level)
            ),
            logger_factory=structlog.stdlib.LoggerFactory(),
            # logger_factory=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,  # ✅ IMPORTANT for performance
        )

        # Add file handler if specified
        if log_file:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(getattr(logging, level.upper(), logging.INFO))
            # Add formatter to properly format messages to file
            formatter = logging.Formatter("%(message)s")
            fh.setFormatter(formatter)
            root_logger.addHandler(fh)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> structlog.BoundLogger:
        """Get a configured logger by name.

        Args:
            name: Logger name (e.g., __name__ for module hierarchy).

        Returns:
            A structlog BoundLogger instance.
        """
        # Don't auto-configure here - let pytest fixtures handle it
        # if not cls._configured:
        #     cls.configure_logging()  # Fallback to defaults
        return structlog.get_logger(name)
