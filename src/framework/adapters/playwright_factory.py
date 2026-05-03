"""Playwright + pywinauto driver factories"""

from __future__ import annotations

from dataclasses import dataclass

# from typing import Literal

from playwright.sync_api import Browser, BrowserContext, Playwright
from src.framework.core.config.models import WebSettings


@dataclass(frozen=True)
class PlaywrightHandles:
    """Container for Playwright browser and context handles."""

    browser: Browser
    context: BrowserContext


def create_browser(playwright: Playwright, web: WebSettings) -> Browser:
    """Launch and return a Playwright browser instance based on web settings.

    Args:
        playwright: Playwright instance providing browser type access.
        web: WebSettings containing browser type and launch configuration.

    Returns:
        Launched Browser instance (chromium, firefox, or webkit).
    """
    browser_type = getattr(playwright, web.browser)  # chromium/firefox/webkit
    return browser_type.launch(headless=web.headless)


def create_context(
    browser: Browser, web: WebSettings, artifacts_dir: str
) -> BrowserContext:
    """Create and return a Playwright browser context with specified settings.

    Args:
        browser: Browser instance to create context from.
        web: WebSettings containing viewport and base URL configuration.
        artifacts_dir: Directory path for storing artifacts (currently unused).

    Returns:
        BrowserContext instance with configured viewport and base URL.
    """
    return browser.new_context(
        viewport={"width": web.viewport.width, "height": web.viewport.height},
        record_video_dir=None,  # can enable if needed
        base_url=web.base_url,
    )
