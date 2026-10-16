"""In-memory chat history manager for specialists."""

from __future__ import annotations

import copy
from typing import Any

from loguru import logger

from aspec.meta.types import Architecture, ChatHistory


class ChatHistoryManager:
    """Sliding-window chat history for specialist operators (max 20 entries)."""

    MAX_HISTORY = 20

    def __init__(self) -> None:
        self.histories: dict[str, ChatHistory] = {}

    def get(self, op_name: str) -> ChatHistory:
        return self.histories.get(op_name, [])

    def set(self, op_name: str, history: ChatHistory) -> None:
        self.histories[op_name] = history

    def get_all(self) -> dict[str, ChatHistory]:
        return self.histories.copy()

    def prune(self, op_name: str) -> None:
        """Remove chat history for a pruned specialist."""
        self.histories.pop(op_name, None)

    async def merge(
        self,
        results_with_state: list[tuple[Any, float, Any, Architecture, dict[str, ChatHistory]]],
        base_operators: set[str],
        is_test: bool = False,
    ) -> None:
        """Merge chat histories from parallel problem executions."""
        if is_test:
            logger.info("Test mode: Specialist histories are frozen. Skipping merge of chat histories.")
            return

        final = copy.deepcopy(self.histories)

        for _action, _cost, _test_results, _, problem_histories in results_with_state:
            if not isinstance(problem_histories, dict):
                continue
            for op_name, history in problem_histories.items():
                if op_name in base_operators:
                    continue
                merged_history: ChatHistory = []
                seen_content: set[str] = set()

                for item in final.get(op_name, []):
                    content = str(item.get("content"))
                    if content and content not in seen_content:
                        merged_history.append(item)
                        seen_content.add(content)

                for item in history:
                    content = str(item.get("content"))
                    if content and content not in seen_content:
                        merged_history.append(item)
                        seen_content.add(content)

                for entry in merged_history:
                    ts = entry.get("timestamp", 0)
                    try:
                        entry["timestamp"] = 0.0 if ts is None else float(ts)
                    except (TypeError, ValueError):
                        entry["timestamp"] = 0.0

                final[op_name] = sorted(merged_history, key=lambda x: x["timestamp"])[-self.MAX_HISTORY :]

        self.histories = final
