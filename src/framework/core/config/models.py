"""Pydantic models for loading and validating framework configuration."""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ExecutionSettings(BaseModel):
    """Test run parallelism, retries, and per-step timeouts."""

    parallel_workers: int = 4
    retries: int = 4
    timeout_sec: int = 60


class WebViewport(BaseModel):
    """Browser window dimensions for web runs."""

    width: int = 1440
    height: int = 900


class WebSettings(BaseModel):
    """Playwright browser target and failure artifacts."""

    base_url: str
    browser: Literal["chrome", "chromium", "firefox", "webkit"] = "chrome"
    headless: bool = True
    viewport: WebViewport = Field(default_factory=WebViewport)
    trace_on_failure: bool = True
    screenshot_on_failure: bool = True


class ApiAuthSettings(BaseModel):
    """API authentication mode and token source."""

    type: Literal["none", "bearer"] = "none"
    token_env_var: str = "API_TOKEN"


class ApiSettings(BaseModel):
    """HTTP API client base URL, timeout, and auth."""

    base_url: str
    timeout_sec: int = 30
    auth: ApiAuthSettings = Field(default_factory=ApiAuthSettings)


class DesktopSettings(BaseModel):
    """Desktop automation target app and pywinauto backend."""

    platform: Literal["windows"] = "windows"
    backend: Literal["uia", "win32"] = "uia"
    app_path: str
    implicit_wait_sec: int = 5


class LoggingSettings(BaseModel):
    """Log level and file path for run logs."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    file: str = "artifacts/logs/run.log"


class Settings(BaseModel):
    """Root configuration: env, channels/domains (web/api/desktop), execution, logging."""

    env: str = "dev"
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    web: WebSettings
    api: ApiSettings
    desktop: DesktopSettings
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    # Optional: allow a "test run id" to group artifacts in CI
    run_id: Optional[str] = None
