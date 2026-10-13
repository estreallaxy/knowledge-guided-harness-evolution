#!/usr/bin/env python3
"""Failure-guided context compression (ACON, arXiv:2510.00615).

Paper mechanism kept here: history and observations are compressed once they exceed a
budget, and the compression *guideline* is improved from development trajectories in
which the full context succeeded but the compressed context failed - the facts that went
missing name the rule that must be added. The compressed layer stays separate from the
agent's decisions, and the guideline is revised only from development failures.

`demo` runs the revision loop on deterministic development trajectories with no model
and no network. It shows: a naive guideline loses facts -> the failures become explicit
retention rules over several rounds -> the revised guideline keeps every required fact
while still cutting context size well below the full history.
`summarize-live` is the optional live path where summary text comes from a model.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, replace
from typing import Callable, Iterable, Sequence

Summarizer = Callable[[Sequence["ContextItem"]], str]


@dataclass(frozen=True)
class ContextItem:
    """One message in the running context. `kind` drives the retention rules."""

    kind: str  # system | user | assistant | tool_call | observation | result
    text: str


@dataclass(frozen=True)
class Guideline:
    """The compression policy; `revisions` is its auditable history."""

    keep_recent: int
    retain_kinds: tuple[str, ...] = ("system",)
    revisions: tuple[str, ...] = ()

    def add_rule(self, kind: str, why: str) -> "Guideline":
        if kind in self.retain_kinds:
            return self
        return replace(self, retain_kinds=self.retain_kinds + (kind,),
                       revisions=self.revisions + (f"retain {kind}: {why}",))


@dataclass(frozen=True)
class CompressionResult:
    guideline: Guideline
    summary: ContextItem
    retained: tuple[ContextItem, ...]
    original_characters: int
    compressed_characters: int

    def render(self) -> str:
        tail = "\n".join(item.text for item in self.retained)
        return f"{self.summary.text}\n{tail}" if tail else self.summary.text


def default_summarizer(budget: int = 110) -> Summarizer:
    """Deterministic, deliberately lossy stand-in for the paper's distilled compressor."""

    def summarize(items: Sequence[ContextItem]) -> str:
        if not items:
            return "[summary] (nothing dropped)"
        preview = "; ".join(item.text.strip().replace("\n", " ")[:28] for item in items)
        text = f"[summary of {len(items)} dropped steps] {preview}"
        return text if len(text) <= budget else text[:budget].rstrip() + "..."

    return summarize


def compress_if_needed(history: Sequence[ContextItem], guideline: Guideline, budget: int,
                       summarize: Summarizer) -> CompressionResult | None:
    """Compress only when the history exceeds `budget`; otherwise return None."""
    if sum(len(item.text) for item in history) <= budget:
        return None
    keep = set(guideline.retain_kinds)
    recent = set(range(max(0, len(history) - guideline.keep_recent), len(history)))
    retained = tuple(item for index, item in enumerate(history)
                     if index in recent or item.kind in keep)
    dropped = [item for index, item in enumerate(history)
               if index not in recent and item.kind not in keep]
    summary = ContextItem("summary", summarize(dropped))
    return CompressionResult(guideline, summary, retained,
                             sum(len(item.text) for item in history),
                             len(summary.text) + sum(len(item.text) for item in retained))


def agent_succeeds(context_text: str, required_facts: Sequence[str]) -> bool:
    """Stand-in for the downstream agent: it fails once a required fact left the context."""
    return all(fact in context_text for fact in required_facts)


def find_missing_facts(history: Sequence[ContextItem], required_facts: Sequence[str],
                       guideline: Guideline, budget: int, summarize: Summarizer) -> tuple[str, ...]:
    full_text = "\n".join(item.text for item in history)
    assert agent_succeeds(full_text, required_facts), "the full context must always pass"
    result = compress_if_needed(history, guideline, budget, summarize)
    if result is None:
        return ()
    return tuple(fact for fact in required_facts if fact not in result.render())


def revise_guideline(guideline: Guideline, history: Sequence[ContextItem],
                     missing_facts: Sequence[str]) -> Guideline:
    """Turn each lost fact into a retention rule, naming the item kind that carried it."""
    revised = guideline
    for fact in missing_facts:
        kinds = [item.kind for item in history if fact in item.text]
        if kinds:
            revised = revised.add_rule(kinds[0], f"compressed context lost {fact!r} on a dev task")
    return revised


def _install_traj() -> tuple[str, tuple[ContextItem, ...], tuple[str, ...]]:
    lines = [
        ("system", "You are a terminal agent. Keep tool state and verified results."),
        ("user", "install the pinned dependencies and confirm nothing is broken"),
        ("tool_call", "pip install --dry-run -r requirements.txt"),
        ("observation", "resolver reports 42 packages with no conflicts"),
        ("assistant", "proceeding with the real install"),
        ("tool_call", "pip install -r requirements.txt"),
        ("observation", "downloaded 42 packages into the environment"),
        ("assistant", "waiting on the resolver to finish"),
        ("tool_call", "pip check"),
        ("observation", "no broken requirements found"),
        ("result", "pip install exited with code 0"),
        ("tool_call", "python -c 'import numpy'"),
        ("observation", "numpy imports fine"),
        ("tool_call", "python -c 'import requests'"),
        ("observation", "requests imports fine"),
        ("assistant", "install verified, reporting back"),
    ]
    required = ("no broken requirements found", "pip install exited with code 0")
    return "install-deps", tuple(ContextItem(k, t) for k, t in lines), required


def _service_traj() -> tuple[str, tuple[ContextItem, ...], tuple[str, ...]]:
    lines = [
        ("system", "You are a terminal agent. Keep tool state and verified results."),
        ("user", "make the service start again with the corrected configuration"),
        ("tool_call", "cat /etc/svc.conf"),
        ("observation", "timeout is set to 1s while the unit expects 30s"),
        ("assistant", "raising the timeout and restarting the unit"),
        ("tool_call", "sed -i 's/timeout=1s/timeout=30s/' /etc/svc.conf"),
        ("observation", "configuration rewritten"),
        ("tool_call", "systemctl daemon-reload"),
        ("observation", "daemon reloaded"),
        ("tool_call", "systemctl restart svc"),
        ("result", "healthcheck returned OK after restart"),
        ("tool_call", "systemctl status svc"),
        ("observation", "svc is active (running)"),
        ("assistant", "wrapping up"),
    ]
    required = ("healthcheck returned OK after restart", "svc is active (running)")
    return "fix-config", tuple(ContextItem(k, t) for k, t in lines), required


def dev_trajectories() -> list[tuple[str, tuple[ContextItem, ...], tuple[str, ...]]]:
    return [_install_traj(), _service_traj()]


def _demo() -> int:
    summarize = default_summarizer()
    budget = 300  # both development trajectories exceed this, so compression triggers
    guideline = Guideline(keep_recent=2)  # naive: system + the last two messages
    dev = dev_trajectories()

    def report(label: str, gl: Guideline) -> list[tuple[str, tuple[ContextItem, ...], tuple[str, ...]]]:
        print(f"\n{label}")
        bad = []
        for task, history, facts in dev:
            missing = find_missing_facts(history, facts, gl, budget, summarize)
            result = compress_if_needed(history, gl, budget, summarize)
            assert result is not None
            print(f"  {task:<13} chars {result.original_characters:>4} -> "
                  f"{result.compressed_characters:>4} ({result.compressed_characters / result.original_characters:>4.0%})"
                  f"  missing={len(missing)}/{len(facts)}")
            if missing:
                bad.append((task, history, missing))
        return bad

    print("=== 1. 朴素压缩指南：比较「全量成功 vs 压缩失败」 ===")
    failures = report("keep_recent=2, retain_kinds=('system',)", guideline)
    assert failures, "the naive guideline must lose facts for the revision loop to be meaningful"

    print("\n=== 2. 由失败反推规则（可多轮，直到开发集无失败） ===")
    for round_index in range(1, 4):
        for task, history, missing in failures:
            guideline = revise_guideline(guideline, history, missing)
        print(f"  round {round_index}: 累计规则 {list(guideline.revisions)}")
        failures = report(f"  轮 {round_index} 后:", guideline)
        if not failures:
            break
    assert not failures, failures

    before = after = 0
    for task, history, facts in dev:
        result = compress_if_needed(history, guideline, budget, summarize)
        assert result is not None
        before += result.original_characters
        after += result.compressed_characters
    saving = 1 - after / before
    print(f"\n=== 3. 修订后的指南 ===\n  retain_kinds={guideline.retain_kinds}\n"
          f"  合计 {before} -> {after} chars（压缩 {saving:.0%}），required facts 全部保留")
    assert saving >= 0.25, saving

    print("\n=== 4. 边界 ===")
    relaxed = Guideline(keep_recent=999)
    assert compress_if_needed(dev[0][1], relaxed, 5000, summarize) is None
    print("  历史低于预算阈值时不压缩（返回 None）")
    print("  revisions 全程留痕，便于审计规则来源")
    assert guideline.revisions
    print("\nself-test OK: 规则由开发失败驱动、可审计；压缩率与事实保留同时成立")
    return 0


def _summarize_live(args: argparse.Namespace) -> int:
    from openai import OpenAI  # imported only for the live command

    client = OpenAI()
    history = dev_trajectories()[0][1]
    prompt = ("Compress this agent history into a compact state summary. Keep tool state, "
              "verified results and unfinished sub-goals. Answer with the summary only.\n\n"
              + "\n".join(item.text for item in history))
    raw = client.chat.completions.create(model=args.model,
                                         messages=[{"role": "user", "content": prompt}],
                                         temperature=0.0).choices[0].message.content
    print(json.dumps({"summary": raw}, ensure_ascii=False, indent=2))
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Failure-guided context compression (ACON)")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo", help="offline deterministic revision loop + self-test")
    live = sub.add_parser("summarize-live", help="produce one summary through a live model")
    live.add_argument("--model", default="deepseek/deepseek-v4-flash")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command in (None, "demo"):
        return _demo()
    if args.command == "summarize-live":
        return _summarize_live(args)
    parser.error(f"unknown command {args.command!r}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
