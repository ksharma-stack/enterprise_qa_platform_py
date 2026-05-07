"""
Resolve locator YAML to a Playwright Locator using ordered strategies and short waits.
"""

from __future__ import annotations

from typing import Any

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from src.framework.core.exceptions.exceptions import LocatorResolutionError
from src.framework.core.observability.logger_config.log_setup import LogFactory
from src.framework.contracts.locator_contract import (
    LocatorStrategy,
    build_strategy_plan,
    is_locator_element_key,
)

logger = LogFactory.get_logger(__name__)

_DEFAULT_VISIBLE_MS = 8_000


class LocatorResolver:
    """Resolve locators for the sync Playwright API."""

    @staticmethod
    def resolve(
        page: Page,
        page_locators: dict[str, Any],
        element: str,
        *,
        visible_timeout_ms: int = _DEFAULT_VISIBLE_MS,
    ) -> Locator:
        """
        Return the first locator that becomes visible within ``visible_timeout_ms``.

        ``page_locators`` is the page section from YAML (e.g. the ``loginpage`` mapping).
        """
        if not is_locator_element_key(element):
            raise LocatorResolutionError(
                f"Key {element!r} is reserved and cannot be used as a locator name."
            )

        definition = page_locators.get(element)
        if definition is None:
            raise LocatorResolutionError(
                f"No locator definition for element {element!r}."
            )
        if not isinstance(definition, dict):
            raise LocatorResolutionError(
                f"Locator {element!r} must be a mapping, got {type(definition).__name__}."
            )

        strategies, healing = build_strategy_plan(definition)
        if not strategies:
            raise LocatorResolutionError(
                f"Locator {element!r} produced no strategies (check primary/healing)."
            )

        errors: list[str] = []
        first_locator: Locator | None = None

        for strat in strategies:
            try:
                loc = LocatorResolver._locator_for_strategy(page, strat)
                if first_locator is None:
                    first_locator = loc
                loc.wait_for(state="visible", timeout=visible_timeout_ms)
                if strat.label != "primary" and healing.mode == "suggest-only":
                    logger.warning(
                        "Locator %s resolved with %s (suggest-only: consider promoting "
                        "this selector in YAML).",
                        element,
                        strat.label,
                    )
                return loc
            except PlaywrightTimeoutError:
                errors.append(f"{strat.label}:{strat.kind} (not visible in time)")
            except LocatorResolutionError as ex:
                errors.append(f"{strat.label}:{strat.kind} ({ex})")

        detail = "; ".join(errors) if errors else "unknown"
        raise LocatorResolutionError(
            f"Could not resolve visible locator for {element!r}. Attempts: {detail}"
        )

    @staticmethod
    def _locator_for_strategy(page: Page, strat: LocatorStrategy) -> Locator:
        if strat.kind == "a11y":
            if not strat.role:
                raise LocatorResolutionError("a11y strategy missing role")
            return page.get_by_role(strat.role, name=strat.name)  # type: ignore[arg-type]
        if strat.kind == "css":
            if not strat.selector:
                raise LocatorResolutionError("css strategy missing selector")
            return page.locator(strat.selector).first
        if strat.kind == "xpath":
            if not strat.selector:
                raise LocatorResolutionError("xpath strategy missing selector")
            return page.locator(strat.selector).first
        raise LocatorResolutionError(f"Unsupported strategy kind {strat.kind!r}")
