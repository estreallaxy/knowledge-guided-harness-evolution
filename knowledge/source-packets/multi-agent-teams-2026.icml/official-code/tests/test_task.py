"""Tests for task abstractions."""

import pytest
from typing import List
from teamwork.tasks import Task, TaskResult
from teamwork.agent import TeamAgent


class MockTask(Task):
    """Mock implementation for testing the Task ABC."""

    def __init__(self, agent_ids, max_rounds=3, name=None, ground_truth="correct answer"):
        super().__init__(agent_ids, max_rounds, name)
        self.ground_truth = ground_truth

    def get_task_description(self, agent_id: int) -> str:
        self.validate_agent_id(agent_id)
        return f"Task description for agent {agent_id}"

    def score_solution(self, solution: str) -> float:
        if solution == self.ground_truth:
            return 1.0
        elif solution.lower() in self.ground_truth.lower():
            return 0.5
        return 0.0

    def get_hidden_info(self, agent_id: int) -> str:
        self.validate_agent_id(agent_id)
        return f"Secret info for agent {agent_id}: hint_{agent_id}"

    def execute(self, agents: List[TeamAgent]) -> TaskResult:
        return TaskResult(
            solution="mock solution",
            score=1.0,
            metadata={"mock": True}
        )



def test_task_initialization():
    """Test basic task initialization and validation."""
    agent_ids = [1, 2, 3]
    task = MockTask(agent_ids, name="Test Task")

    assert task.agent_ids == agent_ids
    assert task.name == "Test Task"
    assert task.get_agent_count() == 3


def test_task_initialization_validation():
    """Test task initialization validation."""
    # Empty agent list should raise error
    with pytest.raises(ValueError, match="at least one agent"):
        MockTask([])

    # Duplicate agent IDs should raise error
    with pytest.raises(ValueError, match="must be unique"):
        MockTask([1, 2, 2, 3])


def test_agent_validation():
    """Test agent ID validation methods."""
    task = MockTask([1, 2, 3])

    # Valid agent IDs
    assert task.has_agent(1)
    assert task.has_agent(2)
    assert task.has_agent(3)

    # Invalid agent ID
    assert not task.has_agent(4)

    # validate_agent_id should raise for invalid IDs
    with pytest.raises(ValueError, match="not assigned to task"):
        task.validate_agent_id(4)


def test_task_description():
    """Test task description method."""
    task = MockTask([1, 2])

    desc1 = task.get_task_description(1)
    desc2 = task.get_task_description(2)

    assert "agent 1" in desc1
    assert "agent 2" in desc2
    assert desc1 != desc2  # Should be agent-specific

    # Invalid agent should raise error
    with pytest.raises(ValueError):
        task.get_task_description(99)


def test_solution_scoring():
    """Test solution scoring functionality."""
    task = MockTask([1], ground_truth="correct answer")

    # Perfect match
    assert task.score_solution("correct answer") == 1.0

    # Partial match
    assert task.score_solution("correct") == 0.5

    # No match
    assert task.score_solution("wrong") == 0.0


def test_hidden_info():
    """Test hidden information method."""
    task = MockTask([1, 2, 3])

    info1 = task.get_hidden_info(1)
    info2 = task.get_hidden_info(2)
    info3 = task.get_hidden_info(3)

    # Each agent should get unique information
    assert info1 != info2 != info3
    assert "agent 1" in info1
    assert "agent 2" in info2
    assert "agent 3" in info3

    # Invalid agent should raise error
    with pytest.raises(ValueError):
        task.get_hidden_info(99)


def test_task_serialization():
    """Test task serialization to dictionary."""
    task = MockTask([1, 2, 3], name="Serialization Test")
    task_dict = task.to_dict()

    expected = {
        "name": "Serialization Test",
        "agent_ids": [1, 2, 3],
        "agent_count": 3,
        "task_type": "MockTask",
        "max_rounds": 3,
    }

    assert task_dict == expected


def test_task_string_representations():
    """Test string and repr methods."""
    task = MockTask([1, 2], name="String Test")

    str_repr = str(task)
    assert "String Test" in str_repr
    assert "[1, 2]" in str_repr

    repr_str = repr(task)
    assert "MockTask" in repr_str
    assert "[1, 2]" in repr_str


def test_default_task_name():
    """Test that task gets default name from class name."""
    task = MockTask([1])
    assert task.name == "MockTask"