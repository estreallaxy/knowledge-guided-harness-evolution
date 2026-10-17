"""OpenRouter 兼容的 chat/completions 同步调用。"""

from __future__ import annotations

import json
import os
import random
import time
from typing import Any, Dict, List, Set

import httpx

# 429 / 5xx / 408：多为瞬时过载或上游故障，适合退避重试
_RETRYABLE_STATUS: Set[int] = {408, 429, 500, 502, 503, 504}


def _llm_max_retries() -> int:
    raw = (os.environ.get("TOOLPRO_LLM_MAX_RETRIES") or "6").strip()
    try:
        n = int(raw)
    except ValueError:
        return 6
    return max(0, min(n, 20))


def _retry_sleep_s(attempt: int) -> float:
    base = float(os.environ.get("TOOLPRO_LLM_RETRY_BASE_S") or "2.0")
    cap = float(os.environ.get("TOOLPRO_LLM_RETRY_MAX_S") or "45.0")
    delay = min(cap, base * (2**attempt))
    return delay + random.uniform(0, min(1.5, delay * 0.15))


def chat_completion_with_stats(
    messages: List[Dict[str, str]],
    *,
    api_key: str,
    model: str,
    base_url: str,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    timeout: float = 180.0,
) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    max_retries = _llm_max_retries()
    data: Dict[str, Any] | None = None
    response_bytes = 0

    with httpx.Client(timeout=httpx.Timeout(timeout, connect=30.0)) as client:
        for attempt in range(max_retries + 1):
            try:
                r = client.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                    content=payload_bytes,
                )
                if r.status_code in _RETRYABLE_STATUS and attempt < max_retries:
                    wait = _retry_sleep_s(attempt)
                    print(
                        f"[ToolPro][LLM] HTTP {r.status_code}，"
                        f"{wait:.1f}s 后重试 ({attempt + 1}/{max_retries})…",
                        flush=True,
                    )
                    time.sleep(wait)
                    continue
                r.raise_for_status()
                data = r.json()
                response_bytes = len(r.content or b"")
                break
            except (
                httpx.ConnectError,
                httpx.ReadTimeout,
                httpx.WriteTimeout,
                httpx.RemoteProtocolError,
            ) as e:
                if attempt < max_retries:
                    wait = _retry_sleep_s(attempt)
                    print(
                        f"[ToolPro][LLM] 网络异常 {type(e).__name__}: {e}，"
                        f"{wait:.1f}s 后重试 ({attempt + 1}/{max_retries})…",
                        flush=True,
                    )
                    time.sleep(wait)
                    continue
                raise
    if data is None:
        raise RuntimeError("LLM 请求未返回可用 JSON（不应到达此分支）")
    choices = data.get("choices") or []
    if not choices or not choices[0].get("message"):
        raise RuntimeError(f"LLM 响应格式异常: {json.dumps(data, ensure_ascii=False)[:500]}")
    return {
        "content": (choices[0]["message"].get("content") or "").strip(),
        "request_bytes": len(payload_bytes),
        "response_bytes": response_bytes,
    }


def chat_completion(
    messages: List[Dict[str, str]],
    *,
    api_key: str,
    model: str,
    base_url: str,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    timeout: float = 180.0,
) -> str:
    data = chat_completion_with_stats(
        messages,
        api_key=api_key,
        model=model,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    return str(data["content"])
