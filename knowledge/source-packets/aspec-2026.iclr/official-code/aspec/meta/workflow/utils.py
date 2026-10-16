from __future__ import annotations

import json
import os
import re
from typing import TYPE_CHECKING, Any

from loguru import logger

from aspec.meta.types import Architecture, ChatHistory, OperatorPool, OperatorSpec

if TYPE_CHECKING:
    from aspec.meta.memory.store import MemoryStore


BASE_OPERATORS = {"CoT", "Debate", "SelfConsistency", "SelfRefine", "Ensemble", "Testing", "ReAct", "EarlyExit"}


def _resolve_memory_store(log_path: str) -> MemoryStore | None:
    """Construct a MemoryStore from a log path, or return None."""
    if not log_path:
        return None
    specialist_memory_dir = os.path.join(log_path, "specialist_memory")
    if not os.path.exists(specialist_memory_dir):
        return None
    try:
        from aspec.meta.memory.backends.markdown import MarkdownFileBackend
        from aspec.meta.memory.store import MemoryStore

        return MemoryStore(MarkdownFileBackend(specialist_memory_dir))
    except ImportError:
        return None


class WorkflowUtils:
    """Utility class containing general workflow helpers."""

    @staticmethod
    def annotate_layer_codes(layer_codes: list[tuple[str, str]]) -> str:
        """Annotate code blocks with their originating operators."""
        annotated_parts: list[str] = []
        for oname, code in layer_codes:
            annotated_parts.append(f"# From operator: {oname}\n{code}")
        return "\n\n".join(annotated_parts)

    @staticmethod
    def has_finish_action(text: str) -> bool:
        """Check if text contains a finish action."""
        if not text:
            return False
        return bool(re.search(r"<action>\s*finish\s*</action>", text, flags=re.IGNORECASE))

    @staticmethod
    def create_retry_prompt(retry_attempt: int, last_validation_msg: str, last_attempt_code: str, prompt: str) -> str:
        """Create a retry prompt for failed validation attempts."""
        prev_ctx = ""
        if last_validation_msg:
            prev_ctx += f"\nPREVIOUS_ERROR: {last_validation_msg}"
        if last_attempt_code:
            prev_ctx += f"\nPREVIOUS_CODE:\n```python\n{last_attempt_code}\n```"

        return f"""RETRY ATTEMPT {retry_attempt}: Previous validation failed.{prev_ctx}

CRITICAL REQUIREMENTS:
- You MUST implement EXACTLY the function specified in the function header
- Use the EXACT function name and parameters as provided
- Do NOT add imports, other functions, or extra code
- Return ONLY the required function implementation

{prompt}

REMEMBER: Implement ONLY the function shown in the header above. Nothing else."""

    @staticmethod
    def extract_code_block(text: str) -> str:
        """Extract code blocks from text using various patterns."""
        try:
            s = re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", "", str(text), flags=re.IGNORECASE)

            code_tags = re.findall(r"<code>([\s\S]*?)</code>", s, re.DOTALL | re.IGNORECASE)
            if code_tags:
                cand = code_tags[-1].strip()
                cand = re.sub(r"```[a-zA-Z0-9_]*", "", cand)
                cand = re.sub(r"```", "", cand)
                return cand.strip()

            blocks = re.findall(r"```(?:[a-zA-Z0-9_]+)?\s*\n?([\s\S]*?)```", s, re.DOTALL | re.IGNORECASE)
            if blocks:
                candidates = [b.strip() for b in blocks if b and b.strip()]
                for b in reversed(candidates):
                    if any(tok in b for tok in ["def ", "class ", "return ", "import "]):
                        clean = re.sub(r"```+[a-zA-Z0-9_]*", "", b)
                        clean = re.sub(r"```", "", clean)
                        return clean.strip()
                return candidates[-1].strip()

            tags = ["final_answer", "final", "voted", "refined", "answer", "input"]
            for tag in tags:
                match = re.search(rf"<{tag}>([\s\S]*?)</{tag}>", s, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    inner = re.findall(r"```(?:[a-zA-Z0-9_]+)?\s*\n?([\s\S]*?)```", content, re.DOTALL | re.IGNORECASE)
                    if inner:
                        return inner[-1].strip()
                    content_no_tags = re.sub(r"<[/]?[a-zA-Z][^>]*>", "", content)
                    if len(content_no_tags.splitlines()) > 1 and any(
                        k in content_no_tags for k in ["def ", "import ", "return "]
                    ):
                        return content_no_tags.strip()

            steps = re.findall(r"<step>([\s\S]*?)</step>", s, re.DOTALL | re.IGNORECASE)
            if steps:
                last = steps[-1]
                if re.search(r"<action>\s*finish\s*</action>", last, re.IGNORECASE):
                    m = re.search(r"<input>([\s\S]*?)</input>", last, re.DOTALL | re.IGNORECASE)
                    if m:
                        content = m.group(1).strip()
                        blk = re.findall(
                            r"```(?:[a-zA-Z0-9_]+)?\s*\n?([\s\S]*?)```", content, re.DOTALL | re.IGNORECASE
                        )
                        if blk:
                            return blk[-1].strip()
                        code_in = re.findall(r"<code>([\s\S]*?)</code>", content, re.DOTALL | re.IGNORECASE)
                        if code_in:
                            return code_in[-1].strip()
                        content_no_tags = re.sub(r"<[/]?[a-zA-Z][^>]*>", "", content)
                        if any(tok in content_no_tags for tok in ["def ", "return ", "class ", "import "]):
                            return content_no_tags.strip()
            return ""
        except Exception as e:
            logger.warning(f"Failed to extract code block: {e}")
            return ""

    @staticmethod
    def merge_chat_history(existing: ChatHistory, incoming: ChatHistory) -> ChatHistory:
        """Merge two chat history lists, removing duplicates based on content and timestamp."""
        ex = existing or []
        inc = incoming or []
        seen: set[tuple[str, Any]] = set()
        merged: ChatHistory = []
        for e in ex + inc:
            key = (e.get("content", ""), e.get("timestamp"))
            if key in seen:
                continue
            seen.add(key)
            merged.append(e)
        return merged

    @staticmethod
    def initialize_operators_from_architecture(
        static_architecture: Architecture | None,
        operator_pool: OperatorPool,
        operator_mapping: dict[str, type],
        operator_chat_histories: dict[str, ChatHistory],
        allow_specialist_autocreate: bool = True,
    ) -> None:
        """Initialize specialized operators from architecture configuration."""
        if not static_architecture:
            return

        for layer in static_architecture:
            for op_name in layer:
                if "_" in op_name and op_name not in operator_pool and allow_specialist_autocreate:
                    base_template = op_name.split("_")[0]
                    if base_template in operator_mapping:
                        logger.info(f"Creating new specialist operator '{op_name}' from architecture.")
                        new_entry: OperatorSpec = {
                            "base_template": base_template,
                            "prompt": "",
                            "chat_history": [],
                        }
                        operator_pool[op_name] = new_entry

        for op_name in operator_pool:
            if "_" in op_name:
                incoming = operator_pool[op_name].get("chat_history", [])
                existing = operator_chat_histories.get(op_name, [])
                operator_chat_histories[op_name] = WorkflowUtils.merge_chat_history(existing, incoming)

    @staticmethod
    def sync_operator_pool_with_memory_files(log_path: str, operator_pool: OperatorPool) -> None:
        """Align operator pool with specialist memory .md files."""
        store = _resolve_memory_store(log_path)
        if store is None:
            return
        removed, added = store.sync_pool(operator_pool, BASE_OPERATORS)
        if removed:
            logger.info(f"Syncing operator pool: Removing {len(removed)} specialists without valid memory files")
        if added:
            logger.info(f"Syncing operator pool: Adding {len(added)} new specialists with valid memory files")

    @staticmethod
    def load_operator_pool(
        log_path: str,
        operator_pool: OperatorPool,
        operator_chat_histories: dict[str, ChatHistory],
        frozen_mode: bool = False,
    ) -> None:
        """Load operator pool from JSON file if it exists."""
        if frozen_mode or not log_path:
            return

        pool_file = os.path.join(log_path, "specialist_operator_pool.json")
        if not os.path.exists(pool_file):
            return

        try:
            with open(pool_file, encoding="utf-8") as f:
                loaded_pool: dict[str, Any] = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load operator pool: {e}")
            return

        # Determine which specialists have valid memory files
        store = _resolve_memory_store(log_path)
        valid_specialists: set[str]
        if store is not None:
            valid_specialists = {n for n in store.list_specialists() if store.has_required_sections(n)}
        else:
            valid_specialists = set()

        # Only load specialists that have valid memory files
        for name, data in (loaded_pool or {}).items():
            if name in BASE_OPERATORS or name in valid_specialists:
                if name not in operator_pool:
                    operator_pool[name] = data
                else:
                    if data.get("prompt"):
                        operator_pool[name]["prompt"] = data["prompt"]
                    old_hist = operator_pool[name].get("chat_history", [])
                    new_hist = data.get("chat_history", [])
                    operator_pool[name]["chat_history"] = WorkflowUtils.merge_chat_history(old_hist, new_hist)
                    if data.get("specialist_data"):
                        operator_pool[name]["specialist_data"] = data["specialist_data"]
                    if data.get("base_template"):
                        operator_pool[name]["base_template"] = data["base_template"]

    @staticmethod
    def save_operator_pool(
        log_path: str,
        operator_pool: OperatorPool,
        operator_chat_histories: dict[str, ChatHistory],
        frozen_mode: bool = False,
    ) -> None:
        """Save operator pool to JSON file."""
        if frozen_mode or not log_path:
            return

        pool_file = os.path.join(log_path, "specialist_operator_pool.json")
        try:
            specialist_pool: dict[str, dict[str, Any]] = {}
            for op_name, op_data in operator_pool.items():
                if "_" in op_name:
                    clean_op_data = {k: v for k, v in op_data.items() if k != "embedding"}
                    if op_name in operator_chat_histories:
                        clean_op_data["chat_history"] = operator_chat_histories[op_name]
                    specialist_pool[op_name] = clean_op_data

            os.makedirs(log_path, exist_ok=True)
            temp_file = pool_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(specialist_pool, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, pool_file)
        except (OSError, TypeError) as e:
            logger.error(f"Failed to save operator pool: {e}")
