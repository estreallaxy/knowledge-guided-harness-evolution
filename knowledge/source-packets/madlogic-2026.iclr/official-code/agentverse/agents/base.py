from abc import abstractmethod

from pydantic import BaseModel, Field

from agentverse.llms import BaseLLM
from agentverse.memory import BaseMemory, ChatHistoryMemory
from agentverse.parser import OutputParser


class BaseAgent(BaseModel):
    name: str
    llm: BaseLLM
    output_parser: OutputParser
    prompt_template: str
    role_description: str = ""
    memory: BaseMemory = Field(default_factory=ChatHistoryMemory)
    max_retry: int = Field(default=3, ge=1)
    receiver: set[str] = Field(default_factory=lambda: {"all"})

    @abstractmethod
    async def astep(self, env=None, env_description=""):
        raise NotImplementedError

    def get_receiver(self):
        return self.receiver

    def add_message_to_memory(self, messages):
        self.memory.add_message(messages)

    def reset(self):
        self.memory.reset()
