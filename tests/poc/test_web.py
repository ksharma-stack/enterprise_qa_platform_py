"""Test method"""

import pytest

# from src.framework.core.quality.assertions.assert_web import WebUiAssert
from src.framework.core.quality.assertions.assert_web import WebUiAssert
from src.framework.domains.web.pages.login import LoginPage


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
def test_login1(logger, page, context, config):
    """Create a page and capture a screenshot when a test fails."""
    logger.info("Starting test execution .")
    lp = LoginPage(page, config=config)
    lp.goto(config.web.base_url)
    lp.login("standard_user", "secret_sauce")
    WebUiAssert.url(
        logger, "Verify page url contains", page, context, __name__, "inventory1"
    )
