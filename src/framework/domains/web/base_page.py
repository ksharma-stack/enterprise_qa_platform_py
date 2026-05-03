"""
# Base Page Object for the Page Object Model (POM).

# This module provides the `BasePage` class, which defines common navigation and shared
# capabilities for all page objects in the framework.
#"""

from __future__ import annotations

import re
from playwright.sync_api import Page, expect
from src.framework.core.config.models import Settings
from src.framework.core.utils.utils_generic import (
    get_system_username,
    get_worker_id,
)
from src.framework.core.observability.logger_config.log_setup import LogFactory

logger = LogFactory.get_logger(__name__)


class BasePage:
    """Base class for all page objects.

    Attributes:
        page: Playwright Page instance used to interact with the browser.
        base_url: The application's base URL.
    """

    def __init__(self, page: Page, config: Settings) -> None:
        self.page = page
        self.config = config
        self.user = get_system_username()
        self.wid = get_worker_id()
        wid = get_worker_id()
        if wid != "local":
            self.user = f"{self.user}_{wid}"

    def goto(
        self, base_url: str = "https://www.saucedemo.com/", expected_title: str = ""
    ) -> None:
        """Navigate to specified url and verify expected title
        Args:
            base_url: Url to navigate
            expectedTitle: Expected title of the page.
        #"""
        self.page.goto(base_url, wait_until="domcontentloaded")
        if expected_title:
            self.assert_title(expected_title)

    def assert_title(self, expected_title: str) -> None:
        """verify expected title
        Args:
            expectedTitle: Expected title of the page.
        #"""
        expect(self.page).to_have_title(expected_title)

    def assert_url(self, expected_value: str) -> None:
        """verify expected title
        Args:
            expectedTitle: Expected title of the page.
        #"""

        expect(self.page).to_have_url(re.compile(f".*{expected_value}"))
