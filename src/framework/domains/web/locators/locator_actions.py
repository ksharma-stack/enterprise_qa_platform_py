"""
Events for locators
"""

from __future__ import annotations

from typing import Any

from src.framework.domains.web.locators.locator_resolver import LocatorResolver


class ElementActions:
    """Locator action helpers; ``page_host`` is any object with a ``.page`` Playwright Page."""

    @staticmethod
    def fill(page_host: Any, locators: dict, locatorname: str, value: str) -> None:
        """Type into the resolved locator."""
        loc = LocatorResolver.resolve(page_host.page, locators, locatorname)
        loc.fill(value)

    @staticmethod
    def click(page_host: Any, locators: dict, locatorname: str) -> None:
        """Click the resolved locator."""
        loc = LocatorResolver.resolve(page_host.page, locators, locatorname)
        loc.click()

    @staticmethod
    def hover(page_host: Any, locators: dict, locatorname: str) -> None:
        """Hover the resolved locator."""
        loc = LocatorResolver.resolve(page_host.page, locators, locatorname)
        loc.hover()

    @staticmethod
    def checkbox(page_host: Any, locators: dict, locatorname: str) -> None:
        """Check the resolved locator (checkbox / radio)."""
        loc = LocatorResolver.resolve(page_host.page, locators, locatorname)
        loc.check()
