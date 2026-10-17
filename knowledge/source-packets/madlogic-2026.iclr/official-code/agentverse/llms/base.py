from abc import abstractmethod
from pydantic import BaseModel, Field


class LLMResult(BaseModel):
    content: str


class BaseModelArgs(BaseModel):
    pass


class BaseLLM(BaseModel):
    args: BaseModelArgs = Field(default_factory=BaseModelArgs)
    max_retry: int = Field(default=3, ge=1)

    @abstractmethod
    def generate_response(self, structured_prompt, chat_memory) -> LLMResult:
        raise NotImplementedError

    @abstractmethod
    async def agenerate_response(self, structured_prompt, chat_memory) -> LLMResult:
        raise NotImplementedError


class BaseChatModel(BaseLLM):
    pass
