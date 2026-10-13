#!/usr/bin/env python3
"""Induce, verify and reuse programmatic Skills (ASI, arXiv:2504.06821).

Paper mechanism kept here: a *program* is abstracted from an episode the evaluator
marked successful; it is accepted only if it passes **execution verification** - the
program must reach the goal on its own, so the actions that came after it cannot be
what made the episode succeed. Verified programs are stored and reused on new tasks.

`demo` runs the whole loop on a deterministic mini web environment with no model and
no network, and also shows the ablation the paper argues for: checking the candidate
only with the tail still attached accepts a useless program.
`induce-live` proposes a program through an OpenAI-compatible endpoint (needs `openai`
installed and credentials in the environment).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

Action = tuple
Predicate = Callable[["MiniWeb"], bool]


class MiniWeb:
    """Deterministic stand-in for a browsable site: goto / click / fill / submit."""

    FIELDS = {"item": ("rating",)}

    def __init__(self) -> None:
        self.page = "home"
        self.filled: dict[str, str] = {}
        self.submitted = False
        self.log: list[str] = []

    def step(self, action: Action) -> None:
        kind, *rest = action
        self.log.append(f"{kind}({', '.join(map(str, rest))})")
        if kind == "goto":
            self.page = rest[0]
        elif kind == "click":
            target = rest[0]
            if target == "search" and self.page == "home":
                self.page = "results"
            elif target == "item" and self.page == "results":
                self.page = "item"
            elif target == "submit" and self.page == "item" and "rating" in self.filled:
                self.submitted = True
        elif kind == "fill":
            name, value = rest
            if name in self.FIELDS.get(self.page, ()):
                self.filled[name] = str(value)

    def run(self, actions: Sequence[Action]) -> "MiniWeb":
        for action in actions:
            self.step(action)
        return self


def submit_rating_is(value: str) -> Predicate:
    return lambda env: env.submitted and env.filled.get("rating") == value


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    program: tuple[Action, ...]  # literal values are swapped for "{param}" placeholders
    params: tuple[str, ...]
    verified: bool = False

    def instantiate(self, **values: str) -> tuple[Action, ...]:
        out = []
        for action in self.program:
            out.append(tuple(
                values.get(part[1:-1], part) if isinstance(part, str) and part.startswith("{") else part
                for part in action
            ))
        return tuple(out)

    def render(self, **values: str) -> str:
        return " ; ".join(f"{a[0]}({', '.join(map(str, a[1:]))})" for a in self.instantiate(**values))


class SkillLibrary:
    """Stores only verified Skills; retrieval uses token overlap (the paper uses an LM)."""

    def __init__(self) -> None:
        self._skills: list[Skill] = []

    def verify_and_add(self, candidate: Skill, verifier: Callable[[Skill], bool]) -> Skill:
        checked = Skill(candidate.name, candidate.description, candidate.program,
                        candidate.params, verifier(candidate))
        if not checked.verified:
            raise ValueError(f"Skill {candidate.name!r} failed execution verification")
        self._skills.append(checked)
        return checked

    def retrieve(self, task: str, limit: int = 3) -> list[Skill]:
        query = set(task.lower().split())
        return sorted(self._skills,
                      key=lambda s: len(query & set(s.description.lower().split())),
                      reverse=True)[:limit]

    def __iter__(self) -> Iterable[Skill]:
        return iter(self._skills)

    def __len__(self) -> int:
        return len(self._skills)


def induce_program(episode: Sequence[Action], predicate: Predicate, goal_field: str = "rating") -> Skill:
    """Take the shortest suffix of `episode` that still reaches the goal from scratch.

    This is the paper's induction step in miniature: the actions that only mattered
    because they were already half-way through the episode are dropped, and the value
    written into the goal field becomes a parameter.
    """
    start = 0
    for index in range(len(episode) - 1, -1, -1):  # shortest suffix that still works
        if predicate(MiniWeb().run(episode[index:])):
            start = index
            break
    program, params = [], []
    for action in episode[start:]:
        if action[0] == "fill" and action[1] == goal_field:
            params.append(goal_field)
            program.append(("fill", goal_field, "{%s}" % goal_field))
        else:
            program.append(action)
    return Skill(name="submit_rating",
                 description="submit a rating on the item page so the review is recorded",
                 program=tuple(program), params=tuple(params))


def execution_verifier(binding: dict[str, str], predicate: Predicate) -> Callable[[Skill], bool]:
    """ASI's execution-based check: the program must reach the goal on its own."""

    def verify(skill: Skill) -> bool:
        return bool(predicate(MiniWeb().run(skill.instantiate(**binding))))

    return verify


DEV_EPISODE: tuple[Action, ...] = (("goto", "home"), ("click", "search"), ("click", "item"),
                                   ("fill", "rating", "4"), ("click", "submit"))


def _demo() -> int:
    goal = submit_rating_is("4")

    print("=== 1. 诱导：从成功 episode 中取出真正起作用的 suffix ===")
    candidate = induce_program(DEV_EPISODE, goal)
    print(f"episode      : {' ; '.join(f'{a[0]}({a[1]})' for a in DEV_EPISODE)}")
    print(f"candidate    : {candidate.render(rating='{rating}')}  params={candidate.params}")

    print("\n=== 2. 执行式验证（program 必须自己从初始状态达成目标） ===")
    library = SkillLibrary()
    added = library.verify_and_add(candidate, execution_verifier({"rating": "4"}, goal))
    print(f"verified -> 入库 {added.name}（库内 {len(library)} 条）")
    try:
        library.verify_and_add(Skill("submit_only", "submit the form", (("click", "submit"),), ()),
                               execution_verifier({"rating": "4"}, goal))
        raise AssertionError("an unverified skill must not be added")
    except ValueError as exc:
        print(f"未通过验证的候选被拒绝: {exc}")

    print("\n=== 3. 复用：新任务、不同参数值，不重新探索 ===")
    retrieved = library.retrieve("submit rating review on the item page")[0]
    reuse = retrieved.instantiate(rating="7")
    env = MiniWeb().run(reuse)
    print(f"复用 {retrieved.name}(rating=7) -> {env.log}")
    assert submit_rating_is("7")(env), env.filled
    print("复用成功")

    print("\n=== 4. 消融：把尾部动作也算进验证会怎样（论文论证的假成功） ===")
    prefix, tail = DEV_EPISODE[:4], DEV_EPISODE[4:]
    attached = MiniWeb().run(prefix + tail)
    print(f"带尾部重放 prefix+tail -> submitted={attached.submitted}"
          f"（看起来成功，靠的是 prefix 里已填好的 rating）")
    alone = MiniWeb().run(tail)
    print(f"只重放 tail           -> submitted={alone.submitted}（真相：该 program 本身无效）")
    assert attached.submitted and not alone.submitted
    print("结论：只有'truncate 尾部后再执行'这种验证才能拒绝这条假成功候选")

    print("\nself-test OK: 验证过的 Skill 可跨任务复用，未验证候选与假成功候选都被拒")
    return 0


def _induce_live(args: argparse.Namespace) -> int:
    from openai import OpenAI  # imported only for the live command

    client = OpenAI()
    prompt = ("Turn a successful web episode into a reusable program. Return only JSON, a list of "
              "actions shaped as {\"type\": ..., \"args\": [...]}.\n"
              f"Episode: {json.dumps([list(a) for a in DEV_EPISODE])}\nGoal: {args.goal}")
    raw = client.chat.completions.create(model=args.model,
                                         messages=[{"role": "user", "content": prompt}],
                                         temperature=0.0).choices[0].message.content
    print(raw)
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agent Skill Induction (ASI) reference loop")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo", help="offline deterministic induce/verify/reuse demo + self-test")
    live = sub.add_parser("induce-live", help="propose a program through a live model")
    live.add_argument("--goal", default="submit the item rating")
    live.add_argument("--model", default="deepseek/deepseek-v4-flash")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command in (None, "demo"):
        return _demo()
    if args.command == "induce-live":
        return _induce_live(args)
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
