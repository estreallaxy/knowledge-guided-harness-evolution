#!/usr/bin/env python3
"""Self-adaptive planning from environment feedback (AdaPlanner, arXiv:2305.16653).

Paper mechanism kept here: the agent plans, executes, and then adapts on two levels -
**in-plan** feedback fixes a step whose parameters were wrong while the plan's shape is
still sound, and **out-of-plan** feedback discards the remaining plan and re-plans
because the world contradicted the assumptions the plan was built on. Adaptation
happens while the plan is still being carried out, so the agent does not have to run a
doomed plan to the end.

`demo` drives both feedback types through a deterministic mini household environment
with no model and no network, and shows that the non-adaptive baseline fails on the same
task. `replan-live` shows the optional live path where the re-plan is produced by a model.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class Step:
    name: str
    target: str
    where: str = ""

    def render(self) -> str:
        return f"{self.name}({self.target}{', ' + self.where if self.where else ''})"


@dataclass
class Plan:
    steps: list[Step]
    completed: list[int] = field(default_factory=list)
    revisions: list[str] = field(default_factory=list)

    def next_step(self) -> tuple[int, Step] | None:
        for index, step in enumerate(self.steps):
            if index not in self.completed:
                return index, step
        return None

    def mark_completed(self, index: int) -> None:
        if index not in self.completed:
            self.completed.append(index)

    def revise_in_plan(self, index: int, replacement: Step, why: str) -> None:
        """In-plan feedback: the plan shape is fine, one step's parameters were wrong."""
        self.steps[index] = replacement
        self.revisions.append(f"in-plan[{index}] {why}: -> {replacement.render()}")

    def replan_remaining(self, current: int, replacement: Sequence[Step], why: str) -> None:
        """Out-of-plan feedback: the world contradicted the plan, re-plan what is left."""
        if not 0 <= current <= len(self.steps):
            raise IndexError(current)
        self.steps[current:] = list(replacement)
        self.completed = [index for index in self.completed if index < current]
        self.revisions.append(f"out-of-plan[{current}] {why}: replanned "
                              f"{len(replacement)} steps")


class MiniHouse:
    """Deterministic state machine exposing the two feedback kinds AdaPlanner reacts to."""

    def __init__(self) -> None:
        self.location = {"mug": "cabinet", "key": "hall"}
        self.locked = {"study": True}
        self.carried: set[str] = set()
        self.placed: dict[str, str] = {}
        self.room = "kitchen"
        self.visits = 0

    def goal_met(self) -> bool:
        return self.placed.get("mug") == "desk"

    def step(self, action: Step) -> str:
        self.visits += 1
        if action.name == "take":
            where = self.location.get(action.target)
            if where is None:
                return f"cannot find {action.target}"
            if action.where and action.where != where:
                return f"the {action.target} is not on the {action.where}; it is in the {where}"
            self.carried.add(action.target)
            self.location.pop(action.target, None)
            return f"took the {action.target} from the {where}"
        if action.name == "go":
            if self.locked.get(action.target) and "key" not in self.carried:
                return (f"the door to the {action.target} is locked; "
                        f"the key is in the {self.location.get('key', 'nowhere')}")
            self.room = action.target
            return f"went to the {action.target}"
        if action.name == "place":
            if action.target not in self.carried:
                return f"{action.target} is not being carried"
            self.carried.discard(action.target)
            self.placed[action.target] = action.where
            return f"placed the {action.target} on the {action.where}"
        return f"unknown action {action.name}"


@dataclass(frozen=True)
class Feedback:
    mode: str  # "in-plan" | "out-of-plan"
    reason: str
    replacement: tuple[Step, ...] = ()
    fixed_step: Step | None = None


WRONG_PLACE = re.compile(r"is not on the (?P<assumed>\w+); it is in the (?P<actual>\w+)")
LOCKED = re.compile(r"door to the (?P<room>\w+) is locked; the key is in the (?P<keyplace>\w+)")


def parse_feedback(observation: str, action: Step) -> Feedback | None:
    """Recognise the two feedback kinds; a real harness would ask the model instead."""
    wrong = WRONG_PLACE.search(observation)
    if wrong and action.name == "take":
        return Feedback("in-plan", observation,
                        fixed_step=Step("take", action.target, wrong.group("actual")))
    locked = LOCKED.search(observation)
    if locked and action.name == "go":
        room, keyplace = locked.group("room"), locked.group("keyplace")
        return Feedback("out-of-plan", observation,
                        replacement=(Step("go", keyplace), Step("take", "key", keyplace),
                                     Step("go", room), Step("place", "mug", "desk")))
    return None


def naive_plan() -> Plan:
    """Plan built from stale assumptions: wrong object location, no key for the locked door."""
    return Plan([
        Step("take", "mug", "counter"),   # actually in the cabinet
        Step("go", "study"),              # actually locked, key is in the hall
        Step("place", "mug", "desk"),
    ])


def run(env: MiniHouse, plan: Plan, *, adapt: bool,
        replan: Callable[[MiniHouse, int], Sequence[Step]] | None = None,
        max_steps: int = 50) -> dict:
    trace: list[str] = []
    for _ in range(max_steps):
        nxt = plan.next_step()
        if nxt is None:
            break
        index, action = nxt
        observation = env.step(action)
        trace.append(f"{action.render()} -> {observation}")
        feedback = parse_feedback(observation, action)
        if feedback is None:
            plan.mark_completed(index)
            continue
        if not adapt:
            break  # non-adaptive baseline: keep going as if nothing happened
        if feedback.mode == "in-plan" and feedback.fixed_step is not None:
            plan.revise_in_plan(index, feedback.fixed_step, feedback.reason)
        elif feedback.mode == "out-of-plan":
            replacement = feedback.replacement or (replan(env, index) if replan else ())
            plan.replan_remaining(index, replacement, feedback.reason)
    else:
        raise RuntimeError(f"plan did not settle within {max_steps} steps: {plan.revisions}")
    return {"trace": trace, "revisions": plan.revisions, "solved": env.goal_met(),
            "env_visits": env.visits}


def _demo() -> int:
    print("=== 1. 不自适应：照初始计划执行 ===")
    baseline = run(MiniHouse(), naive_plan(), adapt=False)
    for line in baseline["trace"]:
        print(f"  {line}")
    print(f"  solved={baseline['solved']}  env_visits={baseline['env_visits']}  "
          f"revisions={len(baseline['revisions'])}")
    assert not baseline["solved"], "the non-adaptive baseline must fail on stale assumptions"

    print("\n=== 2. 自适应：in-plan 修正参数 + out-of-plan 重规划 ===")
    adaptive = run(MiniHouse(), naive_plan(), adapt=True)
    for line in adaptive["trace"]:
        print(f"  {line}")
    print("  修订记录:")
    for revision in adaptive["revisions"]:
        print(f"    - {revision}")
    print(f"  solved={adaptive['solved']}  env_visits={adaptive['env_visits']}  "
          f"revisions={len(adaptive['revisions'])}")
    assert adaptive["solved"], adaptive
    modes = [revision.split("[")[0] for revision in adaptive["revisions"]]
    assert modes == ["in-plan", "out-of-plan"], modes

    print("\n=== 3. 反馈分类边界 ===")
    wrong = parse_feedback("the mug is not on the counter; it is in the cabinet", Step("take", "mug", "counter"))
    locked = parse_feedback("the door to the study is locked; the key is in the hall", Step("go", "study"))
    clean = parse_feedback("took the mug from the cabinet", Step("take", "mug", "cabinet"))
    print(f"  位置不符 -> {wrong.mode}（改这一步即可）")
    print(f"  门锁死   -> {locked.mode}（剩余计划作废，重规划 {len(locked.replacement)} 步）")
    print(f"  正常观测 -> {clean}")
    assert wrong.mode == "in-plan" and locked.mode == "out-of-plan" and clean is None

    print("\nself-test OK: 两类反馈被区分处理，自适应后达成目标，非自适应失败")
    return 0


def _replan_live(args: argparse.Namespace) -> int:
    from openai import OpenAI  # imported only for the live command

    client = OpenAI()
    prompt = ("A household plan failed with this observation. Return only JSON: a list of "
              "{\"name\", \"target\", \"where\"} steps that finish the task from the current state.\n\n"
              f"Observation: {args.observation}\nGoal: {args.goal}")
    raw = client.chat.completions.create(model=args.model,
                                         messages=[{"role": "user", "content": prompt}],
                                         temperature=0.0).choices[0].message.content
    print(json.dumps({"replan": raw}, ensure_ascii=False, indent=2))
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AdaPlanner-style adaptive planning")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo", help="offline deterministic in-plan/out-of-plan demo + self-test")
    live = sub.add_parser("replan-live", help="ask a live model for a re-plan")
    live.add_argument("--observation", required=True)
    live.add_argument("--goal", default="put the mug on the desk in the study")
    live.add_argument("--model", default="deepseek/deepseek-v4-flash")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command in (None, "demo"):
        return _demo()
    if args.command == "replan-live":
        return _replan_live(args)
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
