"""Shared evaluation utilities for CoT Direct and EvoAgent scripts."""

from __future__ import annotations

import asyncio
import json
import os
import random
from typing import Any, Awaitable, Callable, Dict, List

from aspec.llm import BaseLLM
from aspec.llm import LLMConfig
from aspec.llm import create_llm_instance
from aspec.llm import CostManager


async def retry_with_backoff(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    max_retries: int = 10,
    base_delay: float = 1.0,
    max_delay: float = 3600.0,
    **kwargs: Any,
) -> Any:
    """Retry an async function with exponential backoff up to 1 hour."""
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            error_str = str(e).lower()
            is_rate_limit = any(term in error_str for term in ["rate limit", "quota", "too many requests", "429"])
            is_server_error = any(term in error_str for term in ["server error", "500", "502", "503", "504"])

            if attempt == max_retries - 1:
                print(f"Final attempt {attempt + 1} failed: {e}")
                raise e

            delay = min(base_delay * (2**attempt) + random.uniform(0, 1), max_delay)
            if is_rate_limit:
                delay = min(delay * 2, max_delay)
            elif is_server_error:
                delay = min(delay * 1.5, max_delay)

            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {delay:.2f}s...")
            await asyncio.sleep(delay)

    raise last_exception or Exception("Max retries exceeded")


def _extract_string_from_output(output: Any) -> str:
    """Extract a string from various output formats (str, list, dict)."""
    if isinstance(output, str):
        return output
    if isinstance(output, (list, tuple)):
        for item in reversed(output):
            if isinstance(item, str) and item.strip():
                return item
        return str(output[-1]) if output else ""
    if isinstance(output, dict):
        for key in ["answer", "solution", "result", "output", "content", "text", "response"]:
            val = output.get(key)
            if isinstance(val, str) and val.strip():
                return val
        return json.dumps(output, ensure_ascii=False)
    return str(output)


async def load_jsonl_data(jsonl_path: str) -> List[Dict[str, Any]]:
    """Load data from a JSONL file."""
    data = []
    if not os.path.exists(jsonl_path):
        print(f"Data file not found: {jsonl_path}")
        return data
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                item = json.loads(line)
                data.append(item)
    return data


def create_llm(model: str = "gemini-2.0-flash") -> BaseLLM:
    """Create an LLM instance with CostManager.

    Supports shorthand 'llama' for meta-llama/llama-3.3-70b-instruct via OpenRouter.
    """
    if model == "llama":
        llm_config = LLMConfig(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="meta-llama/llama-3.3-70b-instruct",
            api_type="openrouter",
            base_url="https://openrouter.ai/api/v1/",
        )
    elif "/" in model:
        # OpenRouter model path (e.g. deepseek/deepseek-chat-v3.1:free)
        llm_config = LLMConfig(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model=model,
            api_type="openrouter",
            base_url="https://openrouter.ai/api/v1/",
        )
    else:
        llm_config = LLMConfig(
            api_key=os.getenv("GEMINI_API_KEY"),
            model=model,
            api_type="gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta/",
        )
    llm = create_llm_instance(llm_config)
    llm.cost_manager = CostManager()
    return llm
