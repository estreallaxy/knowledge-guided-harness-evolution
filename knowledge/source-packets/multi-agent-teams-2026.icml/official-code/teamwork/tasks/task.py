"""Task abstractions for multi-agent collaboration experiments."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from teamwork.agent import TeamAgent


@dataclass
class TaskResult:
    """Result of executing a task with agents."""

    solution: str
    score: float
    metadata: Dict[str, Any]


class Task(ABC):
    """Abstract base class for collaborative tasks that agents work on together."""

    def __init__(self, agent_ids: List[int], max_rounds: int, name: Optional[str] = None):
        """Initialize task with the agent IDs that will participate.

        Args:
            agent_ids: List of unique agent IDs that will work on this task
            max_rounds: Maximum number of collaboration rounds
            name: Optional human-readable name for the task
        """
        if not agent_ids:
            raise ValueError("Task requires at least one agent ID")

        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("Agent IDs must be unique")

        if max_rounds < 1:
            raise ValueError("max_rounds must be at least 1")

        self.agent_ids = agent_ids.copy()
        self.name = name or self.__class__.__name__
        self.max_rounds = max_rounds

    @abstractmethod
    def get_task_description(self, agent_id: int) -> str:
        """Return the task description for a specific agent.

        This allows for personalized task descriptions based on the agent's role
        or perspective, while keeping the core task the same.

        Args:
            agent_id: The ID of the agent requesting the task description

        Returns:
            Task description string tailored for this agent

        Raises:
            ValueError: If agent_id is not in the task's agent list
        """
        ...

    @abstractmethod
    def score_solution(self, solution: str) -> float:
        """Score a candidate solution.

        Args:
            solution: The proposed solution to evaluate

        Returns:
            Numeric score (interpretation depends on task)
        """
        ...

    @abstractmethod
    def get_hidden_info(self, agent_id: int) -> str:
        """Return agent-specific hidden information not shared with other agents.

        This method ensures each agent gets unique information that provides
        different perspectives or capabilities for solving the task.

        Args:
            agent_id: The ID of the agent requesting hidden information

        Returns:
            Hidden information string unique to this agent

        Raises:
            ValueError: If agent_id is not in the task's agent list
        """
        ...

    @abstractmethod
    def execute(self, agents: List["TeamAgent"]) -> TaskResult:
        """Execute the full task with the given agents.

        This method orchestrates the entire task execution, managing
        communication patterns and interaction phases as needed.

        Args:
            agents: List of TeamAgent objects to participate in the task

        Returns:
            TaskResult containing the final solution and score

        Raises:
            ValueError: If agents don't match the task's agent_ids
        """
        ...

    def validate_agent_id(self, agent_id: int) -> None:
        """Validate that an agent ID is part of this task.

        Args:
            agent_id: The agent ID to validate

        Raises:
            ValueError: If agent_id is not in the task's agent list
        """
        if agent_id not in self.agent_ids:
            raise ValueError(f"Agent {agent_id} is not assigned to task '{self.name}'")

    def get_agent_count(self) -> int:
        """Return the number of agents assigned to this task."""
        return len(self.agent_ids)

    def has_agent(self, agent_id: int) -> bool:
        """Check if an agent is assigned to this task."""
        return agent_id in self.agent_ids

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task metadata to dictionary."""
        return {
            "name": self.name,
            "agent_ids": self.agent_ids.copy(),
            "agent_count": self.get_agent_count(),
            "task_type": self.__class__.__name__,
            "max_rounds": self.max_rounds,
        }

    def __str__(self) -> str:
        """String representation of the task."""
        return f"{self.name} (agents: {self.agent_ids})"

    def __repr__(self) -> str:
        """Developer representation of the task."""
        return f"{self.__class__.__name__}(agent_ids={self.agent_ids}, name='{self.name}')"


