"""A litellm-backed AgentTransport for AutoSaddler V2, so the optimizer can be DeepSeek.

Why this exists: AutoSaddler V2 ships providers for `claude` (Anthropic wire), `codex`
(CLI) and `copilot` (BYOK), none of which can talk to an arbitrary OpenAI-compatible
endpoint with an explicit key. The team protocol fixes the optimizer model to
`deepseek-flash`, so the plugin supplies its own transport. It implements the same
in-process agentic tool loop used by this repo's Meta-Harness proposer
(`meta-harness/code/.../litellm_proposer.py`), narrowed to the V2 contract:

* the workspace is the only writable surface (plus the session's own output file),
* the final structured output must be a JSON object matching the session schema,
* every tool call and token is reported back through ``TransportOutcome``.

The transport never raises for model-side failures: it returns an outcome with an empty
structured output and the base provider turns that into a failed ``SessionResult``.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from autosaddler.v2.core.domain import JsonValue
from autosaddler.v2.prompting.models import ToolCall, Usage
from autosaddler.v2.providers.base import TransportOutcome
from autosaddler.v2.providers.workspace_renderer import RenderedSession

MAX_TOOL_OUTPUT_CHARS = 20_000
BASH_TIMEOUT_S = 300
READ_MAX_LINES = 400


@dataclass(frozen=True, slots=True)
class LitellmTransportSettings:
    model: str = "deepseek/deepseek-v4-flash"
    api_key_env: str = "DEEPSEEK_API_KEY"
    temperature: float = 0.7
    max_tokens: int = 8192
    max_turns: int = 40
    num_retries: int = 3

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("Transport model must be non-empty")
        if self.max_turns < 1:
            raise ValueError("Transport max_turns must be positive")


_TOOL_SCHEMA: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start_line": {"type": "integer"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a UTF-8 text file inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List the entries of a directory inside the workspace.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search for a regular expression in workspace text files.",
            "parameters": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}},
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "Run a shell command with the workspace as the working directory.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": (
                "Finish the session. 'output' must be the JSON object required by "
                ".autosaddler/session_output_schema.json."
            ),
            "parameters": {
                "type": "object",
                "properties": {"output": {"type": "object"}},
                "required": ["output"],
            },
        },
    },
]


@dataclass
class _Ledger:
    usage: list[Usage] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    cost_usd: float = 0.0

    def record(self, response: Any) -> None:
        usage = getattr(response, "usage", None)
        cost = 0.0
        try:
            import litellm

            cost = float(litellm.completion_cost(completion_response=response) or 0.0)
        except Exception:  # pragma: no cover - cost reporting is best-effort
            cost = 0.0
        self.cost_usd += cost
        self.usage.append(
            Usage(
                input_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
                output_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
                model=getattr(response, "model", None),
                role="optimizer",
                provider_cost=cost or None,
                provider_cost_unit="USD" if cost else None,
            )
        )


class LitellmTransport:
    """Agentic tool loop over a workspace, speaking the V2 AgentTransport contract."""

    def __init__(self, settings: LitellmTransportSettings | None = None) -> None:
        self.settings = settings or LitellmTransportSettings()

    async def run(self, session: RenderedSession, timeout_seconds: float) -> TransportOutcome:
        return await asyncio.wait_for(
            asyncio.to_thread(self._run_sync, session),
            timeout=timeout_seconds,
        )

    # -- internals ------------------------------------------------------------

    def _run_sync(self, session: RenderedSession) -> TransportOutcome:
        if not os.environ.get(self.settings.api_key_env):
            raise RuntimeError(
                f"{self.settings.api_key_env} is not set; the litellm transport cannot run"
            )
        import litellm

        workspace = session.workspace.resolve()
        instruction = _read_instruction(session)
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": instruction},
            {
                "role": "user",
                "content": (
                    "Perform the session using the workspace. When you are done, call the "
                    "`finish` tool with the JSON object required by the session schema."
                ),
            },
        ]
        ledger = _Ledger()
        last_text = ""
        for _turn in range(self.settings.max_turns):
            response = litellm.completion(
                model=self.settings.model,
                messages=messages,
                tools=_TOOL_SCHEMA,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                num_retries=self.settings.num_retries,
            )
            ledger.record(response)
            message = response.choices[0].message
            calls = getattr(message, "tool_calls", None) or []
            assistant_entry: dict[str, Any] = {
                "role": "assistant",
                "content": message.content or "",
            }
            if calls:
                assistant_entry["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in calls
                ]
            messages.append(assistant_entry)
            if message.content:
                last_text = message.content

            if not calls:
                # No tool call: accept a JSON object embedded in the message as the output.
                output = _extract_json(last_text)
                if output is not None:
                    _write_output(session, output)
                    return self._outcome(ledger, last_text, output)
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "You did not call `finish`. Call the `finish` tool with the JSON object "
                            "required by the session schema."
                        ),
                    }
                )
                continue

            for call in calls:
                name = call.function.name
                try:
                    arguments = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    arguments = {}
                ledger.tool_calls.append(ToolCall(tool=name, arguments=_freeze(arguments)))
                if name == "finish":
                    output = arguments.get("output")
                    if isinstance(output, Mapping):
                        _write_output(session, output)
                        return self._outcome(ledger, last_text, dict(output))
                    result = "finish requires an 'output' object"
                else:
                    result = self._dispatch(workspace, name, arguments)
                messages.append(
                    {"role": "tool", "tool_call_id": call.id, "content": result[:MAX_TOOL_OUTPUT_CHARS]}
                )

        return self._outcome(ledger, last_text, None)

    def _dispatch(self, workspace: Path, name: str, arguments: Mapping[str, Any]) -> str:
        try:
            if name == "read_file":
                return _read_file(workspace, str(arguments.get("path", "")), arguments.get("start_line"))
            if name == "write_file":
                return _write_file(workspace, str(arguments.get("path", "")), str(arguments.get("content", "")))
            if name == "list_dir":
                return _list_dir(workspace, arguments.get("path"))
            if name == "grep":
                return _grep(
                    workspace,
                    str(arguments.get("pattern", "")),
                    arguments.get("path"),
                )
            if name == "run_bash":
                return _run_bash(workspace, str(arguments.get("command", "")))
            return f"unknown tool: {name}"
        except Exception as exc:  # tool errors are data, not crashes
            return f"{type(exc).__name__}: {exc}"

    def _outcome(
        self,
        ledger: _Ledger,
        raw_response: str,
        output: Mapping[str, JsonValue] | None,
    ) -> TransportOutcome:
        return TransportOutcome(
            raw_response=raw_response,
            structured_output=dict(output) if output is not None else None,
            tool_calls=tuple(ledger.tool_calls),
            usage=tuple(ledger.usage),
        )


# --- workspace-confined tools ------------------------------------------------


def _resolve(workspace: Path, raw_path: str | None) -> Path:
    candidate = Path(raw_path or ".").expanduser()
    resolved = (workspace / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    if resolved != workspace and not resolved.is_relative_to(workspace):
        raise ValueError(f"path escapes the workspace: {raw_path}")
    return resolved


def _read_file(workspace: Path, raw_path: str, start_line: Any = None) -> str:
    path = _resolve(workspace, raw_path)
    text = path.read_text(encoding="utf-8", errors="replace")
    start = int(start_line) if isinstance(start_line, int) and start_line > 0 else 1
    lines = text.splitlines()[start - 1 : start - 1 + READ_MAX_LINES]
    return "\n".join(f"{start + index:5d}\t{line}" for index, line in enumerate(lines))


def _write_file(workspace: Path, raw_path: str, content: str) -> str:
    path = _resolve(workspace, raw_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote {len(content)} bytes to {raw_path}"


def _list_dir(workspace: Path, raw_path: Any) -> str:
    path = _resolve(workspace, raw_path if isinstance(raw_path, str) else None)
    entries = sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name))
    return "\n".join(f"{'d' if entry.is_dir() else 'f'} {entry.name}" for entry in entries)


def _grep(workspace: Path, pattern: str, raw_path: Any) -> str:
    import re

    root = _resolve(workspace, raw_path if isinstance(raw_path, str) else None)
    regex = re.compile(pattern)
    hits: list[str] = []
    files = [root] if root.is_file() else sorted(root.rglob("*"))
    for item in files:
        if not item.is_file() or item.stat().st_size > 2_000_000:
            continue
        try:
            for number, line in enumerate(item.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if regex.search(line):
                    hits.append(f"{item.relative_to(workspace)}:{number}: {line[:200]}")
                    if len(hits) >= 200:
                        return "\n".join(hits)
        except OSError:
            continue
    return "\n".join(hits) if hits else "no matches"


def _run_bash(workspace: Path, command: str) -> str:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.endswith("_API_KEY") and "TOKEN" not in key.upper()
    }
    proc = subprocess.run(
        ["bash", "-lc", command],
        cwd=str(workspace),
        env=env,
        capture_output=True,
        text=True,
        timeout=BASH_TIMEOUT_S,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return f"exit={proc.returncode}\n{output}"[:MAX_TOOL_OUTPUT_CHARS]


# --- helpers -----------------------------------------------------------------


def _read_instruction(session: RenderedSession) -> str:
    parts = [session.system_context.strip(), session.task_prompt.strip()]
    if session.instruction_path.exists():
        parts.append(session.instruction_path.read_text(encoding="utf-8").strip())
    if session.output_schema_path.exists():
        parts.append(
            "Session output schema (the `finish` tool must satisfy it):\n"
            + session.output_schema_path.read_text(encoding="utf-8").strip()
        )
    return "\n\n".join(part for part in parts if part)


def _extract_json(text: str) -> Mapping[str, JsonValue] | None:
    text = (text or "").strip()
    if not text:
        return None
    candidates = [text]
    if "```" in text:
        for block in text.split("```"):
            block = block.strip()
            if block.startswith("json"):
                block = block[4:].strip()
            candidates.append(block)
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def _write_output(session: RenderedSession, output: Mapping[str, JsonValue]) -> None:
    path = session.output_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _freeze(value: Any) -> Mapping[str, JsonValue]:
    return json.loads(json.dumps(value, default=str))
