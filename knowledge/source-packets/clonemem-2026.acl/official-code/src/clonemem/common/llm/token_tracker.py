import asyncio
import json
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict


class TokenUsage(BaseModel):
    input_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)

    @classmethod
    def from_token_summary(cls, data: Dict[str, int]) -> "TokenUsage":
        return cls(
            input_tokens=int(data.get("input_tokens", 0)),
            completion_tokens=int(data.get("completion_tokens", 0)),
            total_tokens=int(data.get("total_tokens", 0)),
        )

    def __sub__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens - other.input_tokens,
            completion_tokens=self.completion_tokens - other.completion_tokens,
            total_tokens=self.total_tokens - other.total_tokens,
        )

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )

    def __iadd__(self, other: "TokenUsage") -> "TokenUsage":
        self.input_tokens += other.input_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        return self


class TokenEvent(BaseModel):
    timestamp: datetime
    model_config = ConfigDict(frozen=True)

    run_id: str
    model: str
    generator: str
    prompt_name: str
    usage: TokenUsage
    meta: Dict[str, Any] = Field(default_factory=dict)


class TokenTracker:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self._events: List[TokenEvent] = []
        self._lock = asyncio.Lock()
        self._last_flushed = 0

    @property
    def events(self) -> List[TokenEvent]:
        return list(self._events)

    async def add(
            self,
            model: str,
            generator: str,
            prompt_name: str,
            usage: TokenUsage,
            meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        event = TokenEvent(
            timestamp=datetime.now(),
            run_id=self.run_id,
            model=model,
            generator=generator,
            prompt_name=prompt_name,
            usage=usage,
            meta=meta or {},
        )
        async with self._lock:
            self._events.append(event)

    def summary(self) -> TokenUsage:
        total = TokenUsage()
        for e in self._events:
            total += e.usage
        return total

    def summary_by_generator(self) -> Dict[str, TokenUsage]:
        out: Dict[str, TokenUsage] = {}
        for e in self._events:
            out[e.generator] = out.get(e.generator, TokenUsage()) + e.usage
        return out

    def summary_by_prompt(self) -> Dict[str, TokenUsage]:
        out: Dict[str, TokenUsage] = {}
        for e in self._events:
            key = f"{e.generator}:{e.prompt_name}"
            out[key] = out.get(key, TokenUsage()) + e.usage
        return out

    async def save(self, base_dir: str | Path) -> Path:
        """
        Persist tracker data to:
          - token_events.jsonl
          - token_summary.json
          - token_by_generator.json
          - token_by_prompt.json
        """
        base = Path(base_dir) / self.run_id
        base.mkdir(parents=True, exist_ok=True)

        async with self._lock:
            events = list(self._events)
            start = self._last_flushed
            new_events = events[start:]
            self._last_flushed = len(events)

        events_path = base / "token_events.jsonl"
        mode = "a" if events_path.exists() else "w"
        with events_path.open(mode, encoding="utf-8") as f:
            for e in new_events:
                f.write(json.dumps(e.model_dump(mode="json"), ensure_ascii=False) + "\n")

        summary_path = base / "token_summary.json"
        summary_payload = {
            "run_id": self.run_id,
            "total": self.summary().model_dump(),
            "num_events": len(events),
        }
        summary_path.write_text(
            json.dumps(summary_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        by_gen_path = base / "token_by_generator.json"
        by_gen_payload = {k: v.model_dump() for k, v in self.summary_by_generator().items()}
        by_gen_path.write_text(
            json.dumps(by_gen_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        by_prompt_path = base / "token_by_prompt.json"
        by_prompt_payload = {k: v.model_dump() for k, v in self.summary_by_prompt().items()}
        by_prompt_path.write_text(
            json.dumps(by_prompt_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return base
