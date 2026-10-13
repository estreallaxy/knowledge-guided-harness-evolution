"""One asynchronous, non-streaming OpenRouter request per call.

API contract: https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion
Retries belong to the discussion engine. Credentials never enter saved config.
"""

import asyncio
import base64
from copy import deepcopy
import json
import math
import os
from dataclasses import dataclass
from datetime import timezone
from email.utils import parsedate_to_datetime
from time import time
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from .types import Completion, ModelError, Request


ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def _image_url(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelError("Image input requires a nonempty local path or HTTP(S) URL")
    url = urlsplit(value)
    if url.scheme in ("http", "https") and url.netloc:
        return value
    if url.scheme:
        raise ModelError("Image inputs must use local paths or HTTP(S) URLs")
    path = Path(value)
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".gif": "image/gif"}.get(path.suffix.lower())
    if mime is None:
        raise ModelError("Local images must be PNG, JPEG, WebP, or GIF files")
    try:
        content = path.read_bytes()
    except OSError:
        raise ModelError("Cannot read local image file") from None
    valid = {
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/gif": content.startswith((b"GIF87a", b"GIF89a")),
        "image/webp": content.startswith(b"RIFF") and content[8:12] == b"WEBP",
    }
    if not valid[mime]:
        raise ModelError("Local image bytes do not match its supported image format")
    return f"data:{mime};base64," + base64.b64encode(content).decode("ascii")


def _messages(messages) -> list[dict]:
    """Encode image bytes only in the outgoing payload, never in stored requests."""
    result = []
    for message in messages:
        content = deepcopy(message.content)
        if isinstance(content, list):
            for part in content:
                if not isinstance(part, dict):
                    raise ModelError("Multimodal content parts must be objects")
                if part.get("type") == "text" and isinstance(part.get("text"), str):
                    continue
                if part.get("type") != "image_url" or not isinstance(part.get("image_url"), dict):
                    raise ModelError("Only text and image_url content parts are supported")
                part["image_url"]["url"] = _image_url(part["image_url"].get("url"))
        elif not isinstance(content, str):
            raise ModelError("Message content must be text or multimodal content parts")
        result.append({"role": message.role, "content": content})
    return result


def _finite_number(value: object) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _settings(value: object, allowed: tuple[str, ...], name: str) -> dict:
    if not isinstance(value, dict) or set(value) - set(allowed):
        raise ValueError(f"{name} must be an object containing only supported fields")
    return value


@dataclass(frozen=True)
class ModelConfig:
    model: str
    temperature: float | None = 0.25
    max_completion_tokens: int = 2048
    timeout: float = 60
    seed: int | None = None
    reasoning: dict | None = None
    provider: dict | None = None
    output_format: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("model must be a nonempty OpenRouter model ID")
        if not _finite_number(self.timeout) or self.timeout <= 0:
            raise ValueError("timeout must be a positive finite number")
        if self.temperature is not None and (
            not _finite_number(self.temperature) or not 0 <= self.temperature <= 2
        ):
            raise ValueError("temperature must be between 0 and 2, or null")
        if type(self.max_completion_tokens) is not int or self.max_completion_tokens < 1:
            raise ValueError("max_completion_tokens must be a positive integer")
        if self.seed is not None and type(self.seed) is not int:
            raise ValueError("seed must be an integer or null")
        if self.output_format not in (None, "json_object", "json_schema"):
            raise ValueError("output_format must be json_object, json_schema, or null")
        if self.reasoning is not None:
            reasoning = _settings(self.reasoning, ("effort", "enabled"), "reasoning")
            if "effort" in reasoning and reasoning["effort"] not in ("max", "xhigh", "high", "medium", "low", "minimal", "none"):
                raise ValueError("reasoning.effort must be max, xhigh, high, medium, low, minimal, or none")
            if "enabled" in reasoning and type(reasoning["enabled"]) is not bool:
                raise ValueError("reasoning.enabled must be a boolean")
            if "enabled" in reasoning and "effort" in reasoning:
                if reasoning["enabled"] == (reasoning["effort"] == "none"):
                    raise ValueError("reasoning.enabled and reasoning.effort conflict")
            object.__setattr__(self, "reasoning", deepcopy(reasoning))
        if self.provider is not None:
            provider = _settings(self.provider, ("only", "allow_fallbacks", "sort", "max_price"), "provider")
            if "only" in provider and (not isinstance(provider["only"], list) or not provider["only"]
                    or any(not isinstance(item, str) or not item.strip() for item in provider["only"])):
                raise ValueError("provider.only must be a nonempty list of provider identifiers")
            if "allow_fallbacks" in provider and type(provider["allow_fallbacks"]) is not bool:
                raise ValueError("provider.allow_fallbacks must be a boolean")
            if "sort" in provider and provider["sort"] not in ("price", "latency", "throughput"):
                raise ValueError("provider.sort must be price, latency, or throughput")
            if "max_price" in provider:
                prices = _settings(provider["max_price"], ("prompt", "completion", "request", "image"), "provider.max_price")
                if any(not _finite_number(value) or value < 0 for value in prices.values()):
                    raise ValueError("provider.max_price values must be finite nonnegative numbers")
            object.__setattr__(self, "provider", deepcopy(provider))


def _retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        seconds = float(value)
        return seconds if math.isfinite(seconds) and seconds >= 0 else None
    except ValueError:
        pass
    try:
        date = parsedate_to_datetime(value)
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        return max(0.0, date.timestamp() - time())
    except (ValueError, TypeError, OverflowError):
        return None


def _status_error(status: int, retry_after: str | None = None, error: object = None) -> ModelError:
    """Classify known failures using fixed text; never echo remote error details."""
    retryable = status in (408, 429) or 500 <= status < 600
    classification = ""
    if isinstance(error, dict):
        message = error.get("message")
        message = message.lower() if isinstance(message, str) else ""
        metadata = error.get("metadata")
        source = metadata.get("limit_source") if isinstance(metadata, dict) else None
        daily_markers = ("free-models-per-day", "free models per day", "free requests per day",
                         "free daily request limit", "daily free request limit", "free model daily limit")
        if status == 429 and (source in ("free_models_per_day", "free-models-per-day", "free_daily_limit")
                              or any(marker in message for marker in daily_markers)):
            classification = "free daily request limit reached"
            retryable = False
        elif status == 429 and source == "upstream_provider_shared_pool":
            classification = "upstream provider capacity exhausted"
        elif status == 403 and (("only available" in message and "agentic harness" in message)
                                or "restricted to approved applications" in message):
            classification = "restricted to approved applications"
    return ModelError(
        f"OpenRouter HTTP {status}" + (f": {classification}" if classification else ""),
        retryable=retryable,
        retry_after=_retry_after(retry_after),
    )


def _body_error(error: object, retry_after: str | None) -> ModelError:
    code = error.get("code") if isinstance(error, dict) else None
    if isinstance(code, str) and code.isascii() and code.isdigit() and len(code) == 3:
        code = int(code)
    if type(code) is int and 100 <= code < 600:
        return _status_error(code, retry_after, error)
    return ModelError("OpenRouter returned an API error")


def _string(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _usage(value: object) -> dict[str, int | float]:
    """Keep documented numeric counts/costs, never arbitrary response metadata."""
    if not isinstance(value, dict):
        return {}
    allowed = {
        "": ("prompt_tokens", "completion_tokens", "total_tokens", "cost"),
        "prompt_tokens_details": ("cached_tokens", "cache_write_tokens", "audio_tokens", "video_tokens"),
        "completion_tokens_details": ("reasoning_tokens", "audio_tokens", "image_tokens"),
        "cost_details": ("upstream_inference_cost", "upstream_inference_prompt_cost", "upstream_inference_completions_cost", "server_tool_cost"),
    }
    result = {}
    for group, keys in allowed.items():
        source = value.get(group, {}) if group else value
        if isinstance(source, dict):
            for key in keys:
                number = source.get(key)
                if _finite_number(number) and number >= 0:
                    result[f"{group}.{key}" if group else key] = number
    return result


def _provider(data: dict) -> str | None:
    direct = _string(data.get("provider"))
    if direct:
        return direct
    metadata = data.get("openrouter_metadata")
    endpoints = metadata.get("endpoints") if isinstance(metadata, dict) else None
    available = endpoints.get("available") if isinstance(endpoints, dict) else None
    if isinstance(available, list):
        selected = [item for item in available if isinstance(item, dict) and item.get("selected") is True]
        if len(selected) == 1:
            return _string(selected[0].get("provider"))
    return None


def _recorded_completion(data: dict) -> Completion:
    """Retain known completion metadata even when the output cannot be used."""
    choices = data.get("choices")
    choice = choices[0] if isinstance(choices, list) and len(choices) == 1 and isinstance(choices[0], dict) else {}
    message = choice.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    return Completion(
        text=content if isinstance(content, str) else "", model=_string(data.get("model")),
        provider=_provider(data), usage=_usage(data.get("usage")), generation_id=_string(data.get("id")),
        finish_reason=_string(choice.get("finish_reason")),
    )


def _completion(body: bytes, retry_after: str | None) -> Completion:
    try:
        data = json.loads(body)
    except (ValueError, UnicodeError):
        raise ModelError("OpenRouter returned invalid JSON") from None
    if not isinstance(data, dict):
        raise ModelError("OpenRouter returned an invalid response object")
    recorded = _recorded_completion(data)
    try:
        if data.get("error") is not None:
            raise _body_error(data["error"], retry_after)
        choices = data.get("choices")
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise ModelError("OpenRouter response must contain one completion choice")
        choice = choices[0]
        if choice.get("error") is not None:
            raise _body_error(choice["error"], retry_after)
        reason = choice.get("finish_reason")
        if reason == "length":
            raise ModelError("OpenRouter completion was truncated; increase max_completion_tokens")
        if reason in ("content_filter", "refusal"):
            raise ModelError("OpenRouter model refused the request")
        if reason == "error":
            raise ModelError("OpenRouter generation failed", retryable=True)
        if reason == "tool_calls":
            raise ModelError("OpenRouter returned tool calls instead of an answer")
        message = choice.get("message")
        if not isinstance(message, dict):
            raise ModelError("OpenRouter response has no assistant message")
        if message.get("refusal"):
            raise ModelError("OpenRouter model refused the request")
        if message.get("role") != "assistant":
            raise ModelError("OpenRouter response has an invalid message role")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ModelError("OpenRouter returned empty or non-text content")
    except ModelError as error:
        # Never attach remote error.message or metadata.raw. Only normal assistant
        # content and documented numeric usage/metadata reach the saved Call.
        error.completion = recorded
        raise
    return recorded


class OpenRouterModel:
    def __init__(
        self,
        config: ModelConfig,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        key = os.environ.get("OPENROUTER_API_KEY") if api_key is None else api_key
        if not isinstance(key, str) or not key.strip():
            raise ValueError("OPENROUTER_API_KEY is required")
        key = key.strip()
        if not key.isascii() or not key.isprintable() or any(char.isspace() for char in key):
            raise ValueError("OPENROUTER_API_KEY contains invalid characters")
        self.config = config
        self.name = config.model
        self._api_key = key
        self._owns_client = client is None
        self._client = client if client is not None else httpx.AsyncClient(follow_redirects=False)

    async def __aenter__(self) -> "OpenRouterModel":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Release an owned client; shared clients stay with their caller."""
        if self._owns_client:
            await self._client.aclose()

    async def generate(self, request: Request) -> Completion:
        # Reading/encoding local frames must not block other model requests.
        messages = await asyncio.to_thread(_messages, request.messages)
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "max_completion_tokens": self.config.max_completion_tokens,
            "provider": {"require_parameters": True, **deepcopy(self.config.provider or {})},
        }
        if self.config.reasoning is not None:
            payload["reasoning"] = deepcopy(self.config.reasoning)
        if self.config.output_format == "json_object":
            payload["response_format"] = {"type": "json_object"}
        elif self.config.output_format == "json_schema":
            answer_schema = {"type": "string"}
            if request.answer_type == "choice":
                if not request.choices:
                    raise ModelError("Structured choice output requires available option labels")
                answer_schema["enum"] = list(request.choices)
            elif request.answer_type != "number":
                raise ModelError("Structured output requires number or choice answer_type")
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "discussion_answer", "strict": True,
                    "schema": {"type": "object", "additionalProperties": False,
                               "required": ["reasons", "answer"],
                               "properties": {"reasons": {"type": "string"}, "answer": answer_schema}},
                },
            }
        if self.config.temperature is not None:
            payload["temperature"] = self.config.temperature
        if self.config.seed is not None:
            payload["seed"] = self.config.seed
        try:
            response = await self._client.post(
                ENDPOINT,
                content=json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8"),
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json",
                         "X-OpenRouter-Metadata": "enabled"},
                timeout=self.config.timeout,
                follow_redirects=False,
            )
        except httpx.RequestError:
            raise ModelError("OpenRouter network request failed or timed out", retryable=True) from None
        retry_after = response.headers.get("Retry-After")
        if not 200 <= response.status_code < 300:
            try:
                data = response.json()
            except ValueError:
                data = None
            error = data.get("error") if isinstance(data, dict) else None
            failure = _status_error(response.status_code, retry_after, error)
            if isinstance(data, dict):
                recorded = _recorded_completion(data)
                if recorded.usage:
                    failure.completion = recorded
            raise failure
        return _completion(response.content, retry_after)
