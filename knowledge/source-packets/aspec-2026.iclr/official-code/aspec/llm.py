"""Unified LLM module — config, base class, litellm provider, and cost tracking."""

from __future__ import annotations

import contextlib
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, NamedTuple, NoReturn

import litellm

litellm.suppress_debug_info = True
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, field_validator
from tenacity import (
    RetryCallState,
    after_log,
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

# ── Constants ────────────────────────────────────────────────────────

USE_CONFIG_TIMEOUT = 0  # sentinel: use llm.timeout from config
LLM_API_TIMEOUT = 300


# ── LLMType ──────────────────────────────────────────────────────────


class LLMType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CLAUDE = "claude"
    FIREWORKS = "fireworks"
    OPEN_LLM = "open_llm"
    GEMINI = "gemini"
    AZURE = "azure"
    OLLAMA = "ollama"
    DASHSCOPE = "dashscope"
    MOONSHOT = "moonshot"
    MISTRAL = "mistral"
    YI = "yi"
    OPENROUTER = "openrouter"
    BEDROCK = "bedrock"

    @classmethod
    def _missing_(cls, value: object) -> LLMType:
        return cls.OPENAI


# ── LLMConfig ────────────────────────────────────────────────────────


class LLMConfig(BaseModel):
    """Provider-agnostic LLM configuration."""

    api_key: str = "sk-"
    api_type: LLMType = LLMType.OPENAI
    base_url: str = "https://api.openai.com/v1"
    api_version: str | None = None

    model: str | None = None
    pricing_plan: str | None = None

    # Chat completion params
    max_token: int = 4096
    temperature: float = 0.0
    top_p: float = 1.0
    stop: str | None = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stream: bool = True
    seed: int | None = None
    timeout: int = 600

    # Bedrock
    region_name: str | None = None

    # Cost control
    calc_usage: bool = True

    # Messages
    use_system_prompt: bool = True

    @field_validator("api_key")
    @classmethod
    def check_llm_key(cls, v: str) -> str:
        if v in ["", None, "YOUR_API_KEY"]:
            raise ValueError("Please set your API key via environment variable or config.")
        return v

    @field_validator("timeout")
    @classmethod
    def check_timeout(cls, v: int | None) -> int:
        return v or LLM_API_TIMEOUT


# ── Cost tracking ────────────────────────────────────────────────────


class Costs(NamedTuple):
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost: float
    total_budget: float


class CostManager(BaseModel):
    """Track token usage and costs across LLM calls.

    Uses ``litellm.cost_per_token`` for pricing — no hardcoded tables.
    """

    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_budget: float = 0
    max_budget: float = 10.0
    total_cost: float = 0

    # Fallback per-token prices (USD) when litellm has no pricing data.
    # Roughly GPT-4o-mini tier — just enough to give the reward signal a cost term.
    FALLBACK_PROMPT_COST_PER_TOKEN: float = 0.15e-6
    FALLBACK_COMPLETION_COST_PER_TOKEN: float = 0.60e-6

    def update_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> None:
        if prompt_tokens + completion_tokens == 0 or not model:
            return
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        try:
            prompt_cost, completion_cost = litellm.cost_per_token(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
            self.total_cost += prompt_cost + completion_cost
        except Exception as e:
            logger.warning(f"litellm.cost_per_token failed for model={model}, using fallback pricing: {e}")
            fallback = (
                prompt_tokens * self.FALLBACK_PROMPT_COST_PER_TOKEN
                + completion_tokens * self.FALLBACK_COMPLETION_COST_PER_TOKEN
            )
            self.total_cost += fallback

    def get_costs(self) -> Costs:
        return Costs(
            self.total_prompt_tokens,
            self.total_completion_tokens,
            self.total_cost,
            self.total_budget,
        )


# ── BaseLLM ──────────────────────────────────────────────────────────


def _is_overload_or_rate_limit_error(e: Exception) -> bool:
    with contextlib.suppress(ImportError):
        from openai import RateLimitError

        if isinstance(e, RateLimitError):
            return True
    status = getattr(e, "status_code", None) or getattr(e, "status", None)
    if status in [429, 503, 502, 504]:
        return True
    error_msg = str(e).lower()
    indicators = [
        "503",
        "service unavailable",
        "overloaded",
        "rate limit",
        "quota",
        "too many requests",
        "retry",
        "busy",
        "capacity",
        "throttled",
    ]
    return any(ind in error_msg for ind in indicators)


def _log_and_reraise(retry_state: RetryCallState) -> NoReturn:
    logger.error(f"Retry attempts exhausted. Last exception: {retry_state.outcome.exception()}")
    raise retry_state.outcome.exception()


class BaseLLM(ABC):
    """Abstract base for LLM providers."""

    config: LLMConfig
    use_system_prompt: bool = True
    system_prompt: str = "You are a helpful assistant."

    aclient: AsyncOpenAI | None = None
    cost_manager: CostManager | None = None
    model: str | None = None
    pricing_plan: str | None = None

    @abstractmethod
    def __init__(self, config: LLMConfig) -> None:
        pass

    def _user_msg(self, msg: str, images: str | list[str] | None = None) -> dict[str, str | list[dict[str, Any]]]:
        if images:
            return self._user_msg_with_imgs(msg, images)
        return {"role": "user", "content": msg}

    def _user_msg_with_imgs(self, msg: str, images: str | list[str] | None) -> dict[str, str | list[dict[str, Any]]]:
        if isinstance(images, str):
            images = [images]
        content: list[dict[str, Any]] = [{"type": "text", "text": msg}]
        for image in images:
            url = image if image.startswith("http") else f"data:image/jpeg;base64,{image}"
            content.append({"type": "image_url", "image_url": {"url": url}})
        return {"role": "user", "content": content}

    def _assistant_msg(self, msg: str) -> dict[str, str]:
        return {"role": "assistant", "content": msg}

    def _system_msg(self, msg: str) -> dict[str, str]:
        return {"role": "system", "content": msg}

    def make_messages(self, prompt: str) -> list[dict[str, str]]:
        return [self._user_msg(prompt)]

    def format_msg(self, messages: str | list[dict[str, Any]] | list[str]) -> list[dict[str, Any]]:
        if not isinstance(messages, list):
            messages = [messages]
        processed: list[dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, str):
                processed.append({"role": "user", "content": msg})
            elif isinstance(msg, dict):
                processed.append(msg)
            else:
                raise ValueError(f"Unsupported message type: {type(msg).__name__}")
        return processed

    def _system_msgs(self, msgs: list[str]) -> list[dict[str, str]]:
        return [self._system_msg(msg) for msg in msgs]

    def _default_system_msg(self) -> dict[str, str]:
        return self._system_msg(self.system_prompt)

    def _update_costs(
        self,
        usage: dict[str, Any] | BaseModel,
        model: str | None = None,
        local_calc_usage: bool = True,
    ) -> None:
        calc_usage = self.config.calc_usage and local_calc_usage
        model = model or self.pricing_plan or self.model
        usage = usage.model_dump() if isinstance(usage, BaseModel) else usage
        if calc_usage and self.cost_manager and usage:
            try:
                prompt_tokens = int(usage.get("prompt_tokens", 0))
                completion_tokens = int(usage.get("completion_tokens", 0))
                self.cost_manager.update_cost(prompt_tokens, completion_tokens, model)
            except (TypeError, ValueError) as e:
                logger.error(f"Cost update failed: {e}")

    def get_costs(self) -> Costs:
        if not self.cost_manager:
            return Costs(0, 0, 0, 0)
        return self.cost_manager.get_costs()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random_exponential(min=1, max=60),
        after=after_log(logger, logger.level("WARNING").name),
        retry=(retry_if_exception_type(ConnectionError) | retry_if_exception(_is_overload_or_rate_limit_error)),
        retry_error_callback=_log_and_reraise,
    )
    async def aask(
        self,
        msg: str | list[dict[str, str]],
        system_msgs: list[str] | None = None,
        format_msgs: list[dict[str, str]] | None = None,
        images: str | list[str] | None = None,
        timeout: int = USE_CONFIG_TIMEOUT,
        stream: bool | None = None,
    ) -> str:
        if system_msgs:
            message = self._system_msgs(system_msgs)
        else:
            message = [self._default_system_msg()]
        if not self.use_system_prompt:
            message = []
        if format_msgs:
            message.extend(format_msgs)
        if isinstance(msg, str):
            message.append(self._user_msg(msg, images=images))
        else:
            message.extend(msg)
        if stream is None:
            stream = self.config.stream

        if stream:
            response = await self._achat_completion_stream(message, timeout=self.get_timeout(timeout))
        else:
            response = await self._achat_completion(message, timeout=self.get_timeout(timeout))
            response = self.get_choice_text(response)
        return response

    @abstractmethod
    async def _achat_completion(self, messages: list[dict[str, Any]], timeout: int = USE_CONFIG_TIMEOUT) -> Any:
        """Non-streaming chat completion."""

    @abstractmethod
    async def _achat_completion_stream(self, messages: list[dict[str, Any]], timeout: int = USE_CONFIG_TIMEOUT) -> str:
        """Streaming chat completion returning full text."""

    def get_choice_text(self, rsp: dict[str, Any]) -> str:
        return rsp.get("choices")[0]["message"]["content"]

    def get_timeout(self, timeout: int) -> int:
        return timeout or self.config.timeout or LLM_API_TIMEOUT


# ── litellm model name resolution ───────────────────────────────────

_LITELLM_PREFIX: dict[LLMType, str] = {
    LLMType.GEMINI: "gemini/",
    LLMType.ANTHROPIC: "anthropic/",
    LLMType.CLAUDE: "anthropic/",
    LLMType.AZURE: "azure/",
    LLMType.BEDROCK: "bedrock/",
    LLMType.OLLAMA: "ollama/",
    LLMType.FIREWORKS: "fireworks_ai/",
    LLMType.DASHSCOPE: "dashscope/",
    LLMType.MISTRAL: "mistral/",
    LLMType.OPENROUTER: "openrouter/",
}

_OPENAI_COMPAT_TYPES: set[LLMType] = {
    LLMType.OPENAI,
    LLMType.MOONSHOT,
    LLMType.YI,
    LLMType.OPEN_LLM,
}


def _resolve_litellm_model(config: LLMConfig) -> str:
    model = config.model or "gpt-4o-mini"
    prefix = _LITELLM_PREFIX.get(config.api_type, "")
    if prefix and not model.startswith(prefix):
        return f"{prefix}{model}"
    return model


# ── LiteLLM provider ────────────────────────────────────────────────


class LiteLLM(BaseLLM):
    """Single LLM provider backed by :pymod:`litellm`."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.model = config.model
        self.pricing_plan = config.pricing_plan or config.model
        self.cost_manager = None
        self.use_system_prompt = config.use_system_prompt
        self._litellm_model: str = _resolve_litellm_model(config)

    def _build_kwargs(self, messages: list[dict[str, Any]], timeout: int, stream: bool = False) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self._litellm_model,
            "messages": messages,
            "max_tokens": self.config.max_token,
            "temperature": self.config.temperature,
            "timeout": timeout,
            "stream": stream,
        }
        if self.config.api_key and self.config.api_key != "sk-":
            kwargs["api_key"] = self.config.api_key

        if self.config.api_type in _OPENAI_COMPAT_TYPES:
            base_url = self.config.base_url
            if base_url and base_url != "https://api.openai.com/v1":
                kwargs["api_base"] = base_url

        if self.config.api_type == LLMType.AZURE:
            if self.config.base_url:
                kwargs["api_base"] = self.config.base_url
            if self.config.api_version:
                kwargs["api_version"] = self.config.api_version

        if self.config.top_p != 1.0:
            kwargs["top_p"] = self.config.top_p
        if self.config.presence_penalty != 0.0:
            kwargs["presence_penalty"] = self.config.presence_penalty
        if self.config.frequency_penalty != 0.0:
            kwargs["frequency_penalty"] = self.config.frequency_penalty
        if self.config.seed is not None:
            kwargs["seed"] = self.config.seed
        if self.config.stop is not None:
            kwargs["stop"] = self.config.stop

        return kwargs

    async def _achat_completion(self, messages: list[dict[str, Any]], timeout: int = USE_CONFIG_TIMEOUT) -> Any:
        kwargs = self._build_kwargs(messages, self.get_timeout(timeout))
        response = await litellm.acompletion(**kwargs)
        usage = response.get("usage", {}) if isinstance(response, dict) else getattr(response, "usage", None)
        if usage is not None:
            self._update_costs(usage)
        return response

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token count: ~4 chars per token for English text."""
        return max(1, len(text) // 4)

    async def _achat_completion_stream(self, messages: list[dict[str, Any]], timeout: int = USE_CONFIG_TIMEOUT) -> str:
        kwargs = self._build_kwargs(messages, self.get_timeout(timeout), stream=True)
        kwargs["stream_options"] = {"include_usage": True}
        collected: list[str] = []
        usage: dict[str, Any] | BaseModel | None = None
        response = await litellm.acompletion(**kwargs)
        async for chunk in response:
            delta = ""
            if isinstance(chunk, dict):
                choices = chunk.get("choices", [{}])
                if choices:
                    delta = choices[0].get("delta", {}).get("content", "") or ""
                usage = chunk.get("usage") or usage
            else:
                choices = getattr(chunk, "choices", [])
                if choices:
                    d = choices[0].delta
                    delta = getattr(d, "content", "") or ""
                usage = getattr(chunk, "usage", None) or usage
            if delta:
                collected.append(delta)

        output_text = "".join(collected)
        if usage is not None:
            self._update_costs(usage)
        else:
            # Provider didn't return usage — estimate from message/output lengths
            prompt_text = " ".join(m.get("content", "") for m in messages)
            self._update_costs(
                {
                    "prompt_tokens": self._estimate_tokens(prompt_text),
                    "completion_tokens": self._estimate_tokens(output_text),
                }
            )
        return output_text

    def get_choice_text(self, rsp: Any) -> str:
        try:
            return rsp.choices[0].message.content or ""
        except (AttributeError, IndexError, TypeError):
            pass
        try:
            return rsp["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return ""


# ── Factory functions ────────────────────────────────────────────────


def create_llm_instance(config: LLMConfig) -> BaseLLM:
    """Create an LLM instance from config."""
    return LiteLLM(config)
