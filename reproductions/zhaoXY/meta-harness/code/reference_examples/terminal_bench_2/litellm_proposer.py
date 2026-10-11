"""litellm-backed proposer: replaces the Claude Code CLI session in claude_wrapper.

Same outward contract as ``claude_wrapper.run()``: given a prompt and a set of
skills, drive an agentic tool loop and return a ``SessionResult``.  The one
behavioural difference is *how* the loop is driven -- instead of shelling out to
``claude -p`` and parsing its stream-json events, we call litellm directly and
execute the tool calls ourselves.

Why: the team protocol fixes the *optimisation* model to ``deepseek-v4-flash``,
and the Claude Code CLI cannot be pointed at an arbitrary litellm provider.

Log layout is kept identical to the CLI path by reusing
``claude_wrapper.log_session`` verbatim, so ``logs/<run>/claude_sessions/``
keeps the same shape regardless of which backend proposed.

Environment (all optional unless noted):

    PROPOSER_MODEL        default ``deepseek/deepseek-v4-flash``
    PROPOSER_API_BASE     set to talk to an OpenAI-compatible endpoint instead
    PROPOSER_MAX_TURNS    default 40
    PROPOSER_TEMPERATURE  default 0.7
    DEEPSEEK_API_KEY      required when the model routes through the
                          ``deepseek/`` provider -- supply it via ``.env``

Nothing here reads credentials at import time: tests import this module during
collection and must not need a key to be present.
"""

import json
import os
import re
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from litellm import completion as litellm_completion

import claude_wrapper
from claude_wrapper import SessionResult, ToolCall

# --------------------------------------------------------------------------
# constants
# --------------------------------------------------------------------------

DEFAULT_MODEL = "deepseek/deepseek-v4-flash"
DEFAULT_MAX_TURNS = 40
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT_SECONDS = 2400

# Mirrors baseline_kira._limit_output_length (KIRA truncates at 30KB, the stock
# Terminus2 at 10KB).  Keeping tool output at the same ceiling means the
# proposer sees no more of a file than the agent under test would.
MAX_TOOL_OUTPUT_CHARS = 30_000

# bash is capped well below the proposer's own wall-clock budget so one runaway
# command cannot eat the whole iteration.
MAX_BASH_TIMEOUT_SECONDS = 300
DEFAULT_BASH_TIMEOUT_SECONDS = 120

# Credentials are stripped from the bash tool's environment.  The proposer runs
# LLM-authored commands; an accidental ``env``/``printenv`` must not be able to
# echo the key into a log file.
_SECRET_ENV_KEYS = (
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "RUNLOOP_API_KEY",
    "MODAL_TOKEN_ID",
    "MODAL_TOKEN_SECRET",
    "OPENROUTER_API_KEY",
    "GOOGLE_API_KEY",
    "DAYTONA_API_KEY",
)

# exit codes, matching the conventions claude_wrapper already established
EXIT_OK = 0
EXIT_NO_CANDIDATES = 1
EXIT_TIMEOUT = 124
EXIT_CONFIG = 127

# how many consecutive all-malformed tool-call batches before giving up
MAX_MALFORMED_STREAK = 3

# how many times to prod the model after a text-only turn before accepting that
# it is finished. Models sometimes narrate "I will now write ..." and stop.
MAX_NUDGES = 2

NUDGE_TEXT = (
    "You stopped without calling a tool. If you have not written "
    "pending_eval.json yet, do that now with write_file. If you are genuinely "
    "finished, reply with just: DONE"
)

READONLY_AGENT_FILES = ("baseline_kira.py", "baseline_terminus2.py", "__init__.py")


# --------------------------------------------------------------------------
# tool schemas (OpenAI function-calling format)
# --------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read a text file inside the repo. Returns numbered lines "
                "(format: '<lineno>→<text>'). Use offset/limit for large files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Repo-relative path"},
                    "offset": {
                        "type": "integer",
                        "description": "1-based first line to read (default 1)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max lines to read (default 2000)",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Create or overwrite a file. Only agents/<name>.py and "
                "prompt-templates/<name>.txt may be written; the baselines, "
                "meta_harness.py, scripts/ and tests/ are read-only."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Repo-relative path"},
                    "content": {"type": "string", "description": "Full file content"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List directory entries with sizes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Repo-relative dir (default '.')",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Regex search across files. Returns 'path:lineno:line'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Python regex"},
                    "path": {
                        "type": "string",
                        "description": "File or dir to search (default '.')",
                    },
                    "glob": {
                        "type": "string",
                        "description": "Optional filename filter, e.g. '*.json'",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": (
                "Run a shell command with cwd pinned to the repo root. "
                "Use it to sanity-check an import: "
                "uv run python -c \"from agents.<name> import *; print('OK')\""
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {
                        "type": "integer",
                        "description": f"Seconds (max {MAX_BASH_TIMEOUT_SECONDS})",
                    },
                },
                "required": ["command"],
            },
        },
    },
]


# --------------------------------------------------------------------------
# path safety
# --------------------------------------------------------------------------


class ToolError(Exception):
    """Raised for a rejected or failed tool call; surfaced to the model."""


def _truncate(text, limit=MAX_TOOL_OUTPUT_CHARS):
    if len(text) <= limit:
        return text
    dropped = len(text) - limit
    return f"{text[:limit]}\n\n[... truncated {dropped} more characters ...]"


def _resolve(base, path):
    """Resolve ``path`` against ``base``, refusing anything that escapes it."""
    if path is None or str(path).strip() == "":
        path = "."
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = Path(base) / candidate
    resolved = candidate.resolve()
    base_resolved = Path(base).resolve()
    if resolved != base_resolved and base_resolved not in resolved.parents:
        raise ToolError(f"path escapes the workspace: {path}")
    return resolved


def _rel(base, resolved):
    try:
        return str(Path(resolved).relative_to(Path(base).resolve()))
    except ValueError:
        return str(resolved)


def _check_writable(evo_dir, resolved, pending_eval_path):
    """Enforce the write whitelist agreed for this task.

    Writable: ``agents/<name>.py``, ``prompt-templates/<name>.txt``, and the
    run's own ``pending_eval.json``.  The baselines are the protocol's H0 and
    must never be touched.
    """
    rel = _rel(evo_dir, resolved)

    if pending_eval_path is not None:
        try:
            if resolved == Path(pending_eval_path).resolve():
                return
        except OSError:
            pass

    parts = Path(rel).parts
    if len(parts) == 2 and parts[0] == "agents" and parts[1].endswith(".py"):
        if parts[1] in READONLY_AGENT_FILES:
            raise ToolError(
                f"refusing to write {rel}: baselines and __init__.py are read-only"
            )
        return
    if len(parts) == 2 and parts[0] == "prompt-templates":
        if parts[1].endswith(".txt"):
            return
        raise ToolError(f"refusing to write {rel}: only .txt templates are allowed")

    raise ToolError(
        f"refusing to write {rel}: writable paths are agents/<name>.py, "
        "prompt-templates/<name>.txt and the run's pending_eval.json"
    )


# --------------------------------------------------------------------------
# tool implementations
# --------------------------------------------------------------------------


@dataclass
class ToolContext:
    """Workspace handles plus the read/write tallies that go into the log."""

    evo_dir: Path
    pending_eval_path: Path | None = None
    files_read: dict = field(default_factory=dict)
    files_written: dict = field(default_factory=dict)

    def note_read(self, resolved, n_lines):
        rel = _rel(self.evo_dir, resolved)
        entry = self.files_read.setdefault(rel, {"reads": 0, "lines": 0})
        entry["reads"] += 1
        entry["lines"] += n_lines

    def note_write(self, resolved, content):
        rel = _rel(self.evo_dir, resolved)
        self.files_written[rel] = {
            "lines_written": content.count("\n") + (1 if content else 0)
        }


def _fmt_numbered(lines, start):
    """Match Claude's Read layout: right-aligned 6-wide line number, U+2192.

    claude_wrapper._count_read_lines and _clean_read_output both key off
    ``\\s*\\d+→``, so producing this shape keeps log stats working unchanged.
    """
    return "\n".join(f"{start + i:6d}→{line}" for i, line in enumerate(lines))


def _tool_read_file(args, ctx):
    resolved = _resolve(ctx.evo_dir, args.get("path"))
    if not resolved.is_file():
        raise ToolError(f"not a file: {_rel(ctx.evo_dir, resolved)}")
    offset = max(1, int(args.get("offset") or 1))
    limit = max(1, int(args.get("limit") or 2000))
    try:
        text = resolved.read_text(errors="replace")
    except OSError as exc:
        raise ToolError(f"cannot read {_rel(ctx.evo_dir, resolved)}: {exc}") from exc

    all_lines = text.splitlines()
    window = all_lines[offset - 1 : offset - 1 + limit]
    ctx.note_read(resolved, len(window))
    if not window:
        return f"(no lines in range; file has {len(all_lines)} lines)"
    body = _fmt_numbered(window, offset)
    tail = len(all_lines) - (offset - 1 + limit)
    if tail > 0:
        body += f"\n[... {tail} more lines ...]"
    return _truncate(body)


def _tool_write_file(args, ctx):
    resolved = _resolve(ctx.evo_dir, args.get("path"))
    _check_writable(ctx.evo_dir, resolved, ctx.pending_eval_path)
    content = args.get("content")
    if content is None:
        raise ToolError("write_file requires 'content'")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content)
    ctx.note_write(resolved, content)
    rel = _rel(ctx.evo_dir, resolved)
    return f"wrote {rel} ({len(content)} bytes, {content.count(chr(10)) + 1} lines)"


def _tool_list_dir(args, ctx):
    resolved = _resolve(ctx.evo_dir, args.get("path") or ".")
    if not resolved.is_dir():
        raise ToolError(f"not a directory: {_rel(ctx.evo_dir, resolved)}")
    entries = []
    for child in sorted(resolved.iterdir(), key=lambda p: (p.is_file(), p.name)):
        if child.name == "__pycache__":
            continue
        if child.is_dir():
            entries.append(f"  {child.name}/")
        else:
            try:
                size = child.stat().st_size
            except OSError:
                size = -1
            entries.append(f"  {child.name}  ({size} bytes)")
    if not entries:
        return "(empty directory)"
    return _truncate("\n".join(entries))


def _tool_grep(args, ctx):
    pattern = args.get("pattern")
    if not pattern:
        raise ToolError("grep requires 'pattern'")
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        raise ToolError(f"bad regex: {exc}") from exc

    target = _resolve(ctx.evo_dir, args.get("path") or ".")
    glob = args.get("glob")

    if target.is_file():
        files = [target]
    else:
        files = [
            p
            for p in target.rglob(glob or "*")
            if p.is_file()
            and "__pycache__" not in p.parts
            and ".venv" not in p.parts
            and ".git" not in p.parts
        ]

    hits = []
    for path in sorted(files)[:400]:
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(errors="replace")
        except (OSError, ValueError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append(f"{_rel(ctx.evo_dir, path)}:{lineno}:{line[:300]}")
                if len(hits) >= 200:
                    break
        if len(hits) >= 200:
            break

    if not hits:
        return "(no matches)"
    return _truncate("\n".join(hits))


def _tool_run_bash(args, ctx):
    command = args.get("command")
    if not command:
        raise ToolError("run_bash requires 'command'")
    timeout = int(args.get("timeout") or DEFAULT_BASH_TIMEOUT_SECONDS)
    timeout = max(1, min(timeout, MAX_BASH_TIMEOUT_SECONDS))

    env = os.environ.copy()
    for key in _SECRET_ENV_KEYS:
        env.pop(key, None)
    env["PYTHONPATH"] = f"{ctx.evo_dir}{os.pathsep}{env.get('PYTHONPATH', '')}"

    try:
        proc = subprocess.run(
            ["bash", "-lc", command],
            cwd=str(ctx.evo_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise ToolError(f"command timed out after {timeout}s") from None
    except OSError as exc:
        raise ToolError(f"cannot run command: {exc}") from exc

    parts = []
    if proc.stdout:
        parts.append(proc.stdout)
    if proc.stderr:
        parts.append(f"[stderr]\n{proc.stderr}")
    parts.append(f"[exit code: {proc.returncode}]")
    return _truncate("\n".join(parts))


TOOL_IMPL = {
    "read_file": _tool_read_file,
    "write_file": _tool_write_file,
    "list_dir": _tool_list_dir,
    "grep": _tool_grep,
    "run_bash": _tool_run_bash,
}


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------


def _resolve_model():
    """Return ``(model, api_base)``.

    With no PROPOSER_API_BASE we use litellm's native provider routing, so
    ``deepseek/deepseek-v4-flash`` goes to api.deepseek.com.  Setting
    PROPOSER_API_BASE switches to OpenAI-compatible routing against that host,
    which covers a team proxy or self-hosted gateway without a code change.
    """
    model = os.environ.get("PROPOSER_MODEL") or DEFAULT_MODEL
    base = os.environ.get("PROPOSER_API_BASE") or None
    if base:
        bare = model.split("/", 1)[1] if "/" in model else model
        return f"openai/{bare}", base
    return model, None


def _missing_key_error(model):
    """Return a message if the routed provider's key is absent, else None."""
    if model.startswith("deepseek/"):
        if not os.environ.get("DEEPSEEK_API_KEY"):
            return (
                "DEEPSEEK_API_KEY is not set. Put it in "
                "reproductions/zhaoXY/meta-harness/code/reference_examples/"
                "terminal_bench_2/.env (gitignored) and re-run."
            )
    elif model.startswith("openai/"):
        if not os.environ.get("OPENAI_API_KEY"):
            return "OPENAI_API_KEY is not set (needed for PROPOSER_API_BASE routing)."
    return None


# --------------------------------------------------------------------------
# prompt assembly
# --------------------------------------------------------------------------


COLD_START_NOTE = """\
## Cold-start note

If `logs/` and `jobs/` contain no result files yet, there is no trajectory
history to analyse. In that case skip the trajectory-reading step and instead
read `agents/baseline_kira.py` closely, then propose ONE general-purpose
mechanism based on its overridable methods. Do not fabricate trajectory
findings, and do not block on missing data.
"""

TOOL_NOTE = """\
## How to act

You work by calling tools, one step at a time. Read a file before editing it.
Write the candidate to `agents/<name>.py` (copy the baseline's structure, then
apply your change). Validate the import with `run_bash` before you finish.
Finally, write `pending_eval.json` to the exact path given in the task prompt --
that file is what the outer loop reads, and without it this iteration produced
nothing.
"""


def build_system_prompt(skills, cold_start_note=True):
    parts = []
    if skills:
        rendered = "\n\n".join(f"## Skill: {s['name']}\n{s['content']}" for s in skills)
        parts.append(f"Follow these skill instructions:\n\n{rendered}")
    if cold_start_note:
        parts.append(COLD_START_NOTE)
    parts.append(TOOL_NOTE)
    return "\n\n".join(parts)


# --------------------------------------------------------------------------
# litellm plumbing
# --------------------------------------------------------------------------


def _message_to_dict(message):
    if hasattr(message, "model_dump"):
        return message.model_dump()
    if isinstance(message, dict):
        return message
    return {"content": str(message)}


def _extract_tool_calls(message):
    """Return tool calls on ``message`` as dicts of {id, name, arguments}.

    Tolerates both shapes litellm can hand back: objects carrying
    ``.function.name`` / ``.function.arguments``, or plain dicts.
    """
    raw = getattr(message, "tool_calls", None)
    if raw is None and isinstance(message, dict):
        raw = message.get("tool_calls")
    if not raw:
        return []

    calls = []
    for item in raw:
        generated_id = f"call_{uuid.uuid4().hex[:12]}"
        if isinstance(item, dict):
            fn = item.get("function") or {}
            calls.append(
                {
                    "id": item.get("id") or generated_id,
                    "name": fn.get("name") or "",
                    "arguments": fn.get("arguments") or "{}",
                }
            )
        else:
            fn = getattr(item, "function", None)
            calls.append(
                {
                    "id": getattr(item, "id", None) or generated_id,
                    "name": getattr(fn, "name", "") or "",
                    "arguments": getattr(fn, "arguments", None) or "{}",
                }
            )
    return calls


def _parse_arguments(raw):
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ToolError(f"arguments are not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ToolError("arguments must be a JSON object")
    return parsed


def _log_input(args):
    """Shape the logged tool input so claude_wrapper.log_session reads well.

    log_session summarises tool calls by looking for a ``file_path`` key; our
    tools call it ``path``. Mirroring it keeps tool_summary in meta.json
    informative instead of falling through to a raw blob.
    """
    if not isinstance(args, dict):
        return {"raw": str(args)[:200]}
    shaped = dict(args)
    if "path" in shaped and "file_path" not in shaped:
        shaped["file_path"] = shaped["path"]
    return shaped


def _completion_cost(response):
    """Cost lookup isolated so tests can stub it without importing litellm's map."""
    try:
        from litellm import completion_cost

        return float(completion_cost(completion_response=response) or 0.0)
    except Exception:  # noqa: BLE001 - unknown model => no cost info
        return 0.0


def _salvage_pending_eval(text, pending_eval_path):
    """Recover a pending_eval payload the model pasted as text.

    claude_wrapper._extract_json_blocks already understands the
    "```json ... ```" convention. Belt and braces: some models describe the file
    instead of writing it, and discarding a well-formed payload would waste the
    whole iteration.
    """
    if not text or pending_eval_path is None:
        return False
    try:
        blocks = claude_wrapper._extract_json_blocks(text)
    except Exception:  # noqa: BLE001
        return False
    for _filename, payload in blocks:
        if isinstance(payload, dict) and payload.get("candidates"):
            pending_eval_path.parent.mkdir(parents=True, exist_ok=True)
            pending_eval_path.write_text(json.dumps(payload, indent=2))
            return True
    return False


# --------------------------------------------------------------------------
# the loop
# --------------------------------------------------------------------------


def run(
    prompt,
    model=None,
    cwd=None,
    log_dir=None,
    name=None,
    skills=None,
    skill_dir=None,
    timeout_seconds=None,
    max_turns=None,
    progress=True,
    pending_eval_path=None,
):
    """Drive one proposer session. Returns a ``SessionResult``.

    Mirrors ``claude_wrapper.run`` closely enough that ``meta_harness.py`` can
    swap backends without touching its own control flow.
    """
    started = time.time()
    evo_dir = Path(cwd).resolve() if cwd else Path.cwd().resolve()

    if model is None:
        model, api_base = _resolve_model()
    else:
        api_base = os.environ.get("PROPOSER_API_BASE") or None

    if max_turns is None:
        max_turns = int(os.environ.get("PROPOSER_MAX_TURNS") or DEFAULT_MAX_TURNS)
    temperature = float(os.environ.get("PROPOSER_TEMPERATURE") or DEFAULT_TEMPERATURE)
    if timeout_seconds is None:
        timeout_seconds = DEFAULT_TIMEOUT_SECONDS

    resolved_skills = claude_wrapper.load_skills(skills, skill_dir) if skills else None

    ctx = ToolContext(
        evo_dir=evo_dir,
        pending_eval_path=(
            Path(pending_eval_path).resolve() if pending_eval_path else None
        ),
    )

    result = SessionResult(
        prompt=prompt,
        text="",
        tool_calls=[],
        files_read=ctx.files_read,
        files_written=ctx.files_written,
        token_usage={"input_tokens": 0, "output_tokens": 0},
        duration_seconds=0.0,
        model=model,
        session_id=f"litellm-{uuid.uuid4().hex[:12]}",
        exit_code=EXIT_OK,
        cost_usd=0.0,
        raw_events=[],
        command=["litellm", model],
        cwd=str(evo_dir),
        stderr="",
        skill=resolved_skills,
        name=name,
    )

    def _finish():
        result.duration_seconds = time.time() - started
        if log_dir:
            claude_wrapper.log_session(result, log_dir)
        return result

    missing = _missing_key_error(model)
    if missing:
        result.exit_code = EXIT_CONFIG
        result.stderr = missing
        return _finish()

    messages = [
        {"role": "system", "content": build_system_prompt(resolved_skills)},
        {"role": "user", "content": prompt},
    ]

    def _produced_candidates():
        return ctx.pending_eval_path is not None and ctx.pending_eval_path.exists()

    deadline = started + timeout_seconds if timeout_seconds else None
    malformed_streak = 0
    nudges = 0

    for turn in range(1, max_turns + 1):
        if _produced_candidates():
            break
        if deadline and time.time() > deadline:
            result.exit_code = EXIT_TIMEOUT
            result.stderr = f"proposer timed out after {timeout_seconds}s"
            break

        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "tools": TOOL_SCHEMAS,
                "temperature": temperature,
                "timeout": max(30, int(timeout_seconds)),
                "num_retries": int(os.environ.get("PROPOSER_NUM_RETRIES") or 3),
                "drop_params": True,
            }
            if api_base:
                kwargs["api_base"] = api_base
            response = litellm_completion(**kwargs)
        except Exception as exc:  # noqa: BLE001 - surfaced into the result
            result.exit_code = EXIT_NO_CANDIDATES
            result.stderr = f"{type(exc).__name__}: {exc}"
            break

        usage = getattr(response, "usage", None)
        if usage is not None:
            result.token_usage["input_tokens"] += int(
                getattr(usage, "prompt_tokens", 0) or 0
            )
            result.token_usage["output_tokens"] += int(
                getattr(usage, "completion_tokens", 0) or 0
            )
        result.cost_usd += _completion_cost(response)

        message = response.choices[0].message
        result.raw_events.append(
            {"type": "assistant", "turn": turn, "message": _message_to_dict(message)}
        )

        text = getattr(message, "content", None) or ""
        if text:
            result.text = text

        calls = _extract_tool_calls(message)
        if not calls:
            # A text-only turn. The model may think it is finished, or it may
            # have just narrated. Salvage a pasted payload first, then prod it
            # a bounded number of times before accepting the end of the session.
            if _salvage_pending_eval(text, ctx.pending_eval_path):
                break
            if nudges < MAX_NUDGES and not text.strip().endswith("DONE"):
                nudges += 1
                if progress:
                    print(
                        f"    [turn {turn}] no tool call; nudging ({nudges}/{MAX_NUDGES})",
                        flush=True,
                    )
                messages.append({"role": "assistant", "content": text})
                messages.append({"role": "user", "content": NUDGE_TEXT})
                continue
            break

        messages.append(
            {
                "role": "assistant",
                "content": text,
                "tool_calls": [
                    {
                        "id": call["id"],
                        "type": "function",
                        "function": {
                            "name": call["name"],
                            "arguments": call["arguments"]
                            if isinstance(call["arguments"], str)
                            else json.dumps(call["arguments"]),
                        },
                    }
                    for call in calls
                ],
            }
        )

        malformed_in_batch = 0
        for call in calls:
            tool_name = call["name"]
            impl = TOOL_IMPL.get(tool_name)
            parsed_args = None

            if impl is None:
                output = f"ERROR: unknown tool '{tool_name}'"
            else:
                try:
                    parsed_args = _parse_arguments(call["arguments"])
                except ToolError as exc:
                    output = f"ERROR: {exc}"
                    malformed_in_batch += 1
                else:
                    try:
                        output = impl(parsed_args, ctx)
                    except ToolError as exc:
                        output = f"ERROR: {exc}"
                    except Exception as exc:  # noqa: BLE001
                        output = f"ERROR: {type(exc).__name__}: {exc}"

            is_error = output.startswith("ERROR:")
            logged_input = (
                _log_input(parsed_args)
                if parsed_args is not None
                else {"raw": str(call["arguments"])[:200]}
            )
            result.tool_calls.append(
                ToolCall(
                    name=tool_name,
                    tool_id=call["id"],
                    input=logged_input,
                    output=output,
                    is_error=is_error,
                )
            )
            if progress:
                head = output.splitlines()[0][:110] if output else ""
                flag = " ERR" if is_error else ""
                print(f"    [turn {turn}] {tool_name}{flag}: {head}", flush=True)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "name": tool_name,
                    "content": output,
                }
            )

        # A batch where every call had unparseable arguments means the model is
        # emitting malformed tool calls; retry a couple of times, then give up.
        malformed_streak = (
            malformed_streak + 1
            if malformed_in_batch == len(calls)
            else 0
        )
        if malformed_streak >= MAX_MALFORMED_STREAK:
            result.stderr = (
                f"aborting after {malformed_streak} malformed tool-call batches"
            )
            break
    else:
        result.stderr = f"reached max_turns={max_turns} without pending_eval.json"

    # Producing the artefact is what defines success. run_evolve deletes
    # pending_eval.json before each proposal, so a file on disk can only have
    # been written by this session -- a late write outranks a timeout note or
    # an exhausted turn budget.
    if not _produced_candidates():
        _salvage_pending_eval(result.text, ctx.pending_eval_path)

    if _produced_candidates():
        result.exit_code = EXIT_OK
    elif result.exit_code == EXIT_OK:
        result.exit_code = EXIT_NO_CANDIDATES
        if not result.stderr:
            result.stderr = "session ended without writing pending_eval.json"

    return _finish()
