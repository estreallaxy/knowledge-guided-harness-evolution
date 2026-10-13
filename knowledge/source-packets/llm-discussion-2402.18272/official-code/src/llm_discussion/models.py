"""Synthetic agents and explicit routing to heterogeneous model clients."""

import json
from typing import Mapping

from .types import Completion, Model, Request


class RoutedModel:
    name = "routed-models"

    def __init__(self, models: Mapping[str, Model]) -> None:
        self.models = dict(models)

    async def generate(self, request: Request) -> str | Completion:
        if request.agent_id not in self.models:
            raise ValueError(f"No model configured for agent {request.agent_id}")
        return await self.models[request.agent_id].generate(request)


class DryRunModel:
    """Invent answers to exercise the protocol without using reference answers."""

    name = "synthetic-dry-run"

    def __init__(self, scenario: str = "consensus", agents: int = 6) -> None:
        if scenario not in {"consensus", "tie"}:
            raise ValueError("scenario must be consensus or tie")
        if agents < 1 or (scenario == "tie" and agents % 2):
            raise ValueError("the tie scenario requires an even number of agents")
        self.scenario, self.agents = scenario, agents

    async def generate(self, request: Request) -> str:
        answer = "1"
        if request.stage != "secretary":
            index = (ord(request.agent_id) - ord("A") if len(request.agent_id) == 1
                     else int(request.agent_id.removeprefix("Agent")) - 1)
            if (self.scenario == "tie" or request.round == 1) and index >= self.agents // 2:
                answer = "2"
        if request.answer_type == "choice":
            if len(request.choices) < 2:
                raise ValueError("choice dry runs require at least two options")
            answer = request.choices[int(answer) - 1]
        return json.dumps({"reasons": "Synthetic protocol exercise; not a solution to the question.",
                           "answer": answer})
