#!/usr/bin/env python3
"""SOP role pipeline: structured role sequence with pub-sub messages and revisions.

Mechanism source: MetaGPT, "Meta Programming for A Multi-Agent Collaborative
Framework" (arXiv:2308.00352, ICLR 2024 Oral).

This is a harness-agnostic skeleton of the mechanism:
- Roles execute in a fixed SOP order and emit structured artifacts;
- Messages go through a publish-subscribe pool filtered by message kind;
- A reviewer role can send an artifact back for revision (bounded rounds);
- Model calls are injected as a callback; uses only the Python standard library.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable

# Model-call protocol: system prompt plus message history in, generated text out.
ModelCall = Callable[[str, list[dict[str, str]]], str]

PASS = "PASS"
REVISE = "REVISE"


@dataclass
class Message:
    """One pooled message: kind (task / artifact / review), sender, content."""

    kind: str
    sender: str
    content: str

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "sender": self.sender, "content": self.content}


class MessagePool:
    """Publish-subscribe pool: roles only receive the message kinds they subscribe to.

    Re-publishing with the same (kind, sender) replaces the previous message, so
    each producer keeps a single latest message (mirrors observing the latest
    artifact of a given type).
    """

    def __init__(self) -> None:
        self.messages: list[Message] = []

    def publish(self, message: Message) -> None:
        self.messages.append(message)

    def replace(self, message: Message) -> None:
        self.messages = [
            existing
            for existing in self.messages
            if not (existing.kind == message.kind and existing.sender == message.sender)
        ]
        self.messages.append(message)

    def received_by(self, subscriptions: tuple[str, ...]) -> list[Message]:
        return [message for message in self.messages if message.kind in subscriptions]


@dataclass
class Artifact:
    """A structured intermediate product: kind (requirements / design / code), content, author."""

    kind: str
    content: str
    author: str


@dataclass
class Role:
    """One pipeline role: fixed responsibility, one produced artifact kind, subscriptions.

    A role with ``reviews`` set acts as a reviewer of that artifact kind instead
    of a producer.
    """

    name: str
    responsibility: str
    produces: str
    subscribes: tuple[str, ...] = ("task", "artifact")
    reviews: str = ""


class SOPPipeline:
    """Run roles in a fixed order; reviewers can send artifacts back for revision."""

    def __init__(self, roles: list[Role], model_call: ModelCall, max_revisions: int = 2):
        self.roles = roles
        self.model_call = model_call
        self.max_revisions = max_revisions
        self.pool = MessagePool()
        self.artifacts: list[Artifact] = []
        self.review_rounds = 0

    def _invoke(self, role: Role, task: str) -> str:
        lines = [f"TASK: {task}"]
        for message in self.pool.received_by(role.subscribes):
            lines.append(f"[{message.kind} from {message.sender}] {message.content}")
        if role.reviews:
            instruction = (
                f"Review artifacts of kind '{role.reviews}' and answer exactly "
                f"'{PASS}' or '{REVISE}: <feedback>'. "
            )
        else:
            instruction = f"Produce a structured artifact of kind '{role.produces}'. "
        system = (
            f"You are {role.name} (RESPONSIBILITY: {role.responsibility}). "
            + instruction
            + "Keep products structured; do not chat."
        )
        messages = [{"role": "user", "content": "\n".join(lines)}]
        return self.model_call(system, messages)

    def _produce(self, role: Role, task: str) -> Artifact:
        content = self._invoke(role, task)
        artifact = Artifact(kind=role.produces, content=content, author=role.name)
        self.artifacts = [
            existing
            for existing in self.artifacts
            if not (existing.kind == artifact.kind and existing.author == artifact.author)
        ]
        self.artifacts.append(artifact)
        self.pool.replace(Message(kind="artifact", sender=role.name, content=content))
        return artifact

    def _review_loop(self, role: Role) -> None:
        for _ in range(self.max_revisions + 1):
            reviewed = [a for a in self.artifacts if a.kind == role.reviews]
            if not reviewed:
                return
            artifact = reviewed[-1]
            verdict = self._invoke(role, task="")
            self.review_rounds += 1
            self.pool.replace(Message(kind="review", sender=role.name, content=verdict))
            if not verdict.startswith(REVISE):
                return
            producer = self._find_role(artifact.author)
            if producer is None:
                return
            self._produce(producer, task="")

    def _find_role(self, name: str) -> Role | None:
        for role in self.roles:
            if role.name == name:
                return role
        return None

    def run(self, task: str) -> list[Artifact]:
        """Execute roles in SOP order; return the final artifact chain."""
        self.pool.publish(Message(kind="task", sender="user", content=task))
        for role in self.roles:
            if role.reviews:
                self._review_loop(role)
            else:
                self._produce(role, task)
        return list(self.artifacts)


def demo_roles() -> list[Role]:
    """Three-role pipeline: analyst produces requirements, builder implements, reviewer gates."""
    return [
        Role(
            name="Analyst",
            responsibility="clarify requirements",
            produces="requirements",
        ),
        Role(
            name="Builder",
            responsibility="implement the module",
            produces="code",
            subscribes=("task", "artifact", "review"),
        ),
        Role(
            name="Reviewer",
            responsibility="review the artifacts against acceptance criteria",
            produces="",
            reviews="code",
            subscribes=("artifact",),
        ),
    ]


def stub_model(system_prompt: str, messages: list[dict[str, str]]) -> str:
    """Deterministic stub: the reviewer rejects the first draft once, then passes."""
    text = messages[-1]["content"]
    if "review" in system_prompt:
        if "acceptance criteria" in text:
            return PASS
        return f"{REVISE}: add acceptance criteria to the artifact"
    if "implement" in system_prompt:
        return "draft-2: parser with acceptance criteria" if REVISE in text else "draft-1: parser"
    return "requirements: parse and validate the config"


def demo_command(args: argparse.Namespace) -> None:
    """Minimal demo: run the three-role pipeline with one review-driven revision."""
    pipeline = SOPPipeline(roles=demo_roles(), model_call=stub_model, max_revisions=2)
    pipeline.run("Add a config parser to the tool.")

    print("--- Artifact chain ---")
    for artifact in pipeline.artifacts:
        print(f"[{artifact.kind}] {artifact.author}: {artifact.content}")

    print("--- Message pool ---")
    for message in pipeline.pool.messages:
        print(f"({message.kind}) {message.sender}: {message.content}")

    print(f"Review rounds: {pipeline.review_rounds}")
    print(f"Final artifact: {pipeline.artifacts[-1].content}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SOP role pipeline with pub-sub messages and review-driven revisions."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser(
        "demo", help="Run a three-role pipeline with one review-driven revision"
    )
    demo.set_defaults(handler=demo_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
