"""Authentication helpers for API domain."""

from __future__ import annotations

import os
from typing import Dict, Optional

from src.framework.core.config.models import ApiSettings


def resolve_bearer_token(api_settings: ApiSettings) -> Optional[str]:
    "Resolve bearer token from env-var name in config."
    token_env_var = api_settings.auth.token_env_var
    token = os.getenv(token_env_var)
    return token


def build_auth_headers(api_settings: ApiSettings) -> Dict[str, str]:
    "Build auth headers based on configured auth mode."
    auth_type = api_settings.auth.type
    if auth_type == "none":
        return {}
    if auth_type == "bearer":
        token = resolve_bearer_token(api_settings)
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}
    return {}
