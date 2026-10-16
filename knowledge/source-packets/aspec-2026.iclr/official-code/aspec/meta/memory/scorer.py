"""Specialist scoring and epoch-2 selection.

Extracted from the original SpecialistMemoryManager.
"""

from __future__ import annotations

from typing import Any

import torch
from loguru import logger

from .chat_history import ChatHistoryManager
from .store import MemoryStore


class SpecialistScorer:
    """Tracks epoch-1 specialist scores and selects top specialists for epoch 2."""

    def __init__(self) -> None:
        self.scores_epoch1: dict[str, dict[str, Any]] = {}
        self.all_created_epoch1: list[dict[str, Any]] = []
        self.top_for_epoch2: list[str] = []
        self.created_this_run: set[str] = set()

    def update_score(self, op_name: str, score: float, prompt: str | None = None) -> None:
        if op_name not in self.scores_epoch1:
            self.scores_epoch1[op_name] = {"name": op_name, "score": 0.0, "count": 0, "prompt": prompt}
        self.scores_epoch1[op_name]["score"] += float(score or 0)
        self.scores_epoch1[op_name]["count"] += 1

    def record_creation(self, op_name: str, score: float, prompt: str) -> None:
        self.all_created_epoch1.append({"name": op_name, "score": score, "prompt": prompt})
        self.created_this_run.add(op_name)

    async def select_specialists_for_epoch2(
        self,
        optimizer,
        memory_store: MemoryStore,
        chat_history_manager: ChatHistoryManager,
    ) -> None:
        """Select top-k specialists for epoch 2 using KMeans + greedy selection (Eq. 5)."""
        k = getattr(optimizer, "max_specialized_operators", 5)
        logger.info(f"--- END OF EPOCH 1: Selecting top {k} specialists for Epoch 2 ---")

        if not self.all_created_epoch1 and not self.scores_epoch1:
            logger.warning("No specialists were created in Epoch 1. Epoch 2 will proceed with base operators only.")
            return

        try:
            import numpy as np
            from sklearn.cluster import KMeans

            specialist_data: dict[str, dict[str, Any]] = {}
            for s in self.all_created_epoch1:
                name = s.get("name")
                if name and name not in specialist_data:
                    specialist_data[name] = {"scores": [], "count": 0, "prompt": s.get("prompt")}
            for name, data in self.scores_epoch1.items():
                entry = specialist_data.setdefault(name, {"scores": [], "count": 0, "prompt": data.get("prompt")})
                if data.get("count"):
                    entry["scores"].append(data["score"] / data["count"])
                    entry["count"] += data["count"]
            logger.info(
                "Epoch 1 specialist aggregation: "
                + str({n: {"avg": d["scores"], "count": d["count"]} for n, d in specialist_data.items()})
            )

            unique_specialists = list(specialist_data.keys())
            if not unique_specialists:
                logger.warning("No unique specialists to select from.")
                return

            if len(unique_specialists) <= k:
                logger.info(f"Fewer than {k} specialists created ({len(unique_specialists)}). Selecting all.")
                self.top_for_epoch2 = unique_specialists
            else:
                logger.info(f"Selecting top {k} diverse specialists from {len(unique_specialists)} candidates.")

                prompts = []
                avg_scores = []
                for name in unique_specialists:
                    prompt = specialist_data[name].get("prompt") or name.replace("_", " ")
                    prompts.append(prompt)
                    scores = specialist_data[name]["scores"]
                    avg_scores.append(float(np.mean(scores)) if scores else 0.0)

                embeddings_tensors = [optimizer._get_embedding_with_cache(p) for p in prompts]
                embeddings_np = torch.stack(embeddings_tensors).cpu().numpy()
                scores_np = np.array(avg_scores)

                k = min(k, len(unique_specialists))
                kmeans = KMeans(n_clusters=k, random_state=5, n_init=10).fit(embeddings_np)
                labels = kmeans.labels_
                lambda_div = 1.0

                def objective(selected_set: set[int]) -> float:
                    if not selected_set:
                        return 0.0
                    perf_sum = float(scores_np[list(selected_set)].sum())
                    div_sum = 0.0
                    for c in range(k):
                        idxs = [i for i in selected_set if labels[i] == c]
                        if idxs:
                            div_sum += float(scores_np[idxs].max())
                    return perf_sum + lambda_div * div_sum

                selected: set[int] = set()
                while len(selected) < k:
                    best_i = None
                    best_gain = -1e18
                    base_obj = objective(selected)
                    for i in range(len(unique_specialists)):
                        if i in selected:
                            continue
                        new_obj = objective(selected | {i})
                        gain = new_obj - base_obj
                        if gain > best_gain or (
                            abs(gain - best_gain) < 1e-9
                            and scores_np[i] > (scores_np[best_i] if best_i is not None else -1e18)
                        ):
                            best_gain = gain
                            best_i = i
                    if best_i is None:
                        break
                    selected.add(int(best_i))

                self.top_for_epoch2 = [unique_specialists[i] for i in selected]

            logger.info(f"Selected {len(self.top_for_epoch2)} specialists for Epoch 2: {self.top_for_epoch2}")

            # Validate memory files
            validated = []
            for name in self.top_for_epoch2:
                if memory_store.has_required_sections(name):
                    validated.append(name)
                    logger.info(f"{name}: Memory file validated")
                else:
                    logger.warning(f"{name}: Memory file missing or incomplete - SKIPPING")

            if len(validated) < len(self.top_for_epoch2):
                logger.warning(f"Memory validation failed for {len(self.top_for_epoch2) - len(validated)} specialists")
                self.top_for_epoch2 = validated

            # Prune non-selected specialists
            current_specialists = {op for op in optimizer.operator_pool if op not in optimizer.operators}
            to_prune = current_specialists - set(self.top_for_epoch2)
            if to_prune:
                logger.info(f"Pruning {len(to_prune)} specialists from operator pool.")
                for op_name in to_prune:
                    if op_name in optimizer.operator_pool:
                        del optimizer.operator_pool[op_name]
                    if op_name in optimizer.operator_pool_embeddings:
                        del optimizer.operator_pool_embeddings[op_name]
                    chat_history_manager.prune(op_name)
                    memory_store.archive_and_delete(op_name, "epoch2_pruned")

                optimizer.operator_embeddings_tensor = optimizer._rebuild_embeddings_tensor()
                logger.info(f"Updated embeddings for {len(optimizer.operator_pool)} operators after pruning.")

        except Exception as e:
            logger.error(f"Failed to select specialists for Epoch 2: {e}. Proceeding with all.")
            self.top_for_epoch2 = list(
                {(s.get("name") if isinstance(s, dict) else str(s)) for s in self.all_created_epoch1}
            )
