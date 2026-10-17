"""Base task definitions and interfaces."""

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


class TaskFamily(str, Enum):
    """Categories of tasks for experiments."""
    TOOL_INTENSIVE = "tool_intensive"
    LONG_HORIZON = "long_horizon"
    POLICY_BOUND = "policy_bound"


class TaskDifficulty(str, Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Task:
    """A task instance for agent execution."""
    id: UUID
    family: TaskFamily
    name: str
    description: str
    prompt: str
    expected_tools: list[str] = field(default_factory=list)
    expected_output_pattern: Optional[str] = None
    difficulty: TaskDifficulty = TaskDifficulty.MEDIUM
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    ground_truth: Optional[Any] = None

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "family": self.family.value,
            "name": self.name,
            "description": self.description,
            "prompt": self.prompt,
            "expected_tools": self.expected_tools,
            "expected_output_pattern": self.expected_output_pattern,
            "difficulty": self.difficulty.value,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "ground_truth": self.ground_truth,
        }


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: UUID
    run_id: UUID
    success: bool
    output: str
    tool_sequence: list[str] = field(default_factory=list)
    expected_tool_match: float = 0.0
    output_correctness: float = 0.0
    duration_ms: float = 0.0
    token_usage: int = 0
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "run_id": str(self.run_id),
            "success": self.success,
            "output": self.output,
            "tool_sequence": self.tool_sequence,
            "expected_tool_match": self.expected_tool_match,
            "output_correctness": self.output_correctness,
            "duration_ms": self.duration_ms,
            "token_usage": self.token_usage,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class TaskGenerator(ABC):
    """Base class for task generators."""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self._task_count = 0
        import random
        self._rng = random.Random(seed)

    @property
    @abstractmethod
    def family(self) -> TaskFamily:
        """Return the task family."""
        pass

    @abstractmethod
    def generate(self, **kwargs) -> Task:
        """Generate a single task."""
        pass

    def generate_batch(self, count: int, **kwargs) -> list[Task]:
        """Generate a batch of tasks."""
        return [self.generate(**kwargs) for _ in range(count)]

    @abstractmethod
    def get_tools(self) -> list[dict[str, Any]]:
        """Get tool definitions required for this task family."""
        pass

    @abstractmethod
    def evaluate(self, task: Task, result: TaskResult) -> dict[str, float]:
        """Evaluate task result and return metrics."""
        pass

    def _next_id(self) -> UUID:
        """Generate next task ID."""
        self._task_count += 1
        return uuid4()


def compute_sequence_similarity(seq1: list[str], seq2: list[str]) -> float:
    """Compute similarity between two sequences using edit distance."""
    if not seq1 and not seq2:
        return 1.0
    if not seq1 or not seq2:
        return 0.0

    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )

    edit_distance = dp[m][n]
    max_len = max(m, n)
    return 1.0 - (edit_distance / max_len)
