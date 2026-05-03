"""Web layer: Login Page objects"""

from __future__ import annotations
from tenacity import retry, stop_after_attempt, wait_fixed
from src.framework.core.utils.utils_loader import _load_yaml
from src.framework.domains.web.base_page import BasePage
from src.framework.domains.web.locators.locator_actions import ElementActions


class InventoryItem(BasePage):
    """Login page object methods and assertions."""

    def __init__(self, page, config):
        """Initialize locator and load locator YAML"""
        super().__init__(page, config)  # Call the BasePage's __init__ method
        self.classname = __class__.__name__
        self.locators = _load_yaml(__class__.__name__, False)[self.classname.lower()]

    # -------------------------
    # Login page actions
    # -------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def open(self, base_url, expected_title) -> None:
        """Navigate to the home page and wait for DOM content to load."""
        self.goto(base_url, expected_title)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def login(self, user: str, password: str) -> None:
        """Login using username and password"""
        ElementActions.fill(self, self.locators, "username", user)
        ElementActions.fill(self, self.locators, "password", password)
        ElementActions.click(self, self.locators, "login_button")

    # -------------------------
    # Login page assertions
    # -------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def assert_loaded(self) -> None:
        """Assert that the page has loaded successfully."""
        self.page.wait_for_timeout(200)  # minimal placeholder
        assert self.page.title == "Swag Labs"
