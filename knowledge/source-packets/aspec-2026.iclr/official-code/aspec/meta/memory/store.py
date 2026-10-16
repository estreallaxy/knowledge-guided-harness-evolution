"""High-level facade for specialist memory operations.

Wraps a ``MemoryBackend`` with convenient typed methods.
"""

from __future__ import annotations

import re
import time
from pathlib import Path

from loguru import logger

from aspec.meta.types import OperatorPool, OperatorSpec

from . import parser
from .backend import MemoryBackend
from .schema import (
    MemoryDocument,
    MemorySection,
    StructuredMemoryEntry,
)


# ---------------------------------------------------------------------------
# Memory directory resolution
# ---------------------------------------------------------------------------


def resolve_memory_dir(
    root_path: str,
    mode_dir: str,
    current_round_dir: str | None = None,
    round_num: int | None = None,
) -> Path:
    """Consolidated memory-directory resolution.

    Priority:
        1. ``current_round_dir`` / specialist_memory
        2. ``root_path / mode_dir / round_N`` / specialist_memory
    """
    if current_round_dir:
        return Path(current_round_dir) / "specialist_memory"
    if round_num is not None and round_num > 0:
        return Path(root_path) / mode_dir / f"round_{round_num}" / "specialist_memory"
    raise ValueError("resolve_memory_dir: either current_round_dir or round_num must be provided")


# ---------------------------------------------------------------------------
# MemoryStore
# ---------------------------------------------------------------------------


class MemoryStore:
    """High-level operations on specialist memory documents."""

    def __init__(self, backend: MemoryBackend) -> None:
        self.backend = backend

    # --- basic CRUD -----------------------------------------------------------

    def ensure_memory_file(self, op_name: str) -> None:
        """Create a starter memory file if none exists."""
        if self.backend.exists(op_name):
            return
        doc = MemoryDocument(
            operator_name=op_name,
            title=f"{op_name.replace('_', ' ')}'s Memory",
        )
        self.backend.save(doc)
        logger.info(f"Initialized memory file for {op_name}")

    def load_document(self, op_name: str) -> MemoryDocument | None:
        return self.backend.load(op_name)

    def save_document(self, doc: MemoryDocument) -> None:
        self.backend.save(doc)

    # --- section-level access -------------------------------------------------

    def replace_section(self, op_name: str, section: MemorySection, content: str) -> bool:
        """Replace (or insert) a section in the operator's memory file.

        Returns True on success.
        """
        try:
            if not (op_name and isinstance(content, str) and content.strip()):
                return False
            self.ensure_memory_file(op_name)
            doc = self.backend.load(op_name)
            if doc is None:
                return False
            doc.set_section(section, content.strip())
            self.backend.save(doc)
            return True
        except Exception as e:
            logger.error(f"Failed to replace {section.value} for {op_name}: {e}")
            return False

    # --- append operations ----------------------------------------------------

    def append_raw_block(self, op_name: str, block_text: str, add_timestamp_header: bool = False) -> None:
        """Append raw markdown to the operator's memory file.

        Uses the backend's raw append to avoid full parse/serialize cycle
        for performance (matches original behavior).
        """
        if not (block_text and op_name):
            return
        if not str(block_text).strip():
            return
        try:
            self.ensure_memory_file(op_name)
            # Try to detect and normalize structured entries
            normalized = self._extract_structured_tuple(block_text)
            if normalized:
                entry_text = parser._render_structured_entry(normalized)
                self.backend.append_raw(op_name, "\n" + entry_text + "\n\n")
                logger.info(f"Appended structured memory entry for {op_name}")
            else:
                parts = []
                if add_timestamp_header:
                    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    parts.append(f"\n<!-- appended: {ts} -->\n")
                parts.append(block_text.rstrip("\n") + "\n\n")
                self.backend.append_raw(op_name, "".join(parts))
                logger.info(f"Appended memory block for {op_name}")
        except Exception as e:
            logger.error(f"Failed to append block for {op_name}: {e}")

    # --- query / inspection ---------------------------------------------------

    def get_memory_headings(self, op_name: str, max_lines: int = 1000) -> list[str]:
        """Return markdown headings found in the memory file."""
        raw = self.backend.read_raw(op_name) if hasattr(self.backend, "read_raw") else ""
        if not raw:
            doc = self.backend.load(op_name)
            if doc is None:
                return []
            raw = parser.serialize(doc)
        headings: list[str] = []
        for i, line in enumerate(raw.splitlines()):
            if i >= max_lines:
                break
            stripped = line.strip()
            if stripped.startswith("#"):
                headings.append(stripped)
        return headings

    def get_memory_preview(self, op_name: str, words_per_heading: int = 100, short_char_threshold: int = 2000) -> str:
        """Return a sanitized preview of the memory file."""
        raw = self.backend.read_raw(op_name) if hasattr(self.backend, "read_raw") else ""
        if not raw:
            doc = self.backend.load(op_name)
            if doc is None:
                return ""
            raw = parser.serialize(doc)
        text = raw
        # Sanitize JSON/fenced code blocks
        text = re.sub(r"```\s*json[\s\S]*?```", "[omitted json]", text, flags=re.IGNORECASE)
        text = re.sub(r"```[a-zA-Z0-9_]*\s*[\s\S]*?```", "[omitted]", text, flags=re.IGNORECASE)
        text = text.replace("```", "")
        if len(text) <= short_char_threshold:
            return text
        lines = text.splitlines()
        preview_parts: list[str] = []
        current_heading: str | None = None
        current_words: list[str] = []

        def _flush() -> None:
            if current_heading is not None:
                joined = " ".join(current_words).strip()
                if joined:
                    preview_parts.append(joined)

        for ln in lines:
            if ln.strip().startswith("#"):
                _flush()
                preview_parts.append(ln)
                current_heading = ln
                current_words = []
            else:
                if current_heading is not None and len(current_words) < words_per_heading:
                    current_words.extend(ln.strip().split())
        _flush()
        out = "\n".join(preview_parts)
        out = re.sub(r"```\s*json[\s\S]*?```", "[omitted json]", out, flags=re.IGNORECASE)
        out = re.sub(r"```[a-zA-Z0-9_]*\s*[\s\S]*?```", "[omitted]", out, flags=re.IGNORECASE)
        out = out.replace("```", "")
        return out

    # --- lifecycle ------------------------------------------------------------

    def archive_and_delete(self, op_name: str, tag: str = "pruned") -> None:
        self.backend.archive(op_name, tag)

    def list_specialists(self) -> list[str]:
        return self.backend.list_specialists()

    def has_required_sections(self, op_name: str) -> bool:
        doc = self.backend.load(op_name)
        if doc is None:
            return False
        return doc.has_required_sections()

    def sync_pool(self, pool: OperatorPool, base_operators: set[str]) -> tuple[list[str], list[str]]:
        """Validate pool against memory files. Returns (removed, added)."""
        valid_names = {n for n in self.list_specialists() if self.has_required_sections(n)}
        removed: list[str] = []
        added: list[str] = []
        for name in list(pool):
            if "_" in name and name.split("_")[0] in base_operators and name not in valid_names:
                del pool[name]
                removed.append(name)
        for name in valid_names:
            if name not in pool:
                entry: OperatorSpec = {
                    "base_template": name.split("_")[0] if "_" in name else "CoT",
                    "prompt": "",
                    "chat_history": [],
                }
                pool[name] = entry
                added.append(name)
        return removed, added

    # --- internal helpers (matches original SpecialistMemoryManager logic) -----

    @staticmethod
    def _extract_structured_tuple(block_text: str) -> StructuredMemoryEntry | None:
        """Detect and extract a structured tuple from block_text."""
        if not isinstance(block_text, str) or not block_text.strip():
            return None
        lines = [ln.strip() for ln in block_text.splitlines() if ln.strip()]
        if not lines:
            return None
        kv = {"problem_pattern": "", "approach_summary": "", "failure_mode": "", "general_rule": ""}

        def match_key(s: str, patterns: list[str]) -> bool:
            s_l = s.lower()
            return any(p in s_l for p in patterns)

        for ln in lines:
            ln_clean = ln.lstrip("-• ")
            parts = ln_clean.split(":", 1)
            if len(parts) != 2:
                continue
            key, val = parts[0].strip(), parts[1].strip()
            if not val:
                continue
            if match_key(key, ["problem-pattern", "problem pattern", "pattern"]):
                kv["problem_pattern"] = val
            elif match_key(key, ["approach-summary", "approach summary", "approach"]):
                kv["approach_summary"] = val
            elif match_key(key, ["failure-mode", "failure mode", "failure"]):
                kv["failure_mode"] = val
            elif match_key(key, ["general-rule", "general rule", "when-to-apply", "when to apply"]):
                kv["general_rule"] = val

        have_core = bool(kv["general_rule"]) and any(
            kv[k] for k in ["problem_pattern", "approach_summary", "failure_mode"]
        )
        if not have_core:
            return None
        return StructuredMemoryEntry(**kv)
