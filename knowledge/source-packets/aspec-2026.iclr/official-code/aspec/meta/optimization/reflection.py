from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import torch
import torch.nn.functional as F

from aspec.controller.utils import get_sentence_embedding
from loguru import logger
from aspec.meta.models.encoder import architecture_to_text
from aspec.meta.prompt import REFLECTION_PRE_MUTATION_PROMPT
from aspec.meta.types import Architecture

if TYPE_CHECKING:
    from aspec.meta.optimizer import Optimizer


class ReflectionManager:
    def __init__(self, optimizer: Optimizer) -> None:
        self.optimizer = optimizer
        self.llm = optimizer.llm

        # Store reflections under the current round directory to avoid cross-run contamination
        self.strategic_reflections_path = (
            Path(optimizer.root_path) / optimizer.mode_dir / f"round_{optimizer.round}" / "strategic_reflections.jsonl"
        )

        # Defaults; can be overridden per-call
        self.default_window_size: int = getattr(self.optimizer, "reflection_window_size", 10)
        self.default_sim_threshold: float = getattr(self.optimizer, "reflection_similarity_threshold", 0.4)

    def build_reflection_prompt(self, **kwargs: Any) -> str:
        query_block = kwargs.get("query_block") or kwargs.get("query") or ""
        k = getattr(self.optimizer, "max_specialized_operators", 5)
        max_pool_size = 2 * k
        recent_window_json = kwargs.get("recent_window_json", "[]")
        prior_reflections_json = kwargs.get("prior_reflections_json", "[]")
        allowed_actions_str = kwargs.get("allowed_actions_str", "")

        # Get current specialist operators (non-base operators)
        current_specialists = []
        if hasattr(self.optimizer, "operator_pool") and self.optimizer.operator_pool:
            for op_name in self.optimizer.operator_pool:
                if op_name not in self.optimizer.operators:  # Not a base template
                    current_specialists.append(op_name)

        return REFLECTION_PRE_MUTATION_PROMPT.format(
            query_block=query_block,
            available_operators=", ".join(self.optimizer.operators),
            current_specialists=", ".join(current_specialists) if current_specialists else "None",
            max_pool_size=max_pool_size,
            recent_window=recent_window_json,
            prior_reflections=prior_reflections_json,
            allowed_actions=allowed_actions_str,
        )

    async def perform_self_reflection(self, **kwargs: Any) -> str | None:
        try:
            reflection_prompt = self.build_reflection_prompt(**kwargs)
            response = await self.llm.aask(reflection_prompt)
            return (response or "").strip()
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Self-reflection failed due to data error: {e}")
            return None
        except OSError as e:
            logger.error(f"Self-reflection failed due to I/O error: {e}")
            return None

    def load_strategic_reflections(self) -> list[dict[str, Any]]:
        """Load strategic reflections from file."""
        try:
            if not self.strategic_reflections_path.exists():
                return []
            reflections = []
            with open(self.strategic_reflections_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            reflections.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            return reflections
        except OSError as e:
            logger.warning(f"Failed to load strategic reflections: {e}")
            return []

    def _round_dirs(self, mode: str) -> list[Path]:
        try:
            base = Path(self.optimizer.root_path) / mode
            if not base.exists():
                return []
            dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith("round_")]
            dirs.sort(key=lambda p: int(re.sub(r"\D", "", p.name) or 0))
            return dirs
        except OSError as e:
            logger.debug(f"Failed to list round directories for mode '{mode}': {e}")
            return []

    def _load_reflections_from_modes(self, modes: list[str]) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for mode in modes:
            for rd in self._round_dirs(mode):
                path = rd / "strategic_reflections.jsonl"
                if path.exists():
                    try:
                        with open(path, encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    entries.append(json.loads(line))
                                except json.JSONDecodeError:
                                    continue
                    except OSError as e:
                        logger.debug(f"Failed to read reflections from {path}: {e}")
                        continue
        return entries

    def _flatten_recent_experiences(self) -> list[dict[str, Any]]:
        if not hasattr(self.optimizer, "experience_buffer") or not self.optimizer.experience_buffer:
            return []
        all_exps: list[dict[str, Any]] = []
        for episode_exps in self.optimizer.experience_buffer.values():
            all_exps.extend(episode_exps)
        return all_exps

    def _get_recent_window(self, window_size: int) -> list[dict[str, Any]]:
        exps = self._flatten_recent_experiences()
        if not exps:
            return []
        return exps[-max(0, int(window_size)) :]

    def _entries_to_experiences(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        converted: list[dict[str, Any]] = []
        for e in entries:
            converted.append(
                {
                    "query": e.get("query", ""),
                    "cost": e.get("cost", ""),
                    "action": e.get("action", "UNKNOWN"),
                    "reward": e.get("final_score", e.get("reward", 0.0)),
                    "architecture": e.get("architecture", []),
                }
            )
        return converted

    def _embed_text(self, text: str) -> torch.Tensor | None:
        try:
            return get_sentence_embedding(text or "")
        except (RuntimeError, ValueError, OSError) as e:
            logger.debug(f"Embedding failed for text: {e}")
            return None

    def _cosine(self, a: torch.Tensor | None, b: torch.Tensor | None) -> float:
        if a is None or b is None:
            return 0.0
        try:
            va = a.view(-1) if hasattr(a, "view") else a
            vb = b.view(-1) if hasattr(b, "view") else b
            return float(F.cosine_similarity(va.unsqueeze(0), vb.unsqueeze(0)).item())
        except (RuntimeError, ValueError, TypeError) as e:
            logger.debug(f"Cosine similarity computation failed: {e}")
            return 0.0

    def _find_similar_reflections(
        self, query_text: str, pool: list[dict[str, Any]], threshold: float
    ) -> list[dict[str, Any]]:
        try:
            q_emb = self._embed_text(query_text)
            ranked: list[tuple[float, dict[str, Any]]] = []
            for entry in pool:
                q = entry.get("query") or entry.get("original_query") or ""
                if not q:
                    continue
                e = self._embed_text(q)
                sim = self._cosine(q_emb, e)
                if sim >= float(threshold):
                    ranked.append((sim, entry))
            ranked.sort(key=lambda x: x[0], reverse=True)
            return [e for _, e in ranked[:20]]
        except (ValueError, TypeError, RuntimeError) as e:
            logger.debug(f"Failed to find similar reflections: {e}")
            return []

    def append_strategic_reflection(self, entry: dict[str, Any]) -> None:
        """Append a strategic reflection entry to file."""
        try:
            # Ensure parent directory exists
            self.strategic_reflections_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.strategic_reflections_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning(f"Failed to append strategic reflection: {e}")
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to serialize strategic reflection entry: {e}")

    def update_strategic_reflection(self, updated_entry: dict[str, Any]) -> None:
        """Update an existing strategic reflection entry."""
        try:
            all_entries = self.load_strategic_reflections()
            query_key = updated_entry.get("query_key")

            found = False
            for i, entry in enumerate(all_entries):
                if entry.get("query_key") == query_key:
                    all_entries[i] = updated_entry
                    found = True
                    break

            if not found:
                all_entries.append(updated_entry)

            # Ensure parent directory exists
            self.strategic_reflections_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.strategic_reflections_path, "w", encoding="utf-8") as f:
                for entry in all_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as e:
            logger.warning(f"Failed to update strategic reflection: {e}")
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to serialize strategic reflection entry: {e}")

    def find_existing_reflection(self, query_key: str) -> dict[str, Any] | None:
        """Find existing reflection by query key."""
        reflections = self.load_strategic_reflections()
        for reflection in reflections:
            if reflection.get("query_key") == query_key:
                return reflection
        return None

    async def update_reflection_with_final_architecture(
        self, query_text: str, final_architecture: Architecture, score: float, total_cost: float
    ) -> None:
        """Update strategic reflection with final architecture and execution results."""
        try:
            query_key = self.get_query_key(query_text)
            existing_entry = self.find_existing_reflection(query_key)

            if existing_entry:
                # Update the entry with final results
                existing_entry["architecture"] = final_architecture
                existing_entry["final_score"] = score
                existing_entry["total_cost"] = total_cost
                existing_entry["window_events"] = list(self.optimizer.window_events)

                # Update the reflection entry
                self.update_strategic_reflection(existing_entry)
                logger.info(f"Updated strategic reflection with final architecture: {final_architecture}")
            else:
                logger.warning(f"No existing reflection found for query key: {query_key}")

        except (OSError, TypeError, ValueError) as e:
            logger.warning(f"Failed to update reflection with final architecture: {e}")

    def get_query_key(self, query_text: str) -> str:
        """Generate a key for the query."""
        normalized = " ".join(query_text.lower().split()[:50])
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]

    async def run_strategic_reflection_before_resample(self, current_query_text: str) -> None:
        """Run strategic reflection before resampling architecture."""
        try:
            arch_text = architecture_to_text(self.optimizer.current_architecture)
            self.load_strategic_reflections()

            query_key = self.get_query_key(current_query_text)
            existing_entry = self.find_existing_reflection(query_key)

            if existing_entry:
                if self.optimizer.current_epoch >= 2:
                    existing_entry["attempts"] = existing_entry.get("attempts", 0) + 1
                else:
                    existing_entry["attempts"] = 1

                if "attempted_architectures" not in existing_entry:
                    existing_entry["attempted_architectures"] = []

                existing_entry["attempted_architectures"].append(self.optimizer.current_architecture.copy())
                existing_entry["window_events"].extend(self.optimizer.window_events)
                self.update_strategic_reflection(existing_entry)

            if not existing_entry:
                window_copy = list(self.optimizer.window_events)
                window_text = json.dumps(window_copy, ensure_ascii=False)

                operator_meta_reflections = []
                for event in window_copy:
                    if event.get("operator_metas"):
                        for meta in event["operator_metas"]:
                            if meta.get("summary") and meta.get("confidence"):
                                operator_meta_reflections.append(
                                    f"Operator {meta.get('operator', 'Unknown')}: {meta.get('summary')} (Confidence: {meta.get('confidence')})"
                                )

                context_text = ""
                if operator_meta_reflections:
                    context_text = "Recent Operator Performance:\n" + "\n".join(operator_meta_reflections)

                truncated_query = " ".join(current_query_text.split()[:200]) + (
                    "..." if len(current_query_text.split()) > 200 else ""
                )
                action_semantics = "Action Semantics: RETAIN = keep current architecture and execute; RESAMPLE = invoke the architecture mutator to evolve the operator graph before execution."
                prompt_query = f"{action_semantics}\n\nQuery: {truncated_query}\nCurrent Architecture: {arch_text}\nWindow Events: {window_text}\nRelevant Past: {context_text}"
                reflection = await self.perform_self_reflection(
                    query_block=prompt_query,
                    mutation_history=[],
                    final_architecture=self.optimizer.current_architecture,
                    score="N/A",
                    reward=0.0,
                    conversation_logs=[],
                    ungraded=False,
                )
                entry = {
                    "query_key": query_key,
                    "query": truncated_query,
                    "architecture": self.optimizer.current_architecture,
                    "attempted_architectures": [self.optimizer.current_architecture],
                    "attempts": 1,
                    "window_events": window_copy,
                    "text": (
                        ((reflection.get("summary", "") + "\n" + reflection.get("performance_analysis", "")).strip())
                        if isinstance(reflection, dict)
                        else (reflection if isinstance(reflection, str) and reflection.strip() else prompt_query)
                    ),
                }
                self.append_strategic_reflection(entry)

        except (OSError, KeyError, ValueError, TypeError) as e:
            logger.warning(f"Strategic reflection failed: {e}")

    async def build_strategic_principles_text(
        self, current_query_text: str, window_size: int | None = 10, sim_threshold: float | None = 0.4
    ) -> str:
        try:
            w = int(window_size) if window_size is not None else int(self.default_window_size)
            th = float(sim_threshold) if sim_threshold is not None else float(self.default_sim_threshold)

            recent_window = self._get_recent_window(w)

            modes_to_read = ["train"] if self.optimizer.mode_dir == "train" else ["train", "test"]
            historical_pool = self._load_reflections_from_modes(modes_to_read)
            similar_refs = self._find_similar_reflections(current_query_text, historical_pool, th)

            # If live window is short (e.g., start of test), backfill with latest reflections across modes
            if len(recent_window) < w:
                backfill_needed = w - len(recent_window)
                historical_exps = self._entries_to_experiences(historical_pool)
                if historical_exps:
                    # Use the most recent entries (order preserved by _load_reflections_from_modes)
                    supplement = historical_exps[-backfill_needed:]
                    recent_window = (recent_window + supplement)[-w:]

            def _fmt_exp(exp: dict[str, Any]) -> dict[str, Any]:
                return {
                    "query": exp.get("query", ""),
                    "action": exp.get("action", "UNKNOWN"),
                    "reward": exp.get("reward", 0.0),
                    "architecture": exp.get("architecture", []),
                }

            recent_block = json.dumps([_fmt_exp(e) for e in recent_window], ensure_ascii=False)
            prior_block = json.dumps(
                [
                    {
                        "query": r.get("query", ""),
                        "architecture": r.get("architecture", []),
                        "text": r.get("text", ""),
                        "final_score": r.get("final_score", None),
                    }
                    for r in similar_refs
                ],
                ensure_ascii=False,
            )

            # Build a single consolidated prompt using REFLECTION_PRE_MUTATION_PROMPT
            # Determine allowed actions
            allowed_actions_list = []
            if getattr(self.optimizer, "mode_dir", "") == "test":
                allowed_actions_list = ["FINALIZE_ARCHITECTURE"]
            elif hasattr(self.optimizer, "epoch_manager") and hasattr(
                self.optimizer.epoch_manager, "get_allowed_mutator_actions"
            ):
                allowed_actions_list = list(self.optimizer.epoch_manager.get_allowed_mutator_actions() or [])

            reflection_prompt = self.build_reflection_prompt(
                query_block=current_query_text,
                recent_window_json=recent_block,
                prior_reflections_json=prior_block,
                allowed_actions_str=", ".join(allowed_actions_list),
            )
            response = await self.llm.aask(reflection_prompt)
            return (response or "").strip()
        except (KeyError, ValueError, TypeError, RuntimeError, OSError) as e:
            logger.warning(f"Failed to build strategic principles text: {e}")
            return ""

    def get_strategic_principles(self, current_query_text: str = "") -> str:
        """Synchronous accessor returning the reflection most relevant to the query, else the most recent."""
        try:
            prior_refs = self.load_strategic_reflections()
            if not prior_refs:
                return ""

            selected = None
            if current_query_text:
                similar = self._find_similar_reflections(current_query_text, prior_refs, self.default_sim_threshold)
                if similar:
                    selected = similar[0]
            if selected is None:
                selected = prior_refs[-1]

            reflection_text = selected.get("text", "")
            return f"Recent Strategic Insight: {reflection_text}" if reflection_text else ""

        except (OSError, KeyError, ValueError, TypeError) as e:
            logger.debug(f"Failed to get strategic principles: {e}")
            return ""
