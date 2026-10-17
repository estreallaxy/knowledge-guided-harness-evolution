from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional


class TraceWriter:
    def __init__(self, trace_path: str):
        self.trace_path = trace_path
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)

    def append(self, obj: Dict[str, Any]) -> None:
        with open(self.trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def new_call_id(self) -> str:
        return str(uuid.uuid4())

    def now(self) -> float:
        return time.time()


def sanitize_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for m in messages:
        mm = dict(m)
        if mm.get("content", None) is None:
            mm["content"] = ""
        out.append(mm)
    return out


def log_request(
    tw: TraceWriter,
    *,
    call_id: str,
    llm_name: str,
    call_site: str,
    sample_idx: int,
    turn_id: int,
    messages: List[Dict[str, Any]],
    gen_args: Dict[str, Any],
) -> None:
    tw.append(
        {
            "event": "request",
            "ts": tw.now(),
            "call_id": call_id,
            "llm": llm_name,
            "call_site": call_site,
            "sample_idx": sample_idx,
            "turn_id": turn_id,
            "messages": sanitize_messages(messages),
            "gen_args": gen_args,
        }
    )


def log_response(
    tw: TraceWriter,
    *,
    call_id: str,
    llm_name: str,
    call_site: str,
    sample_idx: int,
    turn_id: int,
    outputs: Any,
    meta: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, str]] = None,
) -> None:
    tw.append(
        {
            "event": "response",
            "ts": tw.now(),
            "call_id": call_id,
            "llm": llm_name,
            "call_site": call_site,
            "sample_idx": sample_idx,
            "turn_id": turn_id,
            "outputs": outputs,
            "meta": meta,
            "error": error,
        }
    )
