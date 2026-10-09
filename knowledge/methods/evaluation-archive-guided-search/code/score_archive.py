#!/usr/bin/env python3
"""Score archive for candidate modifications and next-round guidance prompts.

Mechanism source: ADAS, "Automated Design of Agentic Systems"
(arXiv:2408.08435, ICLR 2025).

This is a harness-agnostic skeleton of the mechanism:
- Every candidate is archived, success or failure (failures keep their error log
  and repair suggestions);
- Before the next generation round, top-k successes and recent failures are
  retrieved separately;
- Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROMPT_TEMPLATE = Path(__file__).resolve().parent / "archive_prompt.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CandidateRecord:
    """One candidate record: the (design, score, error_log, reflection) tuple plus metadata."""

    design: str  # description or code of the candidate modification
    score: float  # task evaluation score (higher is better)
    error_log: str = ""  # error details on failure; empty on success
    reflection: str = ""  # self-reflection or repair suggestion
    created: str = ""
    meta: dict[str, Any] = field(default_factory=dict)  # task, model, budget, etc.

    def __post_init__(self) -> None:
        if not self.created:
            self.created = _utc_now()

    def as_dict(self) -> dict[str, Any]:
        return {
            "design": self.design,
            "score": self.score,
            "error_log": self.error_log,
            "reflection": self.reflection,
            "created": self.created,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateRecord":
        return cls(
            design=data["design"],
            score=data["score"],
            error_log=data.get("error_log", ""),
            reflection=data.get("reflection", ""),
            created=data.get("created", ""),
            meta=data.get("meta", {}),
        )


class Archive:
    """Score archive: successes and failures are retrieved separately for the next round."""

    def __init__(self, records: list[CandidateRecord] | None = None):
        self.records: list[CandidateRecord] = records or []

    def add(self, record: CandidateRecord) -> None:
        self.records.append(record)

    def top_k(self, k: int = 3) -> list[CandidateRecord]:
        """Top-k candidates by score."""
        ordered = sorted(self.records, key=lambda record: record.score, reverse=True)
        return ordered[:k]

    def failures(self, k: int = 3) -> list[CandidateRecord]:
        """Most recent failed candidates (with error log and reflection), newest first."""
        failed = [record for record in self.records if record.error_log]
        failed.sort(key=lambda record: record.created, reverse=True)
        return failed[:k]

    def to_json(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(
                [record.as_dict() for record in self.records],
                handle,
                ensure_ascii=False,
                indent=2,
            )

    @classmethod
    def from_json(cls, path: str | Path) -> "Archive":
        with open(path, encoding="utf-8") as handle:
            return cls([CandidateRecord.from_dict(item) for item in json.load(handle)])


def _render_records(records: list[CandidateRecord], indent: str = "  ") -> str:
    """Render candidate records as a text block for the prompt template."""
    blocks = []
    for record in records:
        block = (
            f"{indent}Design: {record.design}\n"
            f"{indent}Score: {record.score}\n"
        )
        if record.error_log:
            block += f"{indent}Error log: {record.error_log}\n"
        if record.reflection:
            block += f"{indent}Reflection/repair suggestion: {record.reflection}\n"
        blocks.append(block)
    return "\n".join(blocks)


_FENCE = "```"


def _extract_template(text: str) -> str:
    """Extract the first fenced code block as the prompt body; fall back to the whole text."""
    start = text.find(_FENCE)
    if start == -1:
        return text
    end = text.find(_FENCE, start + len(_FENCE))
    if end == -1:
        return text
    return text[start + len(_FENCE) : end].strip("\n")


def build_guidance_prompt(
    archive: Archive,
    task: str,
    k_success: int = 3,
    k_failure: int = 3,
) -> str:
    """Inject archive examples into the template and build the next-round guidance prompt."""
    template = _extract_template(PROMPT_TEMPLATE.read_text(encoding="utf-8"))
    return template.format(
        task=task,
        successes=_render_records(archive.top_k(k_success)),
        failures=_render_records(archive.failures(k_failure)),
    )


def demo_command(args: argparse.Namespace) -> None:
    """Minimal demo: build a sample archive and generate a guidance prompt."""
    archive = Archive()
    archive.add(
        CandidateRecord(
            design="Add a verification script after the diagnosis step",
            score=0.8,
            reflection="Keep it, and consider adding a budget check",
            meta={"task": "dev-01"},
        )
    )
    archive.add(
        CandidateRecord(
            design="Translate the tool descriptions into Chinese",
            score=0.4,
            error_log="Tool-call parsing failed 3 times",
            reflection="The wording change broke interface parsing; fix the parser first",
            meta={"task": "dev-01"},
        )
    )
    archive.add(
        CandidateRecord(
            design="Raise the per-round retry limit",
            score=0.6,
            meta={"task": "dev-02"},
        )
    )

    print("Top-k successes:", [record.score for record in archive.top_k(2)])
    print("Recent failures:", [record.error_log[:20] for record in archive.failures(2)])
    print("--- Guidance prompt ---")
    print(build_guidance_prompt(archive, task="dev-03: reduce tool-call parsing failures"))

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "demo_archive.json"
        archive.to_json(path)
        restored = Archive.from_json(path)
    print("Records after JSON round-trip:", len(restored.records))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score archive for candidate modifications and next-round guidance prompts."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser(
        "demo", help="Build a sample archive and generate a guidance prompt"
    )
    demo.set_defaults(handler=demo_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
