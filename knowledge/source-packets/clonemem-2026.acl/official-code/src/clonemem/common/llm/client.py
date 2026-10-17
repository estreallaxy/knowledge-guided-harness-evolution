import asyncio
import json
from typing import List, Dict, Union, Optional, Tuple
import tiktoken
from openai import AsyncOpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessage
from .token_tracker import TokenUsage
import numpy as np
import base64


OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_ROUTER_URL = "https://openrouter.ai/api/v1"


def image_to_base64(path: str) -> str:
    """Convert a local image file to a Base‑64 string (data‑URI ready)."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class LLM:
    """Lightweight Async LLM wrapper for OpenRouter‑compatible models."""

    MODEL_REGISTRY: Dict[str, Dict[str, Union[int, bool]]] = {
        "gpt-4o":                    {"limit": 128_000, "mm": True},
        "gpt-4o-mini":               {"limit": 128_000, "mm": True},
        "gpt-4.1":                   {"limit": 256_000, "mm": True},
        "gpt-4.1-mini":              {"limit": 256_000, "mm": True},
        "gpt-4.1-nano":             {"limit": 256_000, "mm": True},
        "google/gemini-pro":         {"limit": 32_768,  "mm": True},
        "google/gemini-2.5-flash":   {"limit": 1_000_000, "mm": True},
        "xai/grok-4":                {"limit": 128_000, "mm": False},
        "moonshotai/kimi-k2":      {"limit": 131_072, "mm": False},
        "deepseek-ai/deepseek-v3":   {"limit": 32_000,  "mm": False},
    }

    @classmethod
    def register_model(cls, name: str, token_limit: int, multimodal: bool = False) -> None:
        """Dynamically register / override a model configuration."""
        cls.MODEL_REGISTRY[name] = {"limit": token_limit, "mm": multimodal}

    def __init__(self, model: str, api_key: str, *, base_url: Optional[str] = None, max_tokens: int = 1024):
        self.model = model
        self.api_key = api_key
        self.max_tokens = max_tokens

        cfg = self.MODEL_REGISTRY.get(model, {"limit": None, "mm": False})
        self.max_input_tokens: Optional[int] = cfg["limit"]  # None ⇒ unlimited / unknown
        self.support_images: bool = cfg["mm"]

        self.base_url = base_url or OPENAI_BASE_URL
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.embedding_client = AsyncOpenAI(api_key=api_key)

        # tokenizer fallback chain
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # usage counters
        self.input_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def _count_text(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def _count_message_tokens(self, messages: List[Dict]) -> int:
        tokens_per_message = 3
        tokens_per_name = 1
        total = 0
        for msg in messages:
            total += tokens_per_message
            for k, v in msg.items():
                if k == "name":
                    total += tokens_per_name
                if isinstance(v, str):
                    total += self._count_text(v)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            total += self._count_text(item)
                        elif isinstance(item, dict):
                            for vv in item.values():
                                if isinstance(vv, str):
                                    total += self._count_text(vv)
        return total + 3  # assistant priming

    def _format_messages(self, messages: List[Dict]) -> List[Dict]:
        fmt: List[Dict] = []
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValueError("Each message must be a dict with 'role' and 'content'.")
            msg = dict(msg)

            if self.support_images and msg.get("base64_image"):
                # ensure content becomes list[dict]
                content = msg.get("content")
                if not content:
                    content = []
                elif isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                elif isinstance(content, list):
                    content = [
                        {"type": "text", "text": x} if isinstance(x, str) else x for x in content
                    ]
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{msg['base64_image']}"}
                })
                msg["content"] = content
                msg.pop("base64_image", None)
            else:
                msg.pop("base64_image", None)
            fmt.append(msg)
        return fmt

    async def ask(self, messages: List[Dict], *, temperature: float = 0.1, response_format: Optional[Dict] = None,
                  max_retries: int = 3) -> Tuple[str, TokenUsage]:
        formatted = self._format_messages(messages)
        input_tokens = self._count_message_tokens(formatted)
        if self.max_input_tokens and input_tokens + self.max_tokens > self.max_input_tokens:
            raise ValueError(
                f"Token limit exceeded: {input_tokens} input + {self.max_tokens} max completion > {self.max_input_tokens}")

        model_params = {
            'model': self.model,
            'messages': formatted,
        }

        if "gpt-5" not in self.model and "o3" not in self.model:
            model_params['temperature'] = temperature

        if response_format is not None:
            model_params["response_format"] = response_format

        last_exception = None
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(**model_params)

                self._update_usage(response.usage)
                token_usage = TokenUsage(
                    input_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )
                return response.choices[0].message.content, token_usage

            except json.JSONDecodeError as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1, 2, 4 秒
                    print(f"[LLM] JSON解析失败，{wait_time}秒后第 {attempt + 2} 次重试...")
                    await asyncio.sleep(wait_time)
            except OpenAIError as e:
                raise RuntimeError(f"OpenRouter API error: {e}")

        raise RuntimeError(f"JSON解析在 {max_retries} 次重试后仍失败: {last_exception}")

    async def ask_tools(self, messages: List[Dict], tools: List[Dict], *, temperature: float = 0.7,
                        tool_choice: Union[str, Dict] = "auto") -> ChatCompletionMessage:
        formatted = self._format_messages(messages)
        input_tokens = self._count_message_tokens(formatted)
        if self.max_input_tokens and input_tokens + self.max_tokens > self.max_input_tokens:
            raise ValueError(
                f"Token limit exceeded: {input_tokens} input + {self.max_tokens} max completion > {self.max_input_tokens}")
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                stream=False,
            )
        except OpenAIError as e:
            raise RuntimeError(f"OpenRouter tool API error: {e}")

        self._update_usage(response.usage)
        return response.choices[0].message

    async def embed(self, text: str) -> np.ndarray:
        response = await self.embedding_client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            encoding_format="float"
        )
        return np.array(response.data[0].embedding, dtype=np.float32)

    def _update_usage(self, usage):
        self.input_tokens += getattr(usage, "prompt_tokens", 0)
        self.completion_tokens += getattr(usage, "completion_tokens", 0)
        self.total_tokens += getattr(usage, "total_tokens", 0)

    def get_usage_summary(self) -> Dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }
