"""Data loader (YAML/JSON/CSV) class"""

from __future__ import annotations

import os
import csv
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Union
from dotenv import load_dotenv
import yaml

from src.framework.contracts.config_contract import Settings
from src.framework.core.exceptions.exceptions import ConfigError


def _load_yaml(file_name: str, configfile=True) -> dict:
    """
    imports locators dictionry
    load YAML file safely.
    """
    # Dynamically insert the class name into the file path for locators
    path: str = ""

    if configfile:
        path = file_name
    else:
        path = os.path.join(
            "src",
            "framework",
            "domains",
            "web",
            "locators_repository",
            f"{file_name.lower()}.yaml",
        )
    if not os.path.exists(path):
        raise FileNotFoundError(f"YAML file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge override into base."""
    merged = deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = _deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def load_settings(env: str, config_dir: str = "configs") -> Settings:
    """
    Loads config via:
    1) configs/default.yaml
    2) configs/{env}.yaml overlay
    3) .env environment variables for secrets (optional)
    """
    load_dotenv(override=False)
    base_path = Path(config_dir)
    default_cfg = _load_yaml(base_path / "default.yaml")

    if default_cfg:
        print(
            f"[DEBUG]: Successfully loaded default config: {base_path / 'default.yaml'}"
        )
    if not default_cfg:
        raise ConfigError(
            f"[ERROR]: Missing or empty config file: {base_path / 'default.yaml'}"
        )

    env_cfg = _load_yaml(base_path / f"{env}.yaml")
    if env_cfg:
        print(
            f"[DEBUG]: Successfully loaded environment-specific config for '{env}': {base_path / f'{env}.yaml'}"
        )
    if not env_cfg:
        raise ConfigError(
            f"ERROR Missing or empty config file: {base_path / f'{env}.yaml'}"
        )
    merged = _deep_merge(default_cfg, env_cfg)
    merged["env"] = env

    # Inject secrets from environment variables (example: API token)
    auth = merged.get("api", {}).get("auth", {})
    token_env_var = auth.get("token_env_var", "API_TOKEN")
    token = os.getenv(token_env_var)
    if token:
        merged.setdefault("api", {}).setdefault("auth", {})["token"] = token

    # optional run id from env
    merged["run_id"] = os.getenv("RUN_ID")
    return Settings.model_validate(merged)
