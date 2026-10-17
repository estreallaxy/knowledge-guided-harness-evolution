"""Base agent interface and common utilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Callable
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ToolCall:
    """Represents a tool call made by the agent."""
    id: UUID
    name: str
    arguments: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "arguments": self.arguments,
            "timestamp": self.timestamp.isoformat(),
            "result": self.result,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


@dataclass
class AgentStep:
    """Represents a single agent step."""
    step_num: int
    input: str
    output: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    thought: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    token_usage: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "step_num": self.step_num,
            "input": self.input,
            "output": self.output,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "thought": self.thought,
            "timestamp": self.timestamp.isoformat(),
            "token_usage": self.token_usage,
        }


@dataclass
class AgentResponse:
    """Response from agent execution."""
    run_id: UUID
    status: AgentStatus
    final_output: str
    steps: list[AgentStep] = field(default_factory=list)
    tool_call_sequence: list[str] = field(default_factory=list)
    total_tokens: int = 0
    total_duration_ms: float = 0.0
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "run_id": str(self.run_id),
            "status": self.status.value,
            "final_output": self.final_output,
            "steps": [s.to_dict() for s in self.steps],
            "tool_call_sequence": self.tool_call_sequence,
            "total_tokens": self.total_tokens,
            "total_duration_ms": self.total_duration_ms,
            "error": self.error,
            "metadata": self.metadata,
        }


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_name: str = Field(default="agent")
    model_provider: str = Field(default="openai")
    model_name: str = Field(default="gpt-4o-mini")
    temperature: float = Field(default=0.0)
    max_tokens: int = Field(default=4096)
    max_steps: int = Field(default=10)
    timeout_seconds: float = Field(default=120.0)


class Tool(BaseModel):
    """Tool definition."""
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    handler: Optional[Callable] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def to_openai_schema(self) -> dict:
        """Convert to OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters or {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, config: AgentConfig, tools: Optional[list[Tool]] = None):
        self.config = config
        self.tools = tools or []
        self._tool_handlers: dict[str, Callable] = {}
        self._run_history: list[AgentResponse] = []

        # Register tool handlers
        for tool in self.tools:
            if tool.handler:
                self._tool_handlers[tool.name] = tool.handler

        logger.info(
            "Agent initialized",
            agent_id=config.agent_id,
            agent_name=config.agent_name,
            model=config.model_name,
            num_tools=len(self.tools),
        )

    def register_tool(self, tool: Tool) -> None:
        """Register a new tool."""
        self.tools.append(tool)
        if tool.handler:
            self._tool_handlers[tool.name] = tool.handler
        logger.debug("Tool registered", tool_name=tool.name)

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by name."""
        if name not in self._tool_handlers:
            raise ValueError(f"Tool '{name}' not found")

        handler = self._tool_handlers[name]
        return handler(**arguments)

    @abstractmethod
    async def run(self, task: str) -> AgentResponse:
        """Run the agent on a task."""
        pass

    @abstractmethod
    async def step(self, input_text: str) -> AgentStep:
        """Execute a single agent step."""
        pass

    def get_run_history(self) -> list[AgentResponse]:
        """Get history of all runs."""
        return self._run_history

    def get_tool_call_sequences(self) -> list[list[str]]:
        """Get all tool call sequences from run history."""
        return [run.tool_call_sequence for run in self._run_history]
