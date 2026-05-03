"""Logging module for structured log writing with hierarchical support."""

from __future__ import annotations
import logging
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

        Args:
            level: Logging level (e.g., 'INFO', 'DEBUG').
            log_file: Optional path to log file. If None, logs only to console.
        """
        if cls._configured:
            return  # Avoid re-configuration

        # Append worker ID to log file for parallel tests
        if log_file:
            user = get_system_username()
            wid = get_worker_id()
            if wid != "local":
                user = f"{user}_{wid}"
            log_file = log_file.replace(".log", f"_{user}.log")
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        # 1. Configure standard logging (root logger)
        logging.basicConfig(
            format="%(message)s",  # structlog handles formatting
            stream=sys.stdout,
            level=getattr(logging, level.upper(), logging.INFO),
        )

        # 2. Configure structlog
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                reorder_fields,
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Add file handler if specified
        if log_file:
            root_logger = logging.getLogger()
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(getattr(logging, level.upper(), logging.INFO))
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
        if not cls._configured:
            cls.configure_logging()  # Fallback to defaults
        return structlog.get_logger(name)
