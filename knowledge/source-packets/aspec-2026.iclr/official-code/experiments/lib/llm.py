"""Shared LLM configuration utilities."""

import os
from typing import Optional

from aspec.llm import LLMConfig


API_DEFAULTS = {
    "gemini": {
        "env_key": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/",
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "base_url": None,
    },
    "openrouter": {
        "env_key": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1/",
    },
}

DEFAULT_MODEL = "gemini-2.0-flash"


def create_llm_config(
    model: str = DEFAULT_MODEL,
    api_type: str = "gemini",
    api_key: Optional[str] = None,
) -> LLMConfig:
    """Create an LLMConfig for the given API type."""
    defaults = API_DEFAULTS.get(api_type, {})
    if api_key is None:
        env_key = defaults.get("env_key", "")
        api_key = os.getenv(env_key, "")

    kwargs = dict(api_key=api_key, model=model, api_type=api_type)
    base_url = defaults.get("base_url")
    if base_url:
        kwargs["base_url"] = base_url
    return LLMConfig(**kwargs)
