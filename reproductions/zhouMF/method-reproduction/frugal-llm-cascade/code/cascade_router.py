#!/usr/bin/env python3
"""Quality-gated LLM cascade (FrugalGPT, arXiv:2305.05176).

Paper mechanism kept here: queries go to the cheapest model first, a *scoring* function
decides whether that answer is good enough, and only the rejected ones escalate to a
larger, more expensive model. The gate is what makes the cascade work, so it has to be
calibrated on development data: too high and you pay for the big model anyway, too low
and wrong answers pass the gate.

`demo` calibrates the gate on a deterministic development set with no model and no
network, then compares the cascade against always-cheap and always-expensive, including
the cost of the gate itself.
`run-live` wires the same cascade to an OpenAI-compatible endpoint.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, replace
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class StageResponse:
    answer: str
    confidence: float


@dataclass(frozen=True)
class CascadeStage:
    name: str
    cost: float
    invoke: Callable[[str], StageResponse]


@dataclass(frozen=True)
class CascadeResult:
    answer: str
    selected_stage: str
    accumulated_cost: float
    escalations: int


def run_cascade(task: str, stages: Sequence[CascadeStage], tau: float,
                gate_cost: float = 0.0) -> CascadeResult:
    """Walk cheap -> expensive; accept the first answer whose confidence clears `tau`."""
    if not stages:
        raise ValueError("at least one cascade stage is required")
    cost = 0.0
    escalations = 0
    for stage in stages:
        response = stage.invoke(task)
        cost += stage.cost
        if response.confidence >= tau or stage is stages[-1]:
            return CascadeResult(response.answer, stage.name, cost, escalations)
        cost += gate_cost  # the scoring/verification step is not free
        escalations += 1
    raise AssertionError("unreachable")


@dataclass(frozen=True)
class DevItem:
    """Development query: per-stage confidence and ground-truth correctness."""

    query: str
    confidences: tuple[float, ...]
    correct: tuple[bool, ...]


@dataclass(frozen=True)
class CascadeEval:
    tau: float
    quality: float
    mean_cost: float
    escalation_rate: float


def evaluate_cascade(dev: Sequence[DevItem], stages: Sequence[CascadeStage], tau: float,
                     gate_cost: float = 0.0) -> CascadeEval:
    correct = 0
    cost = 0.0
    escalated = 0
    for item in dev:
        chosen = len(stages) - 1
        item_escalated = False
        for index, stage in enumerate(stages):
            cost += stage.cost
            if item.confidences[index] >= tau or index == len(stages) - 1:
                chosen = index
                break
            cost += gate_cost
            item_escalated = True
        escalated += int(item_escalated)
        correct += int(item.correct[chosen])
    total = len(dev)
    return CascadeEval(tau, correct / total, cost / total, escalated / total)


def calibrate_cascade(dev: Sequence[DevItem], stages: Sequence[CascadeStage],
                      quality_target: float, gate_cost: float = 0.0,
                      grid: int = 101) -> CascadeEval:
    """Smallest gate threshold that still meets the quality target, at minimum cost."""
    candidates = [evaluate_cascade(dev, stages, step / (grid - 1), gate_cost) for step in range(grid)]
    feasible = [c for c in candidates if c.quality >= quality_target - 1e-12]
    if not feasible:
        raise ValueError("no gate threshold on the grid reaches the quality target")
    return min(feasible, key=lambda c: (round(c.mean_cost, 9), -c.quality, -c.tau))


def _stages() -> list[CascadeStage]:
    """Three synthetic models: cheap/small -> mid -> expensive/large, deterministic."""

    def make_stage(threshold: float, confidence: Callable[[float], float], cost: float, name: str) -> CascadeStage:
        def invoke(query: str) -> StageResponse:
            difficulty = float(query.split("d=")[1])
            return StageResponse(answer=f"{name}-answer", confidence=confidence(difficulty))

        return CascadeStage(name, cost, invoke)

    return [
        make_stage(0.35, lambda d: 0.95 - 0.9 * d, 0.002, "small"),
        make_stage(0.70, lambda d: 0.90 - 0.5 * d, 0.020, "medium"),
        make_stage(0.95, lambda d: 0.98, 0.200, "large"),
    ]


def dev_items(n: int = 100) -> list[DevItem]:
    stages = _stages()
    items = []
    for index in range(n):
        difficulty = (index % 20) / 19.0
        query = f"q{index} d={difficulty:.2f}"
        responses = [stage.invoke(query) for stage in stages]
        correct = tuple(difficulty <= threshold for threshold in (0.35, 0.70, 0.95))
        items.append(DevItem(query, tuple(r.confidence for r in responses), correct))
    return items


def _demo() -> int:
    stages = _stages()
    dev = dev_items()
    gate_cost = 0.001

    print("=== 1. 固定策略对照（同一批开发查询） ===")
    cheap = evaluate_cascade(dev, stages, tau=0.0, gate_cost=gate_cost)       # 首个模型直接采纳
    expensive = evaluate_cascade(dev, stages, tau=1.1, gate_cost=gate_cost)   # 一律升到最大模型
    print(f"always-small   quality={cheap.quality:.3f}  cost={cheap.mean_cost:.4f}  "
          f"escalated={cheap.escalation_rate:.0%}")
    print(f"always-large   quality={expensive.quality:.3f}  cost={expensive.mean_cost:.4f}  "
          f"escalated={expensive.escalation_rate:.0%}")

    print("\n=== 2. 门槛校准：在质量目标下取最小成本 ===")
    target = 0.90
    best = calibrate_cascade(dev, stages, target, gate_cost)
    print(f"target={target}  ->  tau={best.tau:.2f}  quality={best.quality:.3f}  "
          f"cost={best.mean_cost:.4f}  escalation={best.escalation_rate:.0%}")

    print("\n=== 3. 门槛选错的代价（同一批开发数据） ===")
    print("tau     quality  cost     escalation")
    for tau in (0.00, 0.30, best.tau, 0.95, 1.00):
        ev = evaluate_cascade(dev, stages, tau, gate_cost)
        mark = "  <- calibrated" if abs(tau - best.tau) < 1e-9 else ""
        print(f"{tau:5.2f}   {ev.quality:7.3f}  {ev.mean_cost:7.4f}  {ev.escalation_rate:9.0%}{mark}")

    print("\n=== 4. 一次真实调用 ===")
    result = run_cascade("q0 d=0.90", stages, best.tau, gate_cost)
    print(f"query q0(d=0.90) -> {result.answer} at stage '{result.selected_stage}', "
          f"cost={result.accumulated_cost:.4f}, escalations={result.escalations}")

    assert best.quality >= target - 1e-12, best
    assert best.mean_cost < expensive.mean_cost * 0.5, (best, expensive)
    assert best.quality > cheap.quality, (best, cheap)
    assert result.selected_stage == "large", result.selected_stage
    print("\nself-test OK: 校准后的级联在质量达标的同时显著低于 always-large 成本")
    return 0


def _run_live(args: argparse.Namespace) -> int:
    from openai import OpenAI  # imported only for the live command

    client = OpenAI()

    def make(model: str, cost: float, name: str) -> CascadeStage:
        def invoke(query: str) -> StageResponse:
            text = client.chat.completions.create(
                model=model, messages=[{"role": "user", "content": query}], temperature=0.0
            ).choices[0].message.content or ""
            return StageResponse(text, 0.9)  # replace with a real scoring function

        return CascadeStage(name, cost, invoke)

    models = [m for m in args.models.split(",") if m]
    stages = [make(model, 0.01 * (index + 1), f"stage{index}") for index, model in enumerate(models)]
    result = run_cascade(args.query, stages, args.tau, gate_cost=0.001)
    print(json.dumps({"stage": result.selected_stage, "cost": result.accumulated_cost,
                      "answer": result.answer[:200]}, ensure_ascii=False, indent=2))
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Quality-gated LLM cascade (FrugalGPT)")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo", help="offline deterministic calibration demo + self-test")
    live = sub.add_parser("run-live", help="run one query through a live cascade")
    live.add_argument("--query", required=True)
    live.add_argument("--tau", type=float, default=0.5)
    live.add_argument("--models", default="deepseek/deepseek-v4-flash")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command in (None, "demo"):
        return _demo()
    if args.command == "run-live":
        return _run_live(args)
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
