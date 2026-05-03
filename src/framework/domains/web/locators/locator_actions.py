"""
Events for locators
"""

# Import the resolve function (if it belongs to another module)
from .locator_resolver import LocatorResolver


class ElementActions:
    """Locator's common action methods"""

    def __init__(self, page, name: str):
        self.page = page
        self.name = name

    def fill(self, locators: dict, locatorname: str, value: str):
        """Type event on a locator"""
        LocatorResolver.resolve(self, locators, locatorname).fill(value)

    def click(self, locators: dict, locatorname: str):
        """Click event on a locator"""
        LocatorResolver.resolve(self, locators, locatorname).click()

    def hover(self, locators: dict, locatorname: str):
        """Hover event on a locator"""
        LocatorResolver.resolve(self, locators, locatorname).hover()

    def checkbox(self, locators: dict, locatorname: str):
        """Hover event on a locator"""
        LocatorResolver.resolve(self, locators, locatorname).check()
