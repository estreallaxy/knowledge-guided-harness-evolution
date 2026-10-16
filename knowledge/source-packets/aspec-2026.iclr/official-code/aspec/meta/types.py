"""Shared type definitions for the ASpec optimizer core."""

from __future__ import annotations

from typing import Any, NotRequired, TypedDict

Architecture = list[list[str]]


class OperatorSpec(TypedDict):
    """One entry in the operator pool."""

    base_template: str
    prompt: str
    specialist_data: NotRequired[dict[str, str]]
    chat_history: NotRequired[list[dict[str, Any]]]
    variants_finalized: NotRequired[bool]
    assigned_tool: NotRequired[str | None]


OperatorPool = dict[str, OperatorSpec]

ChatHistory = list[dict[str, Any]]


class Experience(TypedDict):
    """One REINFORCE experience-buffer entry (written by the evaluator)."""

    action_index: int
    reward: float
    architecture: Architecture
    architecture_before: Architecture
    query: str
    similarity: float
    cost: float
    mutation_cost: float
    score: float
    newly_created_operators: dict[str, OperatorSpec]
    modified_operators: list[str]
    pruned_operators: list[str]


class SpecialistExperience(TypedDict):
    """One Epoch-2 prompt-refinement experience for a specialist."""

    problem: str
    prediction: str
    ground_truth: str
    score: float
