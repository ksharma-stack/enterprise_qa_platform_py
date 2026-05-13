"""
Defines contracts for AI client and self-healing services.
These contracts must not import Playwright or framework-specific code.
"""

from __future__ import annotations

from abc import ABC
from typing import Protocol, Dict, Any


class AIClientContract(ABC):
    """
    Stable interface every AI provider must staisfy
    Tests depend only on this - never on a concrete class.
    """

    # @abstractmethod
    def complete(self, prompt: str) -> str:
        """
        Execute a prompt and return the raw model response.
        :param prompt: Fully constructed prompt
        :return: Model output as string
        """

    # @abstractmethod
    def is_ready(self) -> bool:
        """Returns True when the client initialized successfully."""


class SelfHealingService(Protocol):
    """
    Contract for AI-driven self-healing logic.
    """

    def heal(
        self,
        *,
        dom_snapshot: str,
        intent: str,
        constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Attempt to resolve a new locator.

        :param dom_snapshot: Serialized DOM / accessibility snapshot
        :param intent: Business or test intent (e.g. "Login username field")
        :param constraints: Allowed locator strategies, tags, etc.
        :return: New locator payload (contract-safe)
        """
