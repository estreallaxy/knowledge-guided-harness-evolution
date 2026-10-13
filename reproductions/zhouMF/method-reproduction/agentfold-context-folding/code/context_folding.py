#!/usr/bin/env python3
"""Proactive multi-scale context folding (AgentFold, arXiv:2510.24699).

Paper mechanism kept here: the context is kept as a small task anchor plus a long-term
memory of summaries plus the most recent high-fidelity interactions. The agent folds
**fine** (summarise the interactions it just finished) and, less often, **deep**
(consolidate several summaries of a completed sub-task into one). Deep folds are where
detail dies, so the fold instruction must carry critical evidence forward explicitly.

`demo` drives that policy over a deterministic long-horizon trajectory with no model and
no network, and shows: context size stays bounded instead of growing linearly, every
`KEY:` evidence line survives the folds, and the ablation without a "keep the key lines"
instruction silently loses evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

Summarizer = Callable[[Sequence[str]], str]
KEY_MARKER = "KEY:"


@dataclass(frozen=True)
class Interaction:
    action: str
    observation: str

    def render(self) -> str:
        return f"{self.action} -> {self.observation}"


def keep_key_summarizer(items: Sequence[str], width: int = 46) -> str:
    """Fold with the instruction that matters: critical evidence is carried verbatim."""
    key_lines = [line for item in items for line in item.splitlines() if KEY_MARKER in line]
    others = [line.strip() for item in items for line in item.splitlines() if KEY_MARKER not in line]
    body = "; ".join(line[:width] for line in others)
    return " | ".join(key_lines + ([body] if body else []))


def lossy_summarizer(items: Sequence[str], width: int = 24) -> str:
    """Ablation: fold everything by truncation, with no rule for critical evidence."""
    return "; ".join(line.strip()[:width] for item in items for line in item.splitlines())


@dataclass
class ContextWorkspace:
    question: str
    summaries: list[str] = field(default_factory=list)
    recent: list[Interaction] = field(default_factory=list)
    fold_log: list[str] = field(default_factory=list)

    def add(self, action: str, observation: str) -> None:
        self.recent.append(Interaction(action, observation))

    def fold_recent(self, summarizer: Summarizer) -> str:
        """Fine fold: compress the interactions just finished into one memory line."""
        if not self.recent:
            raise ValueError("nothing to fold")
        folded = summarizer([item.render() for item in self.recent])
        self.summaries.append(folded)
        self.fold_log.append(f"fine: {len(self.recent)} interactions -> {len(folded)} chars")
        self.recent.clear()
        return folded

    def consolidate(self, start: int, end: int, summarizer: Summarizer) -> None:
        """Deep fold: condense a completed sub-task that spans several summaries."""
        if not 0 <= start < end <= len(self.summaries):
            raise ValueError("invalid summary range")
        merged = summarizer(self.summaries[start:end])
        self.summaries[start:end] = [merged]
        self.fold_log.append(f"deep: summaries[{start}:{end}] -> {len(merged)} chars")

    def render(self) -> str:
        memory = "\n".join(f"- {item}" for item in self.summaries) or "- (empty)"
        latest = "\n".join(item.render() for item in self.recent) or "(none)"
        return (f"Task:\n{self.question}\n\nLong-term memory:\n{memory}\n\n"
                f"Latest interactions:\n{latest}")

    def missing_evidence(self, evidence: Sequence[str]) -> tuple[str, ...]:
        text = self.render()
        return tuple(item for item in evidence if item not in text)


@dataclass
class FoldingPolicy:
    recent_budget: int
    summary_budget: int

    def maybe_fold(self, workspace: ContextWorkspace, summarizer: Summarizer) -> None:
        if len(workspace.recent) > self.recent_budget:
            workspace.fold_recent(summarizer)
        while len(workspace.summaries) > self.summary_budget:
            workspace.consolidate(0, 2, summarizer)  # deep-fold the oldest completed sub-task


def long_horizon(steps: int = 120) -> tuple[str, list[tuple[str, str]], list[str]]:
    """Deterministic long-horizon trajectory with periodic critical evidence."""
    question = "find which service each component depends on and produce a dependency report"
    events: list[tuple[str, str]] = []
    evidence: list[str] = []
    for index in range(steps):
        component = f"comp-{index % 7}"
        events.append((f"step {index}: inspect {component}", f"{component} reports metric {index}"))
        if index % 24 == 23:
            fact = f"{KEY_MARKER} {component} depends on service svc-{index % 7}"
            events.append((f"step {index}: query dependency graph", fact))
            evidence.append(fact)
    return question, events, evidence


def _run(policy: FoldingPolicy | None, summarizer: Summarizer,
         events: Sequence[tuple[str, str]], question: str) -> tuple[ContextWorkspace, list[int]]:
    workspace = ContextWorkspace(question)
    sizes: list[int] = []
    for action, observation in events:
        workspace.add(action, observation)
        if policy is not None:
            policy.maybe_fold(workspace, summarizer)
        sizes.append(len(workspace.render()))
    return workspace, sizes


def _demo() -> int:
    question, events, evidence = long_horizon()
    policy = FoldingPolicy(recent_budget=6, summary_budget=4)

    print("=== 1. 不折叠：上下文随步数线性增长 ===")
    _, raw_sizes = _run(None, keep_key_summarizer, events, question)
    print(f"{len(events)} 步后 render() = {raw_sizes[-1]} chars（第 1 步 {raw_sizes[0]} chars）")
    growth = raw_sizes[-1] / raw_sizes[0]
    print(f"增长倍数 {growth:.1f}x")
    assert growth > 3, growth

    print("\n=== 2. 主动折叠：任务锚点 + 长期摘要 + 最近高保真交互 ===")
    folded, folded_sizes = _run(policy, keep_key_summarizer, events, question)
    print(f"折叠后 render() = {folded_sizes[-1]} chars（峰值 {max(folded_sizes)}）")
    print(f"折叠次数 fine/deep: {sum('fine' in line for line in folded.fold_log)}/"
          f"{sum('deep' in line for line in folded.fold_log)}")
    print(f"长期记忆 {len(folded.summaries)} 条，最近交互 {len(folded.recent)} 条")
    assert folded_sizes[-1] < raw_sizes[-1] / 2, (folded_sizes[-1], raw_sizes[-1])
    assert any("deep" in line for line in folded.fold_log), "the demo must exercise a deep fold"

    print("\n=== 3. 关键证据是否在折叠中存活 ===")
    missing = folded.missing_evidence(evidence)
    print(f"必须保留的证据 {len(evidence)} 条，丢失 {len(missing)} 条")
    for fact in evidence:
        print(f"  {'OK ' if fact not in missing else 'LOST'} {fact}")
    assert not missing, missing

    print("\n=== 4. 消融：折叠指令不含「保留关键证据」会怎样 ===")
    ablated, _ = _run(policy, lossy_summarizer, events, question)
    lost = ablated.missing_evidence(evidence)
    print(f"无保留指令时丢失 {len(lost)}/{len(evidence)} 条关键证据")
    assert lost, "the ablation must lose evidence, otherwise the demo proves nothing"

    print("\nself-test OK: 折叠把上下文压在预算内、关键证据全部存活，去掉保留指令即丢失")
    return 0


def _fold_live(args: argparse.Namespace) -> int:
    from openai import OpenAI  # imported only for the live command

    client = OpenAI()
    _, events, _ = long_horizon(steps=12)
    prompt = ("Fold these agent interactions into one memory line. Preserve any line containing "
              f"'{KEY_MARKER}' verbatim. Answer with the folded line only.\n\n"
              + "\n".join(f"{a} -> {o}" for a, o in events))
    raw = client.chat.completions.create(model=args.model,
                                         messages=[{"role": "user", "content": prompt}],
                                         temperature=0.0).choices[0].message.content
    print(json.dumps({"folded": raw}, ensure_ascii=False, indent=2))
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Proactive context folding (AgentFold)")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo", help="offline deterministic folding demo + self-test")
    live = sub.add_parser("fold-live", help="fold one window through a live model")
    live.add_argument("--model", default="deepseek/deepseek-v4-flash")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command in (None, "demo"):
        return _demo()
    if args.command == "fold-live":
        return _fold_live(args)
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
