"""HTTP client abstraction for API automation."""

from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from requests import Response, Session
from tenacity import Retrying, retry_if_exception_type

from src.framework.core.config.models import ApiSettings
from src.framework.core.exceptions.exceptions import ApiError
from src.framework.domains.api.auth import build_auth_headers
from src.framework.domains.api.retry import (
    RetryableHttpError,
    is_retryable_status,
    stop_condition,
    wait_condition,
)


class ApiClient:
    """Reusable HTTP client with config-based defaults and retries."""

    def __init__(
        self,
        api_settings: ApiSettings,
        logger,
        *,
        retries: int = 1,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.api_settings = api_settings
        self.logger = logger
        self.retries = max(1, retries)
        self.session: Session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

        auth_headers = build_auth_headers(api_settings)
        if auth_headers:
            self.session.headers.update(auth_headers)

        if default_headers:
            self.session.headers.update(default_headers)

    def close(self) -> None:
        """Close HTTP session."""
        self.session.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        expected_status: Optional[int] = None,
    ) -> Response:
        """Issue an API request with retry and optional expected-status validation."""
        final_timeout = timeout or self.api_settings.timeout_sec
        url = urljoin(f"{self.api_settings.base_url.rstrip('/')}/", path.lstrip("/"))
        method_upper = method.upper()

        send_kwargs: Dict[str, Any] = {
            "method": method_upper,
            "url": url,
            "params": params,
            "json": json,
            "data": data,
            "headers": headers,
            "timeout": final_timeout,
        }

        self.logger.info("API request started", method=method_upper, url=url)

        # Retries are intentionally limited to transport errors and retryable status codes.
        retryer = Retrying(
            stop=stop_condition(self.retries),
            wait=wait_condition(),
            retry=retry_if_exception_type(
                (requests.RequestException, RetryableHttpError)
            ),
            reraise=True,
        )

        try:
            response = retryer(self._send_with_retry_status, **send_kwargs)
        except Exception as exc:
            self.logger.error(
                "API request failed",
                method=method_upper,
                url=url,
                error=str(exc),
            )
            raise ApiError(f"Request failed for {method_upper} {url}: {exc}") from exc

        if expected_status is not None and response.status_code != expected_status:
            body_excerpt = response.text[:500]
            raise ApiError(
                f"Unexpected status for {method_upper} {url}. "
                f"Expected {expected_status}, got {response.status_code}. "
                f"Body excerpt: {body_excerpt}"
            )

        self.logger.info(
            "API request completed",
            method=method_upper,
            url=url,
            status_code=response.status_code,
            elapsed_ms=int(response.elapsed.total_seconds() * 1000),
            response=self._response_for_log(response),
        )
        return response

    def _send_with_retry_status(self, **kwargs) -> Response:
        response = self.session.request(**kwargs)
        if is_retryable_status(response.status_code):
            raise RetryableHttpError(response)
        return response

    @staticmethod
    def _response_for_log(response: Response, max_chars: int = 1200):
        """Build a safe, size-limited representation of response body for logs."""
        try:
            payload = response.json()
            text = str(payload)
        except ValueError:
            text = response.text or ""

        if len(text) > max_chars:
            return f"{text[:max_chars]}...<truncated>"
        return text

    def get(self, path: str, **kwargs) -> Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> Response:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs) -> Response:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        return self.request("DELETE", path, **kwargs)
