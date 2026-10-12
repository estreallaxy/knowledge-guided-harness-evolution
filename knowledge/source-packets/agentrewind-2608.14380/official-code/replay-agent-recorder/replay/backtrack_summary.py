from __future__ import annotations

import asyncio
import copy
import json
import os
import threading
import time
from concurrent.futures import Future
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .storage import JsonlWriter, backtrack_summaries_path
from .target_env import parse_env_file


DEFAULT_SUMMARY_MAX_INPUT_CHARS = 80_000
DEFAULT_SUMMARY_FLUSH_TIMEOUT_SECONDS = 5.0
DEFAULT_SUMMARY_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


@dataclass(frozen=True)
class SummaryLLMConfig:
    api_key: str
    base_url: str | None
    model_name: str


def load_summary_llm_config(
    *,
    model_name: str | None = None,
    env_path: str | Path | None = None,
) -> SummaryLLMConfig | None:
    env_values = _load_env_values(DEFAULT_SUMMARY_ENV_FILE if env_path is None else env_path)
    resolved_model = (
        model_name
        or env_values.get("SUMMARY_MODEL_NAME")
        or os.getenv("SUMMARY_MODEL_NAME")
        or ""
    )
    api_key = (
        env_values.get("OPENROUTER_API_KEY")
        or env_values.get("OPENAI_API_KEY")
        or env_values.get("API_KEY")
        or env_values.get("GEMINI_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or ""
    )
    base_url = (
        env_values.get("OPENROUTER_BASE_URL")
        or env_values.get("OPENAI_BASE_URL")
        or env_values.get("BASE_URL")
        or os.getenv("OPENROUTER_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("BASE_URL")
        or None
    )
    if not resolved_model or not api_key:
        return None
    return SummaryLLMConfig(api_key=api_key, base_url=base_url, model_name=resolved_model)


class BacktrackSummaryManager:
    def __init__(
        self,
        *,
        run_id: str,
        log_dir: str | Path,
        enabled: bool,
        model_name: str | None = None,
        max_input_chars: int = DEFAULT_SUMMARY_MAX_INPUT_CHARS,
        flush_timeout_seconds: float = DEFAULT_SUMMARY_FLUSH_TIMEOUT_SECONDS,
    ) -> None:
        self.run_id = run_id
        self.log_dir = Path(log_dir)
        self.config = load_summary_llm_config(model_name=model_name) if enabled else None
        self.max_input_chars = max(0, max_input_chars)
        self.flush_timeout_seconds = max(0.0, flush_timeout_seconds)
        self._current_segment: list[dict[str, Any]] = []
        self._futures: list[Future] = []
        self._write_lock = threading.RLock()
        self._loop_lock = threading.RLock()
        self._loop_ready = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    @property
    def enabled(self) -> bool:
        return self.config is not None

    def reset_sidecar(self) -> None:
        if not self.enabled:
            return
        writer = JsonlWriter(backtrack_summaries_path(self.log_dir, self.run_id), overwrite=True)
        writer.close()

    def observe_records(self, records: list[dict[str, Any]]) -> None:
        if not self.enabled:
            return
        for record in records:
            if record.get("kind") == "llm":
                self._schedule_current_segment(end_before_record_uid=record.get("record_uid"))
                self._current_segment = []
            if self._current_segment or record.get("kind") == "llm":
                self._current_segment.append(copy.deepcopy(record))

    def close(self) -> None:
        if not self.enabled:
            return
        self._schedule_current_segment(end_before_record_uid=None)
        self._flush_futures()
        self._stop_loop()

    def _schedule_current_segment(self, *, end_before_record_uid: Any) -> None:
        if not self._current_segment:
            return
        segment = copy.deepcopy(self._current_segment)
        self._current_segment = []
        start_record_uid = segment[0].get("record_uid")
        if not isinstance(start_record_uid, str):
            return
        end_uid = end_before_record_uid if isinstance(end_before_record_uid, str) else None
        future = asyncio.run_coroutine_threadsafe(
            self._summarize_and_write(segment, start_record_uid, end_uid),
            self._ensure_loop(),
        )
        self._futures.append(future)

    async def _summarize_and_write(
        self,
        segment: list[dict[str, Any]],
        start_record_uid: str,
        end_before_record_uid: str | None,
    ) -> None:
        if self.config is None:
            return
        try:
            payload, source_mode = segment_summary_payload(segment, max_input_chars=self.max_input_chars)
            summary = await summarize_segment_with_openai(
                config=self.config,
                payload=payload,
                start_record_uid=start_record_uid,
                end_before_record_uid=end_before_record_uid,
                source_mode=source_mode,
            )
            if not summary.strip():
                return
            self._write_summary(
                {
                    "kind": "backtrack_summary",
                    "run_id": self.run_id,
                    "record_uid": start_record_uid,
                    "start_record_uid": start_record_uid,
                    "end_before_record_uid": end_before_record_uid,
                    "summary": summary.strip(),
                    "source_mode": source_mode,
                    "model": self.config.model_name,
                    "created_at": iso_now(),
                }
            )
        except Exception:
            return

    def _write_summary(self, item: dict[str, Any]) -> None:
        with self._write_lock:
            writer = JsonlWriter(backtrack_summaries_path(self.log_dir, self.run_id), overwrite=False)
            try:
                writer.write(item)
            finally:
                writer.close()

    def _flush_futures(self) -> None:
        deadline = time.monotonic() + self.flush_timeout_seconds
        for future in list(self._futures):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                future.cancel()
                continue
            try:
                future.result(timeout=remaining)
            except Exception:
                future.cancel()

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        with self._loop_lock:
            if self._loop is not None:
                return self._loop
            self._thread = threading.Thread(
                target=self._run_loop_thread,
                name=f"replay-backtrack-summary-{self.run_id}",
                daemon=True,
            )
            self._thread.start()
        self._loop_ready.wait()
        if self._loop is None:
            raise RuntimeError("Backtrack summary event loop failed to start.")
        return self._loop

    def _run_loop_thread(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        self._loop_ready.set()
        try:
            loop.run_forever()
        finally:
            loop.close()

    def _stop_loop(self) -> None:
        loop = self._loop
        thread = self._thread
        if loop is None or thread is None:
            return
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=1.0)
        self._loop = None
        self._thread = None


async def summarize_segment_with_openai(
    *,
    config: SummaryLLMConfig,
    payload: str,
    start_record_uid: str,
    end_before_record_uid: str | None,
    source_mode: str,
) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)
    from .openai_patch import suppress_openai_replay

    with suppress_openai_replay():
        response = await client.chat.completions.create(
            model=config.model_name,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize this replay timeline segment for future agent backtracking. "
                        "Return only a concise summary of the decision, useful context, tool results, "
                        "and risks. Do not include markdown headings."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "start_record_uid": start_record_uid,
                            "end_before_record_uid": end_before_record_uid,
                            "source_mode": source_mode,
                            "segment": payload,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                },
            ],
        )
    choice = response.choices[0] if response.choices else None
    message = getattr(choice, "message", None) if choice is not None else None
    content = getattr(message, "content", None) if message is not None else None
    return content if isinstance(content, str) else ""


def segment_summary_payload(
    segment: list[dict[str, Any]],
    *,
    max_input_chars: int,
) -> tuple[str, str]:
    segment = [record for record in segment if not _is_internal_replay_boundary(record)]
    raw = json.dumps(segment, ensure_ascii=False, sort_keys=True)
    if len(raw) <= max_input_chars:
        return raw, "raw"
    compact = compact_segment_card(segment)
    return json.dumps(compact, ensure_ascii=False, sort_keys=True), "deterministic"


def _is_internal_replay_boundary(record: dict[str, Any]) -> bool:
    metadata = record.get("metadata")
    return isinstance(metadata, dict) and metadata.get("internal_replay_boundary") is True


def compact_segment_card(segment: list[dict[str, Any]]) -> dict[str, Any]:
    llm_record = next((record for record in segment if record.get("kind") == "llm"), {})
    return {
        "record_uid": llm_record.get("record_uid"),
        "created_at": _record_created_at(llm_record),
        "decision_hint": _preview(_llm_output_hint(llm_record), limit=800),
        "tool_calls_preview": _preview(_llm_tool_calls(llm_record), limit=800),
        "tool_records_preview": [
            {
                "record_uid": record.get("record_uid"),
                "tool_name": (record.get("input") or {}).get("tool_name") if isinstance(record.get("input"), dict) else None,
                "arguments_preview": _preview((record.get("input") or {}).get("arguments") if isinstance(record.get("input"), dict) else None),
                "status": "error" if record.get("error") else "ok",
                "output_preview": _preview((record.get("output") or {}).get("value") if isinstance(record.get("output"), dict) else None),
                "error_preview": _preview(record.get("error")),
                "effects_preview": _preview(record.get("effects")),
            }
            for record in segment
            if record.get("kind") == "tool"
        ],
    }


def _load_env_values(env_path: str | Path | None) -> dict[str, str]:
    if env_path is not None:
        path = Path(env_path)
        return parse_env_file(path) if path.exists() else {}
    for path in _candidate_env_paths():
        if path.exists():
            return parse_env_file(path)
    return {}


def _candidate_env_paths() -> list[Path]:
    cwd = Path.cwd().resolve()
    paths = [cwd / ".env", *(parent / ".env" for parent in cwd.parents)]
    package_root_env = Path(__file__).resolve().parents[1] / ".env"
    if package_root_env not in paths:
        paths.append(package_root_env)
    return paths


def _record_created_at(record: dict[str, Any]) -> Any:
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get("created_at")
    return None


def _llm_output_hint(record: dict[str, Any]) -> Any:
    output = record.get("output")
    if not isinstance(output, dict):
        return None
    return output.get("content") or output.get("raw_response")


def _llm_tool_calls(record: dict[str, Any]) -> Any:
    output = record.get("output")
    if not isinstance(output, dict):
        return None
    return output.get("tool_calls")


def _preview(value: Any, *, limit: int = 400) -> str:
    if value is None:
        return ""
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        text = repr(value)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3].rstrip() + "..."


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
