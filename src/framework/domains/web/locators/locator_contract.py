"""
Normalize enterprise locator YAML (primary / fallback / healing) into runtime strategy lists.
Supports legacy flat locators: role, name, css, xpath.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

StrategyKind = Literal["a11y", "css", "xpath"]

RESERVED_ELEMENT_KEYS = frozenset({"page_metadata"})


@dataclass(frozen=True)
class LocatorStrategy:
    """One ordered resolution attempt."""

    kind: StrategyKind
    label: str
    role: str | None = None
    name: str | None = None
    selector: str | None = None


@dataclass(frozen=True)
class HealingRuntime:
    """Runtime configuration for healing strategies."""

    enabled: bool
    mode: str
    max_strategies: int | None


def _norm_strategy(s: str | None) -> str:
    return (s or "").strip().lower()


def _is_enterprise_element(defn: dict[str, Any]) -> bool:
    return isinstance(defn, dict) and (
        "primary" in defn or isinstance(defn.get("fallback"), list)
    )


def _strategy_from_primary_block(primary: dict[str, Any]) -> LocatorStrategy | None:
    if not primary:
        return None
    st = _norm_strategy(primary.get("strategy"))
    if st in ("accessibility", "a11y", "role"):
        a11y = primary.get("a11y") or {}
        role = a11y.get("role")
        name = a11y.get("name")
        if not role:
            return None
        return LocatorStrategy(
            kind="a11y",
            label="primary",
            role=str(role),
            name=str(name) if name is not None else None,
        )
    if st == "css":
        val = primary.get("value")
        if not val:
            return None
        return LocatorStrategy(kind="css", label="primary", selector=str(val))
    if st == "xpath":
        val = primary.get("value")
        if not val:
            return None
        return LocatorStrategy(kind="xpath", label="primary", selector=str(val))
    return None


def _strategy_from_fallback_item(
    item: dict[str, Any], index: int
) -> LocatorStrategy | None:
    if not item:
        return None
    st = _norm_strategy(item.get("strategy"))
    label = f"fallback_{index}"
    if st == "css":
        val = item.get("value")
        if not val:
            return None
        return LocatorStrategy(kind="css", label=label, selector=str(val))
    if st == "xpath":
        val = item.get("value")
        if not val:
            return None
        return LocatorStrategy(kind="xpath", label=label, selector=str(val))
    if st in ("accessibility", "a11y", "role"):
        # Rare for fallbacks but supported
        role = item.get("role")
        name = item.get("name")
        if not role:
            return None
        return LocatorStrategy(
            kind="a11y",
            label=label,
            role=str(role),
            name=str(name) if name is not None else None,
        )
    return None


def _legacy_strategies(defn: dict[str, Any]) -> list[LocatorStrategy]:
    """Flat Playwright-style dict: role + optional name, css, xpath."""
    out: list[LocatorStrategy] = []
    if "role" in defn:
        out.append(
            LocatorStrategy(
                kind="a11y",
                label="legacy_role",
                role=str(defn["role"]),
                name=str(defn["name"]) if defn.get("name") is not None else None,
            )
        )
    if "css" in defn:
        out.append(
            LocatorStrategy(kind="css", label="legacy_css", selector=str(defn["css"]))
        )
    if "xpath" in defn:
        out.append(
            LocatorStrategy(
                kind="xpath", label="legacy_xpath", selector=str(defn["xpath"])
            )
        )
    return out


def build_strategy_plan(
    defn: dict[str, Any],
) -> tuple[list[LocatorStrategy], HealingRuntime]:
    """
    Returns ordered strategies and healing flags for logging / limits.
    """
    healing = defn.get("healing") if isinstance(defn, dict) else None
    healing = healing if isinstance(healing, dict) else {}
    enabled = bool(healing.get("enabled", True))
    mode = str(healing.get("mode", "auto")).strip().lower()
    raw_max = healing.get("max_attempts")
    max_strategies: int | None
    if raw_max is None:
        max_strategies = None
    else:
        try:
            max_strategies = max(1, int(raw_max))
        except (TypeError, ValueError):
            max_strategies = None

    strategies: list[LocatorStrategy] = []

    if not isinstance(defn, dict):
        return [], HealingRuntime(enabled=False, mode="off", max_strategies=None)

    if _is_enterprise_element(defn):
        p = _strategy_from_primary_block(defn.get("primary") or {})
        if p:
            strategies.append(p)
        if enabled and mode != "off":
            for i, fb in enumerate(defn.get("fallback") or []):
                if isinstance(fb, dict):
                    s = _strategy_from_fallback_item(fb, i)
                    if s:
                        strategies.append(s)
    else:
        strategies.extend(_legacy_strategies(defn))

    if max_strategies is not None:
        max_strategies = len(strategies)

    strategies = strategies[:max_strategies]

    return strategies, HealingRuntime(
        enabled=enabled,
        mode=mode,
        max_strategies=max_strategies,
    )


def is_locator_element_key(key: str) -> bool:
    return key not in RESERVED_ELEMENT_KEYS
