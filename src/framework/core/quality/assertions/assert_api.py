"""API assertion helpers."""

from __future__ import annotations

from typing import Any


class ApiAssert:
    "Assertion primitives for API tests."

    @staticmethod
    def status_code(response, expected: int) -> None:
        assert (
            response.status_code == expected
        ), f"Expected status {expected}, got {response.status_code}. Body: {response.text[:500]}"

    @staticmethod
    def json_key(response, key: str) -> None:
        payload = response.json()
        assert key in payload, f"Expected JSON key '{key}' not found in {payload}"

    @staticmethod
    def json_value(response, key: str, expected: Any) -> None:
        payload = response.json()
        actual = payload.get(key)
        assert (
            actual == expected
        ), f"Expected '{key}' to be '{expected}', got '{actual}'. Payload: {payload}"

    @staticmethod
    def header_contains(response, name: str, expected_substring: str) -> None:
        header_value = response.headers.get(name, "")
        assert expected_substring in header_value, (
            f"Expected header '{name}' to contain '{expected_substring}', "
            f"got '{header_value}'"
        )

    @staticmethod
    def response_time_lt(response, max_ms: int) -> None:
        elapsed_ms = int(response.elapsed.total_seconds() * 1000)
        assert (
            elapsed_ms < max_ms
        ), f"Expected response under {max_ms}ms, got {elapsed_ms}ms"
