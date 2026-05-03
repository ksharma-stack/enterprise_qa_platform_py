"""Web layer: Inventory List objects"""

from __future__ import annotations
from tenacity import retry, stop_after_attempt, wait_fixed
from src.framework.core.utils.utils_loader import _load_yaml
from src.framework.domains.web.base_page import BasePage
from src.framework.domains.web.locators.locator_actions import ElementActions


class InventoryList(BasePage):
    """Inventory List page object methods and assertions."""

    def __init__(self, page, config):
        """Initialize locator and load locator YAML"""
        super().__init__(page, config)  # Call the BasePage's __init__ method
        self.classname = __class__.__name__
        self.locators = _load_yaml(__class__.__name__, False)[self.classname.lower()]

    # -------------------------
    # Inventory List Actions
    # -------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def select_product(self, inventory: str) -> None:
        """Select item from inventory list"""
        ElementActions.click(self, self.locators, inventory)

    # -------------------------
    # Inventory List Assertions
    # -------------------------
    retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)

    def assert_loaded(self) -> None:
        """Assert that the page has loaded successfully."""
        self.page.wait_for_timeout(200)  # minimal placeholder
        assert self.page.title == "Swag Labs"
