from openai import AsyncOpenAI, OpenAI
from pydantic import Field

from . import llm_registry
from .base import BaseChatModel, BaseModelArgs, LLMResult


class OpenAIChatArgs(BaseModelArgs):
    model: str = "gpt-4"
    max_tokens: int = 4096
    temperature: float = 0.0
    top_p: float = 1.0


@llm_registry.register("openai")
class OpenAIChat(BaseChatModel):
    """Chat completions through OPENAI_API_KEY and optional OPENAI_BASE_URL."""

    args: OpenAIChatArgs = Field(default_factory=OpenAIChatArgs)

    def __init__(self, max_retry=3, **kwargs):
        super().__init__(args=OpenAIChatArgs(**kwargs), max_retry=max_retry)

    def _construct_messages(self, structured_prompt, chat_memory):
        messages = []
        if structured_prompt.system_content:
            messages.append({"role": "system", "content": structured_prompt.system_content})
        for message in chat_memory:
            if message.content.strip() and message.content != "[Silence]":
                messages.append({
                    "role": "assistant", "name": message.sender.replace(" ", "_"),
                    "content": message.content,
                })
        if structured_prompt.user_content:
            messages.append({"role": "user", "content": structured_prompt.user_content})
        return messages

    def generate_response(self, structured_prompt, chat_memory):
        with OpenAI(max_retries=0) as client:
            response = client.chat.completions.create(
                messages=self._construct_messages(structured_prompt, chat_memory),
                **self.args.model_dump(),
            )
        return LLMResult(content=response.choices[0].message.content or "")

    async def agenerate_response(self, structured_prompt, chat_memory):
        async with AsyncOpenAI(max_retries=0) as client:
            response = await client.chat.completions.create(
                messages=self._construct_messages(structured_prompt, chat_memory),
                **self.args.model_dump(),
            )
        return LLMResult(content=response.choices[0].message.content or "")
