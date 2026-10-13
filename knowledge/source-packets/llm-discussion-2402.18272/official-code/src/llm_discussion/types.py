"""Small, explicit records shared by the runner, models, and saved experiments."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Task:
    id: str
    question: str
    reference: str | None = None
    images: tuple[str, ...] = ()
    options: tuple[str, ...] = ()
    answer_type: str = "number"
    category: str | None = None
    metric: str = "exact"

    @property
    def choices(self) -> tuple[str, ...]:
        return tuple(chr(ord("A") + index) for index in range(len(self.options)))


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str | list[dict]


@dataclass(frozen=True)
class Request:
    task_id: str
    agent_id: str
    round: int
    stage: str
    messages: tuple[ChatMessage, ...]
    answer_type: str = "number"
    choices: tuple[str, ...] = ()


@dataclass(frozen=True)
class Completion:
    text: str
    model: str | None = None
    provider: str | None = None
    usage: dict[str, int | float] = field(default_factory=dict)
    generation_id: str | None = None
    finish_reason: str | None = None


class ModelError(Exception):
    """A model failure with explicit retry policy; messages must exclude secrets."""

    def __init__(self, message: str, *, retryable: bool = False, retry_after: float | None = None,
                 completion: Completion | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.retry_after = retry_after
        self.completion = completion


class Model(Protocol):
    name: str

    async def generate(self, request: Request) -> str | Completion: ...


@dataclass(frozen=True)
class Answer:
    value: str
    explanation: str
    raw: str


@dataclass(frozen=True)
class Opinion:
    agent_id: str
    group: int
    answer: Answer


@dataclass(frozen=True)
class Call:
    request: Request
    attempt: int
    response: str | None
    answer: Answer | None
    error: str | None
    completion: Completion | None = None


@dataclass(frozen=True)
class DiscussionConfig:
    agents: int = 6
    group_size: int = 3
    rounds: int = 3
    concurrency: int = 6
    max_attempts: int = 1

    def __post_init__(self) -> None:
        for name in ("agents", "group_size", "rounds", "concurrency", "max_attempts"):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.agents % self.group_size:
            raise ValueError("agents must divide evenly into groups")


@dataclass(frozen=True)
class Result:
    task_id: str
    question: str
    reference: str | None
    status: str
    answer: str | None
    votes: dict[str, int]
    used_secretary: bool
    rounds: tuple[tuple[Opinion, ...], ...]
    calls: tuple[Call, ...]
    error: str | None = None
    answer_type: str = "number"
    category: str | None = None
    metric: str = "exact"
