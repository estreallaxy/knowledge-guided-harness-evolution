"""Specialist memory manager — thin facade over the memory package.

Delegates to:
- ``MemoryStore`` (file I/O, section operations)
- ``ChatHistoryManager`` (in-memory chat histories)
- ``SpecialistScorer`` (epoch-1 scoring & epoch-2 selection)
- ``MemoryDistiller`` (LLM-based distillation)
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from aspec.meta.types import Architecture, ChatHistory

from .backends.markdown import MarkdownFileBackend
from .chat_history import ChatHistoryManager
from .distiller import MemoryDistiller
from .scorer import SpecialistScorer
from .schema import MemorySection
from .store import MemoryStore, resolve_memory_dir


class SpecialistMemoryManager:
    def __init__(self, optimizer) -> None:
        self.optimizer = optimizer

        current_round_dir = None
        if hasattr(self.optimizer, "evaluator") and hasattr(self.optimizer.evaluator, "_current_round_dir"):
            current_round_dir = self.optimizer.evaluator._current_round_dir
        elif hasattr(self.optimizer, "_current_round_dir"):
            current_round_dir = self.optimizer._current_round_dir

        self.memory_dir = resolve_memory_dir(
            root_path=self.optimizer.root_path,
            mode_dir=self.optimizer.mode_dir,
            current_round_dir=current_round_dir,
            round_num=getattr(self.optimizer, "round", None),
        )
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.warning(f"Failed to create specialist memory directory {self.memory_dir}: {e}")

        self._backend = MarkdownFileBackend(self.memory_dir)
        self.store = MemoryStore(self._backend)
        self._chat = ChatHistoryManager()
        self._scorer = SpecialistScorer()
        self._distiller: MemoryDistiller | None = None

    def _get_distiller(self) -> MemoryDistiller:
        if self._distiller is None:
            llm = getattr(self.optimizer, "llm", None)
            exec_llm = getattr(self.optimizer, "exec_llm", None)
            self._distiller = MemoryDistiller(self.store, llm=llm, exec_llm=exec_llm)
        return self._distiller

    # ===== File operations =====================================================

    def append_memory_block(self, op_name: str, block_text: str, add_timestamp_header: bool = False) -> None:
        if not (block_text and op_name) or not str(block_text).strip():
            return
        self.store.append_raw_block(op_name, block_text, add_timestamp_header=add_timestamp_header)

    def ensure_memory_file(self, op_name: str) -> None:
        try:
            self.store.ensure_memory_file(op_name)
        except Exception as e:
            logger.warning(f"Failed to initialize memory file for {op_name}: {e}")

    def replace_specialist_prompt(self, op_name: str, new_prompt: str) -> bool:
        return self.store.replace_section(op_name, MemorySection.SPECIALIST_PROMPT, new_prompt)

    def get_memory_headings(self, op_name: str, max_lines: int = 1000) -> list[str]:
        try:
            return self.store.get_memory_headings(op_name, max_lines=max_lines)
        except Exception as e:
            logger.warning(f"Failed to read memory headings for {op_name}: {e}")
            return []

    def get_memory_preview(self, op_name: str, words_per_heading: int = 100, short_char_threshold: int = 2000) -> str:
        try:
            return self.store.get_memory_preview(
                op_name, words_per_heading=words_per_heading, short_char_threshold=short_char_threshold
            )
        except Exception as e:
            logger.warning(f"Failed to build memory preview for {op_name}: {e}")
            return ""

    # ===== Distillation ========================================================

    async def distill_and_update_memory_for_epoch(self, op_name: str, epoch: int) -> None:
        await self._get_distiller().distill_and_update(op_name, epoch)

    async def distill_memory_with_reflections(self, op_name: str, epoch: int) -> None:
        await self._get_distiller().distill_with_reflections(op_name, epoch)

    # ===== Chat history ========================================================

    async def merge_chat_histories(
        self, results_with_state: list[tuple[Any, float, Any, Architecture, dict[str, ChatHistory]]]
    ) -> None:
        await self._chat.merge(results_with_state, set(self.optimizer.operators), is_test=self.optimizer.is_test)

    def update_specialist_scores(self, op_name: str, score: float, prompt: str | None = None) -> None:
        if not self.optimizer.is_test and self.optimizer.current_epoch == 1:
            self._scorer.update_score(op_name, score, prompt)

    def get_chat_history_for_operator(self, op_name: str) -> ChatHistory:
        return self._chat.get(op_name)

    def set_chat_history_for_operator(self, op_name: str, history: ChatHistory) -> None:
        self._chat.set(op_name, history)

    def get_all_chat_histories(self) -> dict[str, ChatHistory]:
        return self._chat.get_all()

    def prune_specialist_history(self, op_name: str) -> None:
        self._chat.prune(op_name)

    def record_specialist_creation(self, op_name: str, score: float, prompt: str) -> None:
        if not self.optimizer.is_test and self.optimizer.current_epoch == 1:
            self._scorer.record_creation(op_name, score, prompt)
        self._scorer.created_this_run.add(op_name)

    # ===== Epoch-2 selection ===================================================

    async def select_specialists_for_epoch2(self) -> None:
        await self._scorer.select_specialists_for_epoch2(
            optimizer=self.optimizer,
            memory_store=self.store,
            chat_history_manager=self._chat,
        )
