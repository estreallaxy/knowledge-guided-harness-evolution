#!/usr/bin/env python3
"""Plan-and-Solve prompting (arXiv:2305.04091), decoupled from any model client.

Paper mechanism kept here: instead of a bare "let's think step by step", the prompt
first asks for a plan and only then for the execution, and the PS+ variant additionally
asks the model to extract the relevant variables and their numerals before computing
(the paper's fix for calculation and missing-step errors).

The prompt strings below are copied verbatim from the pinned upstream snapshot
(`upstream/prompt.py`, `prompt_101` / `prompt_201` / `prompt_302`); the old upstream
scripts are kept under `upstream/` only for provenance and are not imported. This module
exposes prompt building, plan/execution splitting, answer extraction and a `ModelClient`
protocol, so the pipeline runs offline with a scripted client in `demo` and against an
OpenAI-compatible endpoint in `solve-live`.

`demo` exercises the pipeline, not model quality: it verifies which instruction reaches
the model, that the plan is recovered from the reply, and that the answer is extracted.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence

# --- prompt strings: verbatim from upstream/prompt.py ---------------------------------

PROMPTS: dict[str, str] = {
    # upstream prompt_101
    "cot": "Let's think step by step.",
    # upstream prompt_201
    "ps": "Let's first understand the problem and devise a plan to solve the problem. "
          "Then, let's carry out the plan to solve the problem step by step.",
    # upstream prompt_302
    "ps+": "Let's first understand the problem, extract relevant variables and their corresponding numerals, "
           "and devise a complete plan. Then, let's carry out the plan, calculate intermediate variables "
           "(pay attention to correct numerical calculation and commonsense), "
           "solve the problem step by step, and show the answer.",
}

# upstream config.py sets direct_answer_trigger_for_direct = "Therefore,the answer is"
ANSWER_TRIGGERS = ("Therefore, the answer is", "Therefore,the answer is", "The answer is")
EXECUTION_MARKERS = ("Then, let's carry out the plan", "carry out the plan", "Execution:", "execution:")
NUMBERED = re.compile(r"^\s*\d+[.)]\s+\S")


class ModelClient(Protocol):
    """Any object that can turn a prompt into text (OpenAI, litellm, a test double)."""

    def complete(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class PlanAndSolveResult:
    question: str
    variant: str
    prompt: str
    plan: tuple[str, ...]
    execution: str
    answer: str | None
    raw: str


def build_prompt(question: str, variant: str = "ps+") -> str:
    if variant not in PROMPTS:
        raise ValueError(f"unknown variant {variant!r}; expected one of {sorted(PROMPTS)}")
    return f"Q: {question}\nA: {PROMPTS[variant]}"


def split_plan_and_execution(text: str) -> tuple[tuple[str, ...], str]:
    """Recover the plan and the execution from a free-form reply.

    The marker is the prompt's own wording ("Then, let's carry out the plan"), so no
    extra output format has to be imposed on the model.
    """
    lines = text.splitlines()
    split_at = next((index for index, line in enumerate(lines)
                     if any(marker in line for marker in EXECUTION_MARKERS)), None)
    head = lines if split_at is None else lines[:split_at]
    tail = "" if split_at is None else "\n".join(lines[split_at:]).strip()
    plan = tuple(line.strip() for line in head if NUMBERED.match(line))
    return plan, tail


def extract_answer(text: str, triggers: Sequence[str] = ANSWER_TRIGGERS) -> str | None:
    for trigger in triggers:
        index = text.rfind(trigger)
        if index != -1:
            answer = text[index + len(trigger):].strip()
            return answer.rstrip(". ").strip() or None
    return None


def solve(question: str, client: ModelClient, variant: str = "ps+") -> PlanAndSolveResult:
    prompt = build_prompt(question, variant)
    raw = client.complete(prompt)
    plan, execution = split_plan_and_execution(raw)
    return PlanAndSolveResult(question, variant, prompt, plan, execution or raw.strip(),
                              extract_answer(raw), raw)


class ScriptedClient:
    """Deterministic test double: replies are keyed by the instruction that was sent."""

    def __init__(self, replies: dict[str, str]) -> None:
        self.replies = replies
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if prompt not in self.replies:
            raise KeyError(f"no scripted reply for prompt: {prompt[:60]}...")
        return self.replies[prompt]


Q1 = ("Natalia sold clips to 48 friends in April, and then she sold half as many clips in May. "
      "How many clips did Natalia sell altogether in April and May?")
Q2 = ("A pet store had 3 puppies and sold 2 of them in the morning. "
      "How many puppies are left in the store?")

R1 = """1. April sales are given as 48 clips.
2. May sales are half of April, so 48 / 2 = 24 clips.
3. The total is April plus May.
Then, let's carry out the plan:
1. April = 48 clips.
2. May = 48 / 2 = 24 clips.
3. Altogether = 48 + 24 = 72 clips.
Therefore, the answer is 72."""

R2 = """1. Start with the number of puppies in the store.
2. Subtract the puppies that were sold.
Then, let's carry out the plan:
1. In the morning the store had 3 puppies.
2. It sold 2, so 3 - 2 = 1 puppy is left.
Therefore, the answer is 1."""


def _demo() -> int:
    print("=== 1. 三个变体的指令（cot / ps / ps+） ===")
    for variant in ("cot", "ps", "ps+"):
        tail = PROMPTS[variant].split(". ")[0]
        print(f"  {variant:<4} {tail}...")
    assert "extract relevant variables" in PROMPTS["ps+"], "PS+ must keep the extraction instruction"
    assert "devise a plan" in PROMPTS["ps"] and "plan" not in PROMPTS["cot"].split("step")[0]

    print("\n=== 2. 同一条问题走三个变体（scripted client，不联网） ===")
    replies = {build_prompt(Q1, "ps+"): R1, build_prompt(Q2, "ps+"): R2,
               build_prompt(Q1, "ps"): R1, build_prompt(Q2, "ps"): R2,
               build_prompt(Q1, "cot"): "48 + 24 = 72.\nTherefore, the answer is 72.",
               build_prompt(Q2, "cot"): "3 - 2 = 1.\nTherefore, the answer is 1."}
    client = ScriptedClient(replies)
    for variant in ("cot", "ps", "ps+"):
        result = solve(Q1, client, variant)
        print(f"  {variant:<4} plan_steps={len(result.plan)}  answer={result.answer!r}")
        assert result.answer == "72", (variant, result.answer)

    print("\n=== 3. 从自由文本回复里还原 plan 与 execution ===")
    parsed = solve(Q2, client, "ps+")
    print(f"  prompt 结尾 : {parsed.prompt.splitlines()[-1][-46:]}")
    print(f"  还原出的 plan ({len(parsed.plan)} 步):")
    for step in parsed.plan:
        print(f"    - {step}")
    print(f"  execution 首行: {parsed.execution.splitlines()[0]}")
    assert len(parsed.plan) == 2 and parsed.plan[0].startswith("1."), parsed.plan
    assert parsed.execution.startswith("Then, let's carry out the plan"), parsed.execution

    print("\n=== 4. 边界：cot 不给计划、答案缺失、变体名校验 ===")
    cot = solve(Q2, client, "cot")
    print(f"  cot: plan_steps={len(cot.plan)}（无编号计划，符合预期）  answer={cot.answer!r}")
    assert cot.plan == () and cot.answer == "1"
    assert extract_answer("no trigger here") is None
    try:
        build_prompt(Q1, "ps-plus")
        raise AssertionError("unknown variant must be rejected")
    except ValueError as exc:
        print(f"  未知变体被拒: {exc}")

    print("\nself-test OK: 提示模板与客户端解耦，PS/PS+ 计划可还原、答案可提取")
    return 0


class OpenAIClient:
    """Live client; imported lazily so the offline demo needs no third-party package."""

    def __init__(self, model: str, temperature: float = 0.0) -> None:
        from openai import OpenAI  # imported only when the live path is used

        self._client = OpenAI()
        self._model = model
        self._temperature = temperature

    def complete(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model, temperature=self._temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


def _solve_live(args: argparse.Namespace) -> int:
    result = solve(args.question, OpenAIClient(args.model), args.variant)
    print(json.dumps({"variant": result.variant, "plan": list(result.plan),
                      "answer": result.answer, "raw": result.raw[:400]},
                     ensure_ascii=False, indent=2))
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan-and-Solve prompting (client-agnostic)")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo", help="offline deterministic pipeline demo + self-test")
    live = sub.add_parser("solve-live", help="run one question through a live model")
    live.add_argument("--question", required=True)
    live.add_argument("--variant", choices=sorted(PROMPTS), default="ps+")
    live.add_argument("--model", default="deepseek/deepseek-v4-flash")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command in (None, "demo"):
        return _demo()
    if args.command == "solve-live":
        return _solve_live(args)
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
