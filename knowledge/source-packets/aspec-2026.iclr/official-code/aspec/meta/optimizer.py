from __future__ import annotations

import asyncio
import contextlib
import copy
import json
import random
from typing import Any

import torch

from loguru import logger
from aspec.meta.epoch_manager import EpochManager
from aspec.meta.models.evaluator import Evaluator
from aspec.meta.models.evaluator.evaluator import ProblemResult
from aspec.meta.memory import SpecialistMemoryManager
from aspec.meta.optimization.checkpoint import CheckpointManager
from aspec.meta.optimization.core import CoreOptimizer
from aspec.meta.optimization.reflection import ReflectionManager
from aspec.meta.optimization.reward import RewardCalculator
from aspec.meta.types import Architecture, Experience, OperatorSpec, SpecialistExperience


class Optimizer(CoreOptimizer):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if not hasattr(self, "current_architecture") or self.current_architecture is None:
            self.current_architecture: Architecture = [["CoT"]]

        self.checkpoint_manager = CheckpointManager(self)
        if self.is_test:
            self.checkpoint_manager.read_only = True
        self.reward_calculator = RewardCalculator(self)
        self.reflection_manager = ReflectionManager(self)
        self.memory_manager = SpecialistMemoryManager(self)
        self.evaluator = Evaluator(self)
        self.epoch_manager = EpochManager(self)

        self._exp_buffer_lock = asyncio.Lock()
        self.experience_buffer: dict[int, list[Experience]] = {}

        self.window_events: list[dict[str, Any]] = []
        self.operator_pool_embeddings: dict[str, torch.Tensor] = {}

        self.total_problems_evaluated: int = 0

        # Specialist experience collection for Epoch 2 prompt refinement.
        # Writers run during concurrent worker phase, reader runs after merge.
        self.specialist_experience_buffer: dict[str, list[SpecialistExperience]] = {}
        self._specialist_exp_lock = asyncio.Lock()

    @property
    def current_epoch(self) -> int:
        try:
            return self.epoch_manager.current_epoch
        except AttributeError:
            return getattr(self, "_current_epoch", 0)

    @current_epoch.setter
    def current_epoch(self, value: int) -> None:
        with contextlib.suppress(AttributeError):
            self.epoch_manager.current_epoch = int(value)
        self._current_epoch = int(value)

    async def _update_embeddings_from_pool(self) -> None:
        """Re-calculates operator embeddings and the main tensor from the current operator pool."""
        if self.is_test or self.epoch_manager.is_epoch2_or_later():
            return
        if not hasattr(self, "operator_pool_embeddings") or self.operator_pool_embeddings is None:
            self.operator_pool_embeddings = {}

        specialists = {name for name in self.operator_pool if name not in self.operators}

        for op_name in specialists:
            full_text = self._get_operator_full_text(op_name)
            self.operator_pool_embeddings[op_name] = self._get_embedding_with_cache(full_text)

        current_embedding_keys = set(self.operator_pool_embeddings.keys())
        pool_keys = set(self.operator_pool.keys())
        keys_to_remove = current_embedding_keys - pool_keys
        for op_name in keys_to_remove:
            if op_name not in self.operators and op_name in self.operator_pool_embeddings:
                del self.operator_pool_embeddings[op_name]

        self.operator_embeddings_tensor = self._rebuild_embeddings_tensor()

    async def _merge_batch_results(self, results_with_state: list[ProblemResult]) -> None:
        """Merges the operator pools and chat histories from parallel problem executions."""
        if self.is_test:
            logger.info(
                "Test mode: Operator pool and specialist histories are frozen. Skipping merge of batch results."
            )
            return

        initial_pool = copy.deepcopy(self.operator_pool)
        final_operator_pool = copy.deepcopy(self.operator_pool)

        specialist_candidates: dict[str, list[OperatorSpec]] = {}

        for _action, _cost, _test_results, problem_pool, problem_histories in results_with_state:
            # Guard against empty lists - sometimes these are [] instead of {}
            if not isinstance(problem_pool, dict):
                continue
            if not isinstance(problem_histories, dict):
                problem_histories = {}
            for op_name, op_data in problem_pool.items():
                if op_name not in self.operators:
                    if op_name not in specialist_candidates:
                        specialist_candidates[op_name] = []
                    op_data_with_history = copy.deepcopy(op_data)
                    op_data_with_history["chat_history"] = problem_histories.get(op_name, [])
                    specialist_candidates[op_name].append(op_data_with_history)

        for op_name, candidates in specialist_candidates.items():
            if not candidates:
                continue

            if op_name in initial_pool:
                existing_prompt = initial_pool[op_name].get("prompt", "").strip()
                base_template = initial_pool[op_name].get("base_template", op_name.split("_")[0])
                candidate_prompts = [cand.get("prompt", "").strip() for cand in candidates]
                if self.is_test or all(prompt == existing_prompt for prompt in candidate_prompts):
                    merged_op_data: OperatorSpec = initial_pool[op_name].copy()
                    # Preserve specialist_data from candidates if available
                    candidate_specialist_data = next(
                        (c.get("specialist_data", {}) for c in candidates if c.get("specialist_data")), {}
                    )
                    if candidate_specialist_data:
                        merged_op_data["specialist_data"] = candidate_specialist_data
                else:
                    try:
                        all_candidates = [existing_prompt] + [
                            p for p in candidate_prompts if p and p != existing_prompt
                        ]
                        idx = await self._pick_best_prompt(op_name, base_template, all_candidates)
                        chosen_prompt = all_candidates[idx]
                        merged_op_data: OperatorSpec = initial_pool[op_name].copy()
                        merged_op_data["prompt"] = chosen_prompt
                        # Preserve specialist_data from candidates if available
                        candidate_specialist_data = next(
                            (c.get("specialist_data", {}) for c in candidates if c.get("specialist_data")), {}
                        )
                        if candidate_specialist_data:
                            merged_op_data["specialist_data"] = candidate_specialist_data
                    except (json.JSONDecodeError, KeyError, IndexError, ValueError):
                        chosen_candidate = random.choice(candidates)
                        merged_op_data: OperatorSpec = {
                            "prompt": chosen_candidate.get("prompt", ""),
                            "base_template": chosen_candidate.get("base_template", ""),
                            "specialist_data": chosen_candidate.get(
                                "specialist_data", initial_pool.get(op_name, {}).get("specialist_data", {})
                            ),
                        }
            else:
                base_template = candidates[0].get("base_template", op_name.split("_")[0])
                try:
                    cand_prompts = [c.get("prompt", "") for c in candidates]
                    idx = await self._pick_best_prompt(op_name, base_template, cand_prompts)
                    chosen_candidate = candidates[idx]
                except (json.JSONDecodeError, KeyError, IndexError, ValueError):
                    chosen_candidate = random.choice(candidates)
                merged_op_data: OperatorSpec = {
                    "prompt": chosen_candidate.get("prompt", ""),
                    "base_template": chosen_candidate.get("base_template", ""),
                    "specialist_data": chosen_candidate.get("specialist_data", {}),
                }

            final_operator_pool[op_name] = merged_op_data

        self.operator_pool = final_operator_pool

        await self.memory_manager.merge_chat_histories(results_with_state)

        newly_added_specialists = set(final_operator_pool.keys()) - set(initial_pool.keys())
        modified_specialists: set[str] = set()

        for op_name in set(initial_pool.keys()).intersection(set(final_operator_pool.keys())):
            if op_name not in self.operators:
                initial_prompt = initial_pool[op_name].get("prompt", "").strip()
                final_prompt = final_operator_pool[op_name].get("prompt", "").strip()
                if initial_prompt != final_prompt:
                    if self.is_test:
                        # Revert any prompt changes in test mode
                        final_operator_pool[op_name]["prompt"] = initial_prompt
                        # Preserve specialist_data from initial pool
                        if "specialist_data" in initial_pool[op_name]:
                            final_operator_pool[op_name]["specialist_data"] = initial_pool[op_name]["specialist_data"]
                    else:
                        try:
                            base_template = final_operator_pool[op_name].get("base_template", op_name.split("_")[0])
                            idx = await self._pick_best_prompt(op_name, base_template, [initial_prompt, final_prompt])
                            best = [initial_prompt, final_prompt][idx]
                            final_operator_pool[op_name]["prompt"] = best
                            # Preserve specialist_data from initial pool
                            if "specialist_data" in initial_pool[op_name]:
                                final_operator_pool[op_name]["specialist_data"] = initial_pool[op_name][
                                    "specialist_data"
                                ]
                        except (json.JSONDecodeError, KeyError, IndexError, ValueError):
                            pass
                        modified_specialists.add(op_name)

        pruned_specialists = set(initial_pool.keys()) - set(final_operator_pool.keys())
        pool_changed = bool(newly_added_specialists or modified_specialists or pruned_specialists)

        if not pool_changed:
            pass
        elif self.epoch_manager.is_epoch2_or_later():
            logger.info(f"Epoch {self.epoch_manager.current_epoch}: Pool frozen. Skipping embedding updates.")
        else:
            logger.info("Operator pool changed. Updating embeddings for modified operators.")
            if not hasattr(self, "operator_pool_embeddings") or self.operator_pool_embeddings is None:
                self.operator_pool_embeddings = {}

            for op_name in newly_added_specialists.union(modified_specialists):
                full_text = self._get_operator_full_text(op_name)
                self.operator_pool_embeddings[op_name] = self._get_embedding_with_cache(full_text)

            for op_name in pruned_specialists:
                if op_name in self.operator_pool_embeddings:
                    del self.operator_pool_embeddings[op_name]

            self.operator_embeddings_tensor = self._rebuild_embeddings_tensor()

        logger.info("Finished merging operator pools and chat histories for the batch.")

        # Epoch 2: incorporate fresh specialist experiences into prompts
        if self.epoch_manager.is_epoch2_or_later():
            if any(self.specialist_experience_buffer.values()):
                await self._update_prompts_from_experiences()

    async def _evaluate_with_dynamic_architecture(self, directory: str, params: dict[str, Any]) -> float:
        """Delegate to evaluator."""
        return await self.evaluator.evaluate_with_dynamic_architecture(directory, params)

    async def _update_prompts_from_experiences(self) -> None:
        """Use recent per-specialist experiences to refine prompts (Epoch 2).

        Called from _merge_batch_results after all workers complete, so no
        concurrent writers — no lock needed.
        """
        exp_snapshot: dict[str, list[SpecialistExperience]] = {
            k: v[:] for k, v in self.specialist_experience_buffer.items() if v
        }
        self.specialist_experience_buffer = {k: [] for k in self.specialist_experience_buffer}
        if not exp_snapshot:
            return

        updates: dict[str, str] = {}
        for op_name, exps in exp_snapshot.items():
            if op_name in self.operators:
                continue
            current_prompt = self.operator_pool.get(op_name, {}).get("prompt", "")
            base_template = self.operator_pool.get(op_name, {}).get("base_template", op_name.split("_")[0])
            recent = exps[-5:]
            exp_lines: list[str] = []
            for i, e in enumerate(recent, 1):
                exp_lines.append(
                    f"[{i}] Problem: {e.get('problem', '')}\n"
                    f"Prediction: {e.get('prediction', '')}\n"
                    f"Gold: {e.get('ground_truth', '')}\n"
                    f"Outcome (score): {float(e.get('score', 0.0))}\n"
                )
            exp_text = "\n\n".join(exp_lines)
            judge_prompt = (
                "You are refining a specialist operator prompt using fresh experience trajectories.\n"
                f"Operator: {op_name} (base: {base_template})\n\n"
                f"Current prompt:\n{current_prompt}\n\n"
                f"New experiences (problem, prediction, outcome, gold):\n{exp_text}\n\n"
                "Task: Incorporate these lessons to improve the prompt.\n"
                "- Preserve original sections of the prompt if they can still be applied. "
                "Add new sections for the new experiences if they are sufficiently distinguishable.\n"
                "- Emphasize recurring errors and add actionable heuristics to avoid them.\n"
                "- Keep it concise; remove redundancy; do not add boilerplate.\n"
                "- Output ONLY the updated prompt text (no XML, no markdown fences).\n"
            )
            try:
                llm = self.exec_llm if self.exec_llm else self.llm
                resp = await llm.aask(judge_prompt)
                new_prompt = str(resp or "").strip()
                if new_prompt.startswith("```"):
                    new_prompt = new_prompt.strip("`").strip()
                if new_prompt and len(new_prompt) > 20 and new_prompt != current_prompt:
                    updates[op_name] = new_prompt
            except Exception as e:
                logger.warning(f"Prompt refinement failed for {op_name}: {e}")

        for op_name, new_prompt in updates.items():
            if op_name in self.operator_pool:
                self.operator_pool[op_name]["prompt"] = new_prompt
                with contextlib.suppress(Exception):
                    self.memory_manager.replace_specialist_prompt(op_name, new_prompt)

    async def _pick_best_prompt(self, op_name: str, base_template: str, candidates: list[str]) -> int:
        """Return index of best prompt candidate via LLM judging."""
        if len({(c or "").strip() for c in candidates}) <= 1:
            return 0
        numbered = "\n\n".join([f"[#{i}]\n{p}" for i, p in enumerate(candidates)])
        prompt = (
            "You are comparing specialist operator prompts. Pick the single best candidate index.\n"
            f"Operator: {op_name} (base: {base_template})\n\n"
            f"Candidates:\n{numbered}\n\n"
            'Respond with ONLY valid JSON: {{"winner": k}} where k is 0-based index.\n'
        )
        resp = await self.llm.aask(prompt)
        from aspec.meta.models.architect._variants import LLMJudge

        return LLMJudge(self.llm)._parse_winner_response(resp, len(candidates))
