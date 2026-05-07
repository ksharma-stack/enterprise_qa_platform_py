"""
Enterprise Locator Contract
---------------------------
- YAML-backed locator definitions treated as versioned APIs
- Enforces governance, healing rules, and backward compatibility
"""

from datetime import date
from typing import List, Optional, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------------------------------------------------------
# Shared base (strict, future-proof)
# ---------------------------------------------------------
class StrictModel(BaseModel):
    """Shared base (strict, future-proof)"""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


# ------------------------------------------------------------------
# CONTRACT ROOT
# ------------------------------------------------------------------


class ContractSpec(StrictModel):
    """Defines the top-level contract specification and schema guarantees."""

    schema_version: str
    backwards_compatible: bool = True
    locator_spec: Literal["enterprise-a11y-selfhealing"]


# ------------------------------------------------------------------
# PAGE METADATA
# ------------------------------------------------------------------


class PageMetadata(StrictModel):
    """Describes ownership, lifecycle, and policy information for a page."""

    app: str
    page: str
    owner: str
    review_cycle_days: int
    version: str
    last_verified: date
    healing_policy: Literal["off", "cautious", "aggressive"]
    channel_support: List[Literal["web", "desktop"]]


# ------------------------------------------------------------------
# VERSIONING & GOVERNANCE
# ------------------------------------------------------------------


class VersionPolicy(StrictModel):
    """Defines rules governing version evolution of locator elements."""

    major_change_requires_approval: bool
    minor_on_fallback_change: bool
    patch_on_metadata_only: bool


class VersionInfo(StrictModel):
    """Represents the current version and its governing policy."""

    current: str
    policy: VersionPolicy


# ------------------------------------------------------------------
# INTENT & ACCESSIBILITY
# ------------------------------------------------------------------


class IntentContract(StrictModel):
    """Declares the semantic intent of the UI element."""

    role: Literal["textbox", "button", "link", "checkbox"]
    name: str
    placeholder: Optional[str] = None
    control_type: Optional[str] = Field(
        None, description="Desktop control type (Win32/UIA)"
    )


class AccessibilityLocator(StrictModel):
    """Accessibility-first locator definition (ARIA-driven)."""

    role: str
    name: str
    aria_required: bool = False


# ------------------------------------------------------------------
# LOCATOR STRATEGIES
# ------------------------------------------------------------------


class PrimaryLocator(StrictModel):
    """Defines the primary locator strategy (currently accessibility-only)."""

    strategy: Literal["accessibility"]
    a11y: AccessibilityLocator


class FallbackLocator(StrictModel):
    """Defines a fallback locator with an associated confidence score."""

    strategy: Literal["css", "xpath"]
    value: str
    confidence: float = Field(ge=0.0, le=1.0)


# ---------------------------------------------------------
# Selector definitions (domain-agnostic)
# ---------------------------------------------------------
class WebSelector(StrictModel):
    """Web selector"""

    css: Optional[str] = None
    xpath: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None


class DesktopSelector(StrictModel):
    """Desktop selector"""

    automation_id: Optional[str] = None
    title: Optional[str] = None
    control_type: Optional[str] = None
    class_name: Optional[str] = None


ChannelSelector = Union[WebSelector, DesktopSelector]


# ------------------------------------------------------------------
# SELF‑HEALING GOVERNANCE
# ------------------------------------------------------------------


class HealingPolicy(StrictModel):
    """Governs self-healing behavior, approval requirements, and limits."""

    enabled: bool
    mode: Literal["auto", "suggest-only", "off"]
    max_attempts: int
    approval_required: bool
    approvers: List[str]

    @model_validator(mode="after")
    def validate_approval(self):
        """Ensures approvers are present if approval is required."""
        if self.approval_required and not self.approvers:
            raise ValueError("Approval required but no approvers defined")
        return self


# ------------------------------------------------------------------
# RUNTIME CONSTRAINTS
# ------------------------------------------------------------------


class RuntimeConstraints(StrictModel):
    """Defines runtime expectations such as visibility and uniqueness."""

    visibility: Literal["visible", "hidden"]
    unique: bool


# ------------------------------------------------------------------
# AUDIT & RUNTIME METADATA
# ------------------------------------------------------------------


class StaticMetadata(StrictModel):
    """Immutable audit metadata captured at creation or approved changes."""

    element_version_history: List[str]
    created_on: date
    change_reason: str


class RuntimeMetadata(StrictModel):
    """Runtime telemetry updated during locator usage and healing."""

    stability_score: int = Field(ge=0, le=100)
    last_failure: Optional[str]
    healing_attempts: int
    healing_success_rate: float = Field(ge=0.0, le=1.0)
    last_used_selector: Literal["primary", "fallback"]


class ElementMetadata(StrictModel):
    """Combines static audit metadata with runtime telemetry."""

    static: StaticMetadata
    runtime: RuntimeMetadata


# ------------------------------------------------------------------
# LOCATOR ELEMENT CONTRACT
# ------------------------------------------------------------------


class LocatorElement(StrictModel):
    """Represents a fully governed, versioned, self-healable locator element."""

    version: VersionInfo
    intent: IntentContract
    primary: PrimaryLocator
    fallback: List[FallbackLocator]
    healing: HealingPolicy
    constraints: RuntimeConstraints
    metadata: ElementMetadata

    @model_validator(mode="after")
    def validate_fallback_confidence_order(self):
        """Ensures fallback locators are ordered by descending confidence."""
        confidences = [fb.confidence for fb in self.fallback]
        if confidences != sorted(confidences, reverse=True):
            raise ValueError("Fallback locators must be ordered by confidence DESC")
        return self


# ------------------------------------------------------------------
# PAGE CONTRACT
# ------------------------------------------------------------------


class LoginPageContract(StrictModel):
    """Contract definition for the Login page and its elements."""

    page_metadata: PageMetadata
    username: LocatorElement


# ------------------------------------------------------------------
# FULL YAML CONTRACT ROOT
# ------------------------------------------------------------------


class LocatorContract(StrictModel):
    """Root model representing the full locator YAML contract."""

    contract: ContractSpec
    loginpage: LoginPageContract
