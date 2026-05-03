"""Test method"""

import pytest

# from src.framework.core.quality.assertions.assert_web import WebUiAssert
from src.framework.core.quality.assertions.assert_web import WebUiAssert
from src.framework.domains.web.pages.login import LoginPage
from src.framework.domains.web.pages.inventorylist import InventoryList
from src.framework.domains.web.pages.inventoryitem import InventoryItem


@pytest.mark.poc
def test_login(logger, page, context, config):
    """Create a page and capture a screenshot when a test fails."""
    logger.info("Starting test execution .")
    lp = LoginPage(page, config=config)
    lp.goto(config.web.base_url)
    lp.login("standard_user", "secret_sauce")
    WebUiAssert.url(
        logger, "Verify page url contains", page, context, __name__, "inventory"
    )


@pytest.mark.poc
def test_checkout_end_to_end(logger, page, context, config):
    """Create an end 2 end checkout flow and assert."""
    logger.info("Starting test execution .")
    lp = LoginPage(page, config=config)
    lp.goto(config.web.base_url)
    lp.login("standard_user", "secret_sauce")

    il = InventoryList(page, config=config)
    il.select_product("backpack")
    ii = InventoryItem(page, config=config)
    ii.add_to_cart()
    WebUiAssert.url(
        logger, "Verify page url contains", page, context, __name__, "inventory-item"
    )


# @pytest.mark.poc
# def test_login1(logger, page, context, config):
#     """Create a page and capture a screenshot when a test fails."""
#     logger.info("Starting test execution .")
#     lp = LoginPage(page, config=config)
#     lp.goto(config.web.base_url)
#     lp.login("standard_user", "secret_sauce")
#     WebUiAssert.url(
#         logger, "Verify page url contains", page, context, __name__, "inventory1"
#     )
