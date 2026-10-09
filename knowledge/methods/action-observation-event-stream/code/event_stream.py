#!/usr/bin/env python3
"""Structured Action/Observation event stream: capture, filter, replay, and export.

Mechanism source: OpenHands, "An Open Platform for AI Software Developers as
Generalist Agents" (arXiv:2407.16741, ICLR 2025).

This is a harness-agnostic skeleton of the mechanism:
- Event kinds (action / observation / system) and action types are extensible;
- Supports nested events (parent references) and JSONL import/export;
- Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

# Common action classification (from the paper's action space; extensible).
ACTION_TYPES = ("run_ipython", "run_cmd", "browse", "edit", "reply")
# Environment feedback classification.
OBSERVATION_TYPES = ("output", "state", "error")


def _utc_now() -> str:
    """Current UTC timestamp (ISO 8601), sortable across environments."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Event:
    """One event: kind, timestamp, source, target, action type, payload, parent link."""

    kind: str  # action / observation / system
    source: str
    target: str = ""
    action_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    parent: str | None = None  # parent event id of a nested action
    event_id: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.event_id:
            # Timestamp + process-local suffix; use a stronger generator
            # (e.g. uuid) when events are produced concurrently.
            self.event_id = f"{int(datetime.now().timestamp() * 1000)}-{id(self) % 100000}"
        if not self.timestamp:
            self.timestamp = _utc_now()

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "kind": self.kind,
            "source": self.source,
            "target": self.target,
            "action_type": self.action_type,
            "payload": self.payload,
            "parent": self.parent,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        return cls(
            event_id=data.get("event_id", ""),
            timestamp=data.get("timestamp", ""),
            kind=data["kind"],
            source=data["source"],
            target=data.get("target", ""),
            action_type=data.get("action_type", ""),
            payload=data.get("payload", {}),
            parent=data.get("parent"),
        )


class EventStream:
    """Event stream: the single communication medium and trace source.

    Supports append, filter, replay, and JSONL export/import.
    """

    def __init__(self, events: list[Event] | None = None):
        self.events: list[Event] = events or []

    def append(self, event: Event) -> None:
        """Append an event; keep timestamps monotonic (raise out-of-order ones)."""
        if self.events and event.timestamp < self.events[-1].timestamp:
            event.timestamp = self.events[-1].timestamp
        self.events.append(event)

    def filter(
        self,
        kind: str | None = None,
        source: str | None = None,
        action_type: str | None = None,
    ) -> list[Event]:
        """Filter events by kind, source, or action type."""
        result = []
        for event in self.events:
            if kind and event.kind != kind:
                continue
            if source and event.source != source:
                continue
            if action_type and event.action_type != action_type:
                continue
            result.append(event)
        return result

    def replay(self, from_event_id: str | None = None, limit: int = 100) -> Iterator[Event]:
        """Replay step by step from a given event (inclusive); from the start by default."""
        started = from_event_id is None
        count = 0
        for event in self.events:
            if not started:
                if event.event_id == from_event_id:
                    started = True
                else:
                    continue
            if count >= limit:
                return
            yield event
            count += 1

    def to_jsonl(self, path: str | Path) -> None:
        """Export as JSONL: one event per line."""
        with open(path, "w", encoding="utf-8") as handle:
            for event in self.events:
                handle.write(json.dumps(event.as_dict(), ensure_ascii=False) + "\n")

    @classmethod
    def from_jsonl(cls, path: str | Path) -> "EventStream":
        """Import an event stream from JSONL."""
        events = []
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    events.append(Event.from_dict(json.loads(line)))
        return cls(events)

    def stats(self) -> dict[str, Any]:
        """Summary stats: total count plus kind and action-type distributions."""
        kinds: dict[str, int] = {}
        actions: dict[str, int] = {}
        for event in self.events:
            kinds[event.kind] = kinds.get(event.kind, 0) + 1
            if event.action_type:
                actions[event.action_type] = actions.get(event.action_type, 0) + 1
        return {"total": len(self.events), "by_kind": kinds, "by_action": actions}


def demo_command(args: argparse.Namespace) -> None:
    """Minimal demo: build an action-observation trace and exercise filter, replay, export."""
    stream = EventStream()
    stream.append(
        Event(
            kind="action",
            source="agent",
            target="env",
            action_type="run_cmd",
            payload={"command": "pytest tests/"},
        )
    )
    stream.append(
        Event(
            kind="observation",
            source="env",
            target="agent",
            action_type="output",
            payload={"stdout": "1 failed", "exit_code": 1},
        )
    )
    stream.append(
        Event(
            kind="action",
            source="agent",
            target="env",
            action_type="edit",
            payload={"path": "src/app.py", "change": "fix assertion"},
        )
    )
    stream.append(
        Event(
            kind="observation",
            source="env",
            target="agent",
            action_type="state",
            payload={"status": "edited"},
        )
    )

    print("Stats:", stream.stats())
    print("Observation events only:")
    for event in stream.filter(kind="observation"):
        print(" ", event.action_type, event.payload.get("stdout") or event.payload.get("status"))

    first_id = stream.events[1].event_id
    print(f"Replay from {first_id}:")
    for event in stream.replay(from_event_id=first_id):
        print(" ", event.kind, event.action_type)

    stream.to_jsonl("demo_events.jsonl")
    restored = EventStream.from_jsonl("demo_events.jsonl")
    print("Events after JSONL round-trip:", len(restored.events))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture, filter, replay, and export an Action/Observation event stream."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser(
        "demo", help="Build a sample trace and exercise filter, replay, and export"
    )
    demo.set_defaults(handler=demo_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
