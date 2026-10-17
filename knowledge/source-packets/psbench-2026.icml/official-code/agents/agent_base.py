"""Shared interface for the Claude computer-use agent."""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional

import numpy as np


class BaseAgent(ABC):
    """Minimal agent interface required by the benchmark runner."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        self.conversation_history: List[Dict[str, Any]] = []
        self.step_count = 0
        self.semantic_plan: List[str] = []
        self.planning_completed = False
        self._environment_health_check = None

    def set_environment_health_check(self, health_check) -> None:
        self._environment_health_check = health_check

    def assert_environment_healthy(self) -> None:
        if self._environment_health_check is not None:
            self._environment_health_check()

    def reset(self) -> None:
        self.conversation_history.clear()
        self.step_count = 0
        self.semantic_plan = []
        self.planning_completed = False

    @abstractmethod
    def plan_task(
        self, instruction: str, screenshot: Optional[np.ndarray] = None
    ) -> List[str]:
        """Return a short semantic plan for the current task."""

    @abstractmethod
    def act(self, observation: Dict[str, Any]) -> str:
        """Run the agent and return DONE or FAIL."""

    def log_semantic_plan(self, plan_steps: List[str]) -> None:
        self.semantic_plan = list(plan_steps)
        self.planning_completed = True

    def get_semantic_plan(self) -> List[str]:
        return list(self.semantic_plan)

    def log_reasoning(self, reasoning: str) -> None:
        self.logger.debug("Reasoning: %s", reasoning)

    def update_conversation_history(
        self, observation: Dict[str, Any], action: str
    ) -> None:
        self.conversation_history.append(
            {
                "step": self.step_count,
                "task_id": observation.get("task_id"),
                "action": action,
            }
        )

    def get_conversation_summary(self) -> Dict[str, Any]:
        return {
            "agent_name": self.name,
            "total_steps": self.step_count,
            "conversation_length": len(self.conversation_history),
            "actions_taken": [
                item.get("action") for item in self.conversation_history
            ],
        }

