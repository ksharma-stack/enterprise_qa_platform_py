"""Web UI Assertions module."""

import re

from playwright.sync_api import expect
from src.framework.core.quality.assertions.assert_evidence import (
    capture_screenshot,
    stop_and_save_trace,
)


class WebUiAssert:
    """Assertion class for Web UI testing."""

    @staticmethod
    def url(logger, message, page, context, test_name, expected_url):
        """
        Assert that the current page URL contains the expected string.

        Args:
            logger: Logger instance
            message: Assertion message
            page: Playwright page object
            context: Playwright context object
            module_name: Module name (typically __name__)
            expected_url: Expected URL substring to verify
        """
        try:
            current_url = page.url
            expect(page).to_have_url(re.compile(f".*{expected_url}"))
            logger.info(
                f"[PASSED]: {message}: checking if '{expected_url}' is in '{current_url}'"
            )

        except AssertionError as e:
            screenshot = capture_screenshot(page, test_name)
            trace = stop_and_save_trace(context, test_name)

            logger.error(
                "ASSERTION FAILED",
                step=message,
                error=str(e),
                screenshot=screenshot,
                trace=trace,
            )
            raise

    @staticmethod
    def visible(logger, locator, message: str, page, context, test_name: str):
        """Verify and log element visibility status.

        Args:
            locator: Playwright locator for the element.
            message: Description of the assertion.
            page: Playwright page object.
            context: Playwright browser context.
            test_name: Name of the test for artifact naming.

        Raises:
            AssertionError: If element is not visible.
        """

        try:
            expect(locator).to_be_visible()
            logger.info("ASSERTION PASSED", step=message)

        except AssertionError as e:
            screenshot = capture_screenshot(page, test_name)
            trace = stop_and_save_trace(context, test_name)

            logger.error(
                "ASSERTION FAILED",
                step=message,
                error=str(e),
                screenshot=screenshot,
                trace=trace,
            )
            raise

    @staticmethod
    def title(logger, message: str, page, context, test_name: str, expected_title):
        """Verify and log page title.

        Args:
            message: Description of the assertion.
            page: Playwright page object.
            context: Playwright browser context.
            test_name: Name of the test for artifact naming.
            expected_title: The expected page title.

        Raises:
            AssertionError: If page title doesn't match.
        """
        try:
            expect(page).to_have_title(expected_title)
            logger.info("ASSERTION PASSED", step=message)

        except AssertionError as e:
            screenshot = capture_screenshot(page, test_name)
            trace = stop_and_save_trace(context, test_name)

            logger.error(
                "ASSERTION FAILED",
                step=message,
                error=str(e),
                screenshot=screenshot,
                trace=trace,
            )
            raise
