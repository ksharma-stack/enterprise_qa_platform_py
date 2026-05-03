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
    # Inventory page actions
    # -------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def add_to_cart(self) -> None:
        """clicks add to cart button on product/inventory page"""
        ElementActions.click(self, self.locators, "addtocart")

    # -------------------------
    # Inventory page assertions
    # -------------------------
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def assert_loaded(self) -> None:
        """Assert that the page has loaded successfully."""
        self.page.wait_for_timeout(200)  # minimal placeholder
        assert self.page.title == "Swag Labs"
