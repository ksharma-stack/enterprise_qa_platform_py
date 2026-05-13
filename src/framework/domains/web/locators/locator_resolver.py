"""
Resolve locator YAML to a Playwright Locator using ordered strategies and short waits.
"""

from __future__ import annotations

from typing import Any
import json
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from src.framework.core.exceptions.exceptions import LocatorResolutionError
from src.framework.services.locator_healing_service import AiService, get_ai_service
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

    def __init__(self, ai_service: AiService):
        self._ai_service = ai_service

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

        # --------------------------------------------------
        # 1️. DETERMINISTIC RESOLUTION
        # --------------------------------------------------

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

        # --------------------------------------------------
        # 2️. AI FALLBACK (ONLY AFTER DETERMINISTIC FAILURE)
        # --------------------------------------------------

        ai_service = get_ai_service()

        if ai_service:
            try:
                dom_snapshot = page.content()

                ai_result = ai_service.suggest_selectors(
                    definition.get("intent"),
                    dom_snapshot,
                    definition.get("constraints"),
                )

                # ai_result = ai_service.resolve(
                #     intent=f"Locate element '{element}' on page",
                #     constraints={
                #         "allowed_strategies": ["css", "role", "xpath"],
                #         "disallowed": ["nth-child", "index-based"],
                #     },
                #     dom_snapshot=dom_snapshot,
                # )

                suggestion = json.loads(ai_result)

                if suggestion.get("confidence", 0) >= 0.6:
                    strat = suggestion["locator"]

                #     ai_locator = LocatorResolver._locator_for_strategy(
                #         page,
                #         LocatorStrategy(
                #             kind=strat["strategy"],
                #             value=strat["value"],
                #             label="ai-fallback",
                #         ),
                #     )

                #     ai_locator.wait_for(state="visible", timeout=visible_timeout_ms)

                #     logger.warning(
                #         "AI self-healing used for locator %s (confidence=%.2f).",
                #         element,
                #         suggestion["confidence"],
                #     )

                # return ai_locator

                logger.warning(
                    "AI suggestion ignored for %s due to low confidence.",
                    element,
                )

            except Exception as ex:
                errors.append(
                    f"AI fallback failed for locator %s: %s {element} \n {ex}"
                )
                logger.exception(
                    "AI fallback failed for locator %s: %s",
                    element,
                    ex,
                )

        # --------------------------------------------------
        # 3️. FAILURE (UNCHANGED SEMANTICS)
        # --------------------------------------------------

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
