"API client factory methods."

from __future__ import annotations

from typing import Optional, Dict

from src.framework.core.config.models import ApiSettings, Settings
from src.framework.domains.api.client import ApiClient


def create_api_client(
    api: ApiSettings,
    logger,
    *,
    retries: int = 1,
    default_headers: Optional[Dict[str, str]] = None,
) -> ApiClient:
    "Create a configured `ApiClient` from `ApiSettings`."
    return ApiClient(
        api,
        logger,
        retries=retries,
        default_headers=default_headers,
    )


def create_api_client_from_settings(
    settings: Settings,
    logger,
    *,
    default_headers: Optional[Dict[str, str]] = None,
) -> ApiClient:
    "Create a configured `ApiClient` from root `Settings`."
    retries = max(1, settings.execution.retries + 1)
    return create_api_client(
        settings.api,
        logger,
        retries=retries,
        default_headers=default_headers,
    )
