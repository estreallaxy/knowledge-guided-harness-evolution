# file: l0_memory/embedding_interface/factory.py

from .base_config import BaseEmbeddingConfig
from .local_client import LocalEmbeddingClient
from .volc_client import VolcEmbeddingClient
from .gemini_client import GeminiEmbeddingClient
from .openai_client import OpenAIEmbeddingClient


class EmbeddingFactory:
    """Factory class to create embedding client instances based on the provider."""

    provider_map = {
        "local": LocalEmbeddingClient,
        "volc": VolcEmbeddingClient,
        "gemini": GeminiEmbeddingClient,
        "openai": OpenAIEmbeddingClient,
    }

    @classmethod
    def create(cls, provider: str, config_dict: dict):
        """
        Creates and returns an embedding client.

        Args:
            provider: The name of the embedding provider.
            config_dict: Dictionary containing configuration parameters.
        """
        embedder_class = cls.provider_map.get(provider)
        if not embedder_class:
            raise ValueError(f"Unknown Embedding provider: {provider}")

        embedder_config = BaseEmbeddingConfig(**config_dict)
        return embedder_class(config=embedder_config)