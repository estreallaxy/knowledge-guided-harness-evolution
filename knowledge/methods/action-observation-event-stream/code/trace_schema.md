# Event field contract and recording granularity

This page is a draft event contract for integrating a concrete harness; use it
together with `event_stream.py`.

## Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `event_id` | yes | Globally unique event id; use a stronger guarantee (e.g. uuid + sequence) under concurrency. |
| `timestamp` | yes | UTC ISO 8601; monotonic within a stream. |
| `kind` | yes | `action` / `observation` / `system`. |
| `source` | yes | Originator: `agent` / `env` / harness module name. |
| `target` | no | Recipient; leave empty for broadcasts. |
| `action_type` | no | Action or feedback classification; see the table below. |
| `payload` | yes | Payload; keep structured fields only, put large content behind references. |
| `parent` | no | Parent event id of a nested action, for rebuilding the action tree. |

## Action types (extensible)

| Type | Meaning | Payload example |
| --- | --- | --- |
| `run_ipython` | Execute a code cell | `{"code": "..."}` |
| `run_cmd` | Execute a shell command | `{"command": "..."}` |
| `browse` | Browse or read a page or file | `{"url": "...", "path": "..."}` |
| `edit` | Modify a file | `{"path": "...", "change": "..."}` |
| `reply` | Plain-text reply | `{"content": "..."}` |

Feedback classification: `output` (stdout/stderr), `state` (environment state), `error` (exception).

## Recording granularity

- **Full**: all events with complete payloads. Enables replay and strict auditing; highest storage and token cost.
- **Structured** (recommended default): all events with truncated payloads (e.g. first N bytes plus size). Keeps type and order information, drops full text of large fields.
- **Summary**: only the action/observation type sequence and key failure events. Cheapest, but cannot be replayed step by step.

The granularity is set by the harness observation budget and should be negotiated with downstream diagnostic tools: a diagnoser can request an expansion of a summarized span on demand (replay by event-id range), which is itself a modifiable part of the harness.
