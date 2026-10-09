#!/usr/bin/env python3
"""Conversation-driven coordinator loop with recursive subtask delegation.

Mechanism source: AutoGen, "Enabling Next-Gen LLM Applications via Multi-Agent
Conversation Framework" (arXiv:2308.08155, COLM 2024).

This is a harness-agnostic skeleton of the mechanism:
- Model calls are injected as a callback, with no provider binding;
- Nested sessions support both full-history and summary-only hand-back;
- Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import Callable

# Model-call protocol: system prompt plus message history in, generated text out.
ModelCall = Callable[[str, list[dict[str, str]]], str]

TERMINATE = "TERMINATE"


@dataclass
class Agent:
    """A conversable execution unit: name, role description, optional model override."""

    name: str
    system_prompt: str
    model: ModelCall | None = None  # falls back to the orchestrator's model_call


@dataclass
class Message:
    """A shared message: source, target, content, and category."""

    source: str
    target: str
    content: str
    kind: str = "text"  # text / tool_result / summary / terminate

    def as_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "target": self.target,
            "content": self.content,
            "kind": self.kind,
        }


@dataclass
class SubtaskResult:
    """Result handed back from a nested session."""

    summary: str
    history: list[Message] = field(default_factory=list)


class DelegationOrchestrator:
    """Coordinator loop: select a speaker, trigger its auto-reply, update shared history.

    Maps to the paper's three orchestration primitives:
    - auto-reply: each agent replies as soon as it receives a message (the step function);
    - GroupChatManager: select_next_speaker decides who acts next;
    - nested chat: run_subtask opens a nested session recursively and collects its result.
    """

    def __init__(
        self,
        agents: list[Agent],
        model_call: ModelCall,
        history: list[Message] | None = None,
        max_steps: int = 20,
    ):
        self.agents = {agent.name: agent for agent in agents}
        self.model_call = model_call
        self.history: list[Message] = history or []
        self.max_steps = max_steps

    def _model_for(self, agent: Agent) -> ModelCall:
        return agent.model or self.model_call

    def _history_dicts(self) -> list[dict[str, str]]:
        return [message.as_dict() for message in self.history]

    def reply(self, agent_name: str, target: str) -> str:
        """Trigger one agent's auto-reply: generate a reply and append it to shared history."""
        agent = self.agents[agent_name]
        content = self._model_for(agent)(agent.system_prompt, self._history_dicts())
        self.history.append(Message(source=agent_name, target=target, content=content))
        return content

    def select_next_speaker(
        self,
        candidates: list[str],
        last_message: Message,
        task: str,
        speaker_selector: Callable[[str, list[dict[str, str]], list[str]], str] | None,
    ) -> str:
        """Select the next participant.

        Defaults to round-robin in registration order; pass a speaker_selector to
        implement GroupChatManager-style dynamic selection (rule- or model-based).
        """
        if speaker_selector is not None:
            return speaker_selector(task, self._history_dicts(), candidates)
        order = list(self.agents)
        index = order.index(last_message.source) if last_message.source in order else -1
        return order[(index + 1) % len(order)]

    def run_subtask(
        self,
        task: str,
        participants: list[str],
        summary_only: bool = True,
        max_steps: int | None = None,
        speaker_selector: Callable[[str, list[dict[str, str]], list[str]], str] | None = None,
    ) -> SubtaskResult:
        """Nested session (nested chat): run an isolated loop for a subtask and collect its result.

        With summary_only=True only the summary is handed back to the parent
        session, bounding context cost; otherwise the full session history is
        returned.
        """
        local_history: list[Message] = []
        limit = max_steps or self.max_steps
        last = Message(source="orchestrator", target=participants[0], content=task)

        for _ in range(limit):
            speaker = self.select_next_speaker(participants, last, task, speaker_selector)
            agent = self.agents[speaker]
            prompt_history = [m.as_dict() for m in local_history] + [last.as_dict()]
            content = self._model_for(agent)(agent.system_prompt, prompt_history)
            message = Message(source=speaker, target="orchestrator", content=content)
            local_history.append(message)
            last = message
            if TERMINATE in content:
                break

        summary = local_history[-1].content if local_history else task
        if summary_only:
            self.history.append(
                Message(source="orchestrator", target="orchestrator", content=summary, kind="summary")
            )
            return SubtaskResult(summary=summary, history=[])
        self.history.extend(local_history)
        return SubtaskResult(summary=summary, history=local_history)

    def run(
        self,
        task: str,
        speaker_selector: Callable[[str, list[dict[str, str]], list[str]], str] | None = None,
    ) -> list[Message]:
        """Main loop: start from the task description, trigger auto-replies in turn, stop on the
        termination marker or when the budget runs out."""
        last = Message(source="orchestrator", target=list(self.agents)[0], content=task)
        for _ in range(self.max_steps):
            speaker = self.select_next_speaker(list(self.agents), last, task, speaker_selector)
            content = self.reply(speaker, target="orchestrator")
            last = self.history[-1]
            if TERMINATE in content:
                break
        return self.history


def demo_command(args: argparse.Namespace) -> None:
    """Minimal demo: run the coordinator loop and a nested delegation with a stub model."""

    def stub_model(system_prompt: str, history: list[dict[str, str]]) -> str:
        # Stub model: fixed replies per role, only to verify the skeleton runs.
        last_content = history[-1]["content"] if history else ""
        if "orchestrator" in system_prompt:
            if "decompose" in last_content.lower():
                return "Planner: plan first, then hand off to the executor"
            return TERMINATE + ": task complete, results summarized"
        if "planner" in system_prompt:
            return "Decompose the task into two steps, then hand off to the executor"
        return "Executor: completed the planned steps"

    agents = [
        Agent(name="orchestrator", system_prompt="You are the coordinator: choose the next speaker and summarize results"),
        Agent(name="planner", system_prompt="You are the planner: decompose the task into steps"),
        Agent(name="executor", system_prompt="You are the executor: carry out the planned steps"),
    ]
    orchestrator = DelegationOrchestrator(agents=agents, model_call=stub_model, max_steps=5)

    result = orchestrator.run_subtask(
        task="Decompose the task into two steps and execute them",
        participants=["planner", "executor"],
        summary_only=True,
    )
    print("Subtask summary:", result.summary)

    history = orchestrator.run(task="Demo task: decompose and execute")
    for message in history:
        print(f"[{message.source} -> {message.target}] {message.content[:60]}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Conversation-driven coordinator loop with recursive subtask delegation."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Run a minimal demo with a stub model")
    demo.set_defaults(handler=demo_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
