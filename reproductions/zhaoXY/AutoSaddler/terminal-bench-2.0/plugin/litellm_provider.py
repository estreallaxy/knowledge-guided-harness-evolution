"""Provider factory that plugs the litellm transport into the V2 engine.

Upstream's provider factories are `Callable[..., AgentProvider]` invoked as
``factory(ledger=..., settings=...)`` from ``build_runtime``. None of the shipped
types can reach DeepSeek, so the TB2 unit registers this one in its own registry copy
(see ``run_autosaddler_tb2.py``) instead of patching the vendored engine.

Provider settings keys (exact): ``model``, ``api_key_env``, ``temperature``, ``max_turns``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from autosaddler.v2.core.domain import JsonValue
from autosaddler.v2.providers.base import BaseAgentProvider
from autosaddler.v2.providers.workspace_renderer import (
    CLAUDE_CAPABILITY_TO_TOOLS,
    WorkspaceRenderer,
)

from litellm_transport import LitellmTransport, LitellmTransportSettings

_EXPECTED_KEYS = {"model", "api_key_env", "temperature", "max_turns"}


def build_litellm_provider(*, ledger: Any = None, settings: Mapping[str, JsonValue]) -> BaseAgentProvider:
    """Build the provider; ``ledger`` is accepted for signature parity and ignored."""
    del ledger
    extra = sorted(set(settings) - _EXPECTED_KEYS)
    if extra:
        raise ValueError(f"Invalid keys at provider.settings for litellm: extra={extra}")
    model = settings.get("model")
    if not isinstance(model, str) or not model:
        raise ValueError("provider.settings.model must be a non-empty string")
    temperature = settings.get("temperature", 0.7)
    max_turns = settings.get("max_turns", 40)
    if not isinstance(temperature, (int, float)):
        raise ValueError("provider.settings.temperature must be a number")
    if not isinstance(max_turns, int) or max_turns < 1:
        raise ValueError("provider.settings.max_turns must be a positive integer")
    api_key_env = settings.get("api_key_env", "DEEPSEEK_API_KEY")
    if not isinstance(api_key_env, str) or not api_key_env:
        raise ValueError("provider.settings.api_key_env must be a non-empty string")

    renderer = WorkspaceRenderer(
        provider="litellm",
        instruction_file="AGENTS.md",
        skill_directory=".agents/skills",
        capability_tools=CLAUDE_CAPABILITY_TO_TOOLS,
    )
    transport = LitellmTransport(
        LitellmTransportSettings(
            model=model,
            api_key_env=api_key_env,
            temperature=float(temperature),
            max_turns=max_turns,
        )
    )
    return BaseAgentProvider(renderer, transport)
