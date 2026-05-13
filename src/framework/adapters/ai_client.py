"""
Concrete AI client implementation.
This example is deterministic and mock-friendly.
"""

from __future__ import annotations
import os

# from abc import abstractmethod

from openai import AzureOpenAI, OpenAI
from src.framework.contracts.ai_client_contract import AIClientContract


class AzureOpenAIClient(AIClientContract):
    """
    Wraps open.AzureOpenAI.
    All configs is inejcted at construction - no global state.
    """

    def __init__(self, config) -> None:

        self._client = AzureOpenAI(
            azure_endpoint=config.ai.azure_openai.endpoint,
            api_key=os.getenv(config.ai.azure_openai.api_key),
            api_version=config.ai.azure_openai.api_version,
        )
        self._deployment = config.ai.azure_openai.deployment
        self._temperature = config.ai.azure_openai.temperature
        self._max_tokens = config.ai.azure_openai.max_tokens

    def complete(self, prompt: str) -> str:
        """
        Execute a chat completion request.
        Submit prompt to AI model.
        """
        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=prompt,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        print(f"{response}")
        return response.choices[0].message.content

    def is_ready(self):
        """Return True if ai client is initialized."""
        return self._client is not None


class OpenAIClient(AIClientContract):
    """
    Wraps open.AzureOpenAI.
    All configs is inected at construction - no global state.
    """

    def __init__(self, config) -> None:

        self._client = OpenAI(
            base_url=config.ai.azure_openai_model.endpoint,
            api_key=os.getenv(config.ai.azure_openai_model.api_key),
        )
        self._deployment = config.ai.azure_openai_model.deployment
        self._temperature = config.ai.azure_openai_model.temperature
        self._max_tokens = config.ai.azure_openai_model.max_tokens

    def complete(self, prompt: str) -> str:
        """
        Execute a chat completion request.
        Submit prompt to AI model.
        """
        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=prompt,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        print(f"{response}")
        return response.choices[0].message.content

    def is_ready(self):
        """Retunr True if ai client is initialized."""
        return self._client is not None
