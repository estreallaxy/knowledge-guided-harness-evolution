#!/usr/bin/env python3
"""Request-level strong/weak model routing (RouteLLM-style), runnable offline.

Mechanism (RouteLLM, arXiv:2406.18665): a router decides, per request, whether the
cheap "weak" model is enough or the expensive "strong" model is needed, and a single
threshold trades quality for cost. The paper learns the router from preference data;
this module keeps the mechanism (calibrated threshold over a difficulty scorer) and
makes the scorer pluggable, so calibration is testable without a model provider.

`demo` and the self-test never import `openai` and never touch the network. `route`
uses an OpenAI-compatible endpoint and needs `openai` installed plus credentials in
the environment.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

Scorer = Callable[[str], float]


@dataclass(frozen=True)
class RouteDecision:
    model: str
    difficulty: float
    threshold: float


@dataclass(frozen=True)
class DevRecord:
    """One calibration example: scorer output plus each model's quality and cost."""

    score: float
    weak_quality: float
    strong_quality: float
    weak_cost: float
    strong_cost: float


@dataclass(frozen=True)
class PolicyEval:
    threshold: float
    mean_quality: float
    mean_cost: float
    escalation_rate: float
    win_rate: float


class PreferenceRouter:
    """Threshold policy over a difficulty scorer; scoring is supplied by the caller."""

    def __init__(self, weak_model: str, strong_model: str, threshold: float, scorer: Scorer) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be in [0, 1]")
        self.weak_model = weak_model
        self.strong_model = strong_model
        self.threshold = threshold
        self.scorer = scorer

    def route(self, request: str) -> RouteDecision:
        difficulty = self.scorer(request)
        if not 0.0 <= difficulty <= 1.0:
            raise ValueError("scorer must return a value in [0, 1]")
        model = self.strong_model if difficulty >= self.threshold else self.weak_model
        return RouteDecision(model, difficulty, self.threshold)


def evaluate_threshold(records: Sequence[DevRecord], threshold: float, win_quality: float = 0.5) -> PolicyEval:
    """Quality/cost of routing `records` at `threshold`.

    `win_rate` counts requests whose *chosen* model scores at least `win_quality`, while
    `mean_quality` keeps the raw score, so escalating on the wrong requests shows up as
    high cost with little quality gain.
    """
    if not records:
        raise ValueError("no dev records")
    quality = 0.0
    cost = 0.0
    escalations = 0
    wins = 0
    for record in records:
        strong = record.score >= threshold
        escalations += int(strong)
        chosen = record.strong_quality if strong else record.weak_quality
        quality += chosen
        cost += record.strong_cost if strong else record.weak_cost
        wins += int(chosen >= win_quality)
    total = len(records)
    return PolicyEval(threshold, quality / total, cost / total, escalations / total, wins / total)


def calibrate(
    records: Sequence[DevRecord],
    *,
    quality_target: float | None = None,
    cost_budget: float | None = None,
    grid: int = 101,
    win_quality: float = 0.5,
) -> PolicyEval:
    """Pick the threshold on a grid.

    Exactly one of `quality_target` (minimise cost subject to a mean-quality floor) or
    `cost_budget` (maximise quality subject to a mean-cost ceiling) must be given. Ties
    are broken on the remaining objective, then on the lower threshold (fewer expensive
    calls for the same measured quality).
    """
    if (quality_target is None) == (cost_budget is None):
        raise ValueError("give exactly one of quality_target / cost_budget")
    candidates = [evaluate_threshold(records, step / (grid - 1), win_quality) for step in range(grid)]
    feasible = [
        cand
        for cand in candidates
        if (cost_budget is None or cand.mean_cost <= cost_budget + 1e-12)
        and (quality_target is None or cand.mean_quality >= quality_target - 1e-12)
    ]
    if not feasible:
        raise ValueError("no threshold on the grid satisfies the constraint")
    if quality_target is not None:
        return min(feasible, key=lambda c: (round(c.mean_cost, 9), -c.mean_quality, c.threshold))
    return max(feasible, key=lambda c: (round(c.mean_quality, 9), -c.mean_cost, -c.threshold))


def apply_calibration(router: PreferenceRouter, records: Sequence[DevRecord], **kwargs: float) -> PreferenceRouter:
    """Return a copy of `router` whose threshold comes from dev-set calibration."""
    best = calibrate(records, **kwargs)
    return PreferenceRouter(router.weak_model, router.strong_model, best.threshold, router.scorer)


class KeywordDifficultyScorer:
    """Deterministic offline stand-in for the paper's trained preference model.

    Production swaps in the trained router; the policy code only needs a `str -> [0, 1]`
    callable, which keeps calibration and evaluation unit-testable offline.
    """

    HARD_MARKERS = ("prove", "derive", "optimise", "optimize", "debug", "refactor", "why")

    def __init__(self, pivot: int = 40) -> None:
        self.pivot = pivot

    def __call__(self, request: str) -> float:
        length_term = min(len(request.split()) / (2.0 * self.pivot), 1.0)
        marker_term = 0.35 if any(tok in request.lower() for tok in self.HARD_MARKERS) else 0.0
        return min(1.0, length_term + marker_term)


def synthetic_dev(n: int = 200) -> list[DevRecord]:
    """Deterministic dev set where difficulty drives the strong model's advantage."""
    records = []
    for index in range(n):
        score = (index % 20) / 20.0  # max 0.95, so threshold 1.0 means "never escalate"
        records.append(DevRecord(score, 0.35 + 0.15 * score, 0.80 + 0.15 * score, 0.01, 0.20))
    return records


def _live_route(args: argparse.Namespace) -> int:
    from openai import OpenAI  # imported only for the live command

    client = OpenAI()
    prompt = ("Rate how hard this request is for a small model, 0..1. "
              "Answer with a single number.\n\n" + args.request)
    raw = client.chat.completions.create(
        model=args.scorer_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    ).choices[0].message.content
    try:
        difficulty = min(1.0, max(0.0, float(str(raw).strip().split()[0])))
    except (ValueError, IndexError) as exc:
        raise SystemExit(f"scorer returned an unparsable value: {raw!r}") from exc
    model = args.strong_model if difficulty >= args.threshold else args.weak_model
    print(json.dumps({"difficulty": difficulty, "threshold": args.threshold, "model": model},
                     ensure_ascii=False))
    return 0


def _demo() -> int:
    records = synthetic_dev()
    always_weak = evaluate_threshold(records, 1.0)
    always_strong = evaluate_threshold(records, 0.0)
    calibrated = calibrate(records, cost_budget=0.05)
    print("policy                 quality  cost  escalate   win")
    for name, ev in (("always weak", always_weak), ("always strong", always_strong),
                     (f"calibrated tau={calibrated.threshold:.2f}", calibrated)):
        print(f"{name:<22}{ev.mean_quality:7.3f}{ev.mean_cost:6.3f}{ev.escalation_rate:9.2f}{ev.win_rate:6.3f}")

    assert calibrated.mean_cost <= 0.05 + 1e-9, calibrated
    assert always_weak.mean_quality < calibrated.mean_quality < always_strong.mean_quality, calibrated
    assert always_strong.win_rate == 1.0
    assert evaluate_threshold(records, 1.0).escalation_rate == 0.0
    assert apply_calibration(PreferenceRouter("w", "s", 0.0, KeywordDifficultyScorer()), records,
                             quality_target=0.85).threshold < 0.5

    router = PreferenceRouter("weak", "strong", 0.35, KeywordDifficultyScorer())
    assert [router.route(t).model for t in ("hi", "why does this deadlock")] == ["weak", "strong"]
    print("self-test OK: calibrated router stays under budget and beats always-weak quality")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RouteLLM-style request routing")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo", help="offline deterministic calibration demo + self-test")
    live = sub.add_parser("route", help="route one request through a live scorer")
    live.add_argument("--request", required=True)
    live.add_argument("--threshold", type=float, default=0.5)
    live.add_argument("--weak-model", default="deepseek/deepseek-v4-flash")
    live.add_argument("--strong-model", default="deepseek/deepseek-v4-flash")
    live.add_argument("--scorer-model", default="deepseek/deepseek-v4-flash")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command in (None, "demo"):
        return _demo()
    if args.command == "route":
        return _live_route(args)
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
