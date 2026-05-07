"""Retry helpers for API calls."""

from __future__ import annotations

from typing import Iterable

from requests import Response
from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class RetryableHttpError(Exception):
    """Raised to signal retryable HTTP responses."""

    def __init__(self, response: Response):
        self.response = response
        super().__init__(f"Retryable HTTP status: {response.status_code}")


def retry_condition() -> retry_if_exception_type:
    """Retry network and retryable-http failures."""
    return retry_if_exception_type((RetryableHttpError,))


def stop_condition(attempts: int):
    """Stop strategy for retries."""
    return stop_after_attempt(max(1, attempts))


def wait_condition():
    """Wait strategy for retries."""
    return wait_exponential(multiplier=0.2, min=0.2, max=2)


def is_retryable_status(status_code: int, retryable: Iterable[int] | None = None) -> bool:
    """Check if an HTTP status code is retryable."""
    codes = set(retryable) if retryable else RETRYABLE_STATUS_CODES
    return status_code in codes
