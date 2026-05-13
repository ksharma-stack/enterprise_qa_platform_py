"""
Azure OpenAI Adapter

Single responsibility:
- Communicate with Azure OpenAI
- Remain framework-agnostic
"""

from openai import AzureOpenAI


class AzureOpenAIAdapter1:
    """
    Thin wrapper over Azure OpenAI client (Wraps open.AzureOpenAI).
    All configs is inected at construction - no global state.
    """

    def __init__(self, config):
        self._client = AzureOpenAI(
            api_key=config.api_key,
            api_version=config.api_version,
            azure_endpoint=config.endpoint,
        )
        self._deployment = config.deployment
        self._temperature = config.temperature
        self._max_tokens = config.max_tokens

    def complete(self, messages: list[dict]) -> str:
        """
        Execute a chat completion request.
        """
        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return response.choices[0].message.content
