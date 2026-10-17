# file: l0_memory/llm_interface/factory.py

from .base_config import BaseLlmConfig
from .volc_api_client import VolcClient
from .openai_api_client import OpenAIClient
from .bailian_api_client import BaiLianClient
from .gemini_proxy_client import GeminiProxyClient
from .gemini_api_client import GeminiClient


class LlmFactory:
    """Factory class to create L0 LLM client instances."""

    provider_map = {
        "volc": VolcClient,
        "openai": OpenAIClient,
        "bailian": BaiLianClient,
        "gemini_proxy": GeminiProxyClient,
        "gemini": GeminiClient,
        # Register new providers here
    }

    @classmethod
    def create(cls, provider: str, config: dict, client_name: str):
        """
        Creates and returns an LLM client.

        Args:
            provider: The name of the LLM provider.
            config: Configuration dictionary.
            client_name: A unique name for the client instance.
        """
        llm_class = cls.provider_map.get(provider)
        if not llm_class:
            raise ValueError(f"Unknown L0 LLM provider: {provider}")

        # Convert dictionary configuration to a config object
        llm_config = BaseLlmConfig(**config)

        # Instantiate and return the client
        return llm_class(config=llm_config, client_name=client_name)