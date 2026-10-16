from __future__ import annotations

import os
import re
import traceback
from pathlib import Path
from typing import Any, Literal

import torch
from pydantic import BaseModel, Field

from aspec.controller.utils import get_sentence_embedding
from loguru import logger
from aspec.llm import LLMConfig, create_llm_instance
from aspec.meta.models.architect import LLMArchitectureMutator
from aspec.meta.models.controller import MetaController
from aspec.meta.models.encoder import ArchitectureEncoder, OperatorEmbedder
from aspec.meta.specialist import create_specialist_prompt, extract_specialist_knowledge_from_memory
from aspec.meta.types import Architecture, Experience, OperatorPool, OperatorSpec
from aspec.meta.utils import (
    get_specialized_prompts_file_path,
    load_all_operator_prompts,
    load_specialized_prompts_from_memory,
)

DatasetType = Literal["HumanEval", "MATH", "SciCode"]
QuestionType = Literal["math", "code", "qa"]
OptimizerType = Literal["Graph"]


class GraphOptimize(BaseModel):
    modification: str = Field(default="", description="modification")
    graph: str = Field(default="", description="graph")
    prompt: str = Field(default="", description="prompt")


class CoreOptimizer:
    def __init__(
        self,
        dataset: DatasetType,
        question_type: QuestionType,
        opt_llm_config: LLMConfig,
        exec_llm_config: LLMConfig,
        operators: list[str],
        sample: int,
        optimized_path: str | None = None,
        round: int = 1,
        batch_size: int = 4,
        lr: float = 1e-3,
        lambda_cost_penalty: float = 0.3,
        cost_budget_per_problem: float = 0.05,
        sliding_window_k: int = 5,
        device: torch.device | None = None,
        max_specialized_operators: int = 5,
        is_test: bool = False,
        preloaded_weights_path: str | None = None,
        dataset_split: str = "train",
    ) -> None:
        self.optimize_llm_config: LLMConfig = opt_llm_config
        self.execute_llm_config: LLMConfig = exec_llm_config
        self.dataset: DatasetType = dataset
        self.sliding_window_k = sliding_window_k
        self.lambda_cost_penalty = lambda_cost_penalty
        self.cost_budget_per_problem = cost_budget_per_problem
        self.type: QuestionType = question_type
        self.operators = operators

        self.optimized_path: str | None = optimized_path
        self.root_path: str = f"{optimized_path}/{self.dataset}"
        self.mode_dir: str = "test" if is_test else "train"
        self.dataset_split: str = dataset_split if dataset_split in ["train", "test"] else "train"
        self.max_specialized_operators = max_specialized_operators

        self.specialized_operator_age = {}
        self.operator_cooldown_period: int = 3
        self.creation_action_points_max: int = 3
        self.creation_action_points_current: int = self.creation_action_points_max
        self.current_batch_created_operators: set[str] = set()

        self.is_test = is_test
        self.preloaded_weights_path: str | None = preloaded_weights_path
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device

        self.operator_prompts: dict[str, str] = load_all_operator_prompts(f"{self.root_path}/{self.mode_dir}/")

        self.sample = sample
        self.round = round
        self.batch_size = batch_size
        self.lr = lr
        self.device: torch.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._graph_root_path: str = self.root_path

        self.operator_pool: OperatorPool = {}

        self.embedding_cache: dict[str, torch.Tensor] = {}

        specialized_prompts_file = get_specialized_prompts_file_path(f"{self.root_path}/{self.mode_dir}/")

        if not self.is_test:
            if os.path.exists(specialized_prompts_file):
                try:
                    with open(specialized_prompts_file, encoding="utf-8") as f:
                        f.read()

                    os.remove(specialized_prompts_file)
                    logger.info(f"Cleared existing specialized prompts file: {specialized_prompts_file}")
                except OSError as e:
                    logger.warning(f"Failed to clear specialized prompts file: {e}")
        else:
            logger.info(
                f"Test mode: preserving existing specialized prompts file if present: {specialized_prompts_file}"
            )

        # Prefer loading specialists from memory .md files in test mode
        root = Path(self.root_path)
        base_dir = root / ("train" if self.is_test else (self.mode_dir or "train"))
        # In test, prefer the explicitly requested train round to avoid leaking newest round
        if self.is_test:
            specific_round_dir = base_dir / f"round_{self.round}"
            mem_dir_path = specific_round_dir / "specialist_memory"
        else:
            # TRAIN MODE: Prefer the explicitly requested round
            mem_dir_path = None
            if base_dir.name == "train" and base_dir.exists():
                if isinstance(self.round, int) and self.round > 0:
                    specific_round_dir = base_dir / f"round_{self.round}" / "specialist_memory"
                    if specific_round_dir.exists():
                        mem_dir_path = specific_round_dir
        if mem_dir_path:
            specialized_prompts = load_specialized_prompts_from_memory(str(mem_dir_path))
            logger.info(f"Loaded {len(specialized_prompts)} specialized prompts from {mem_dir_path}")
        else:
            specialized_prompts = {}

        for op_name in self.operators:
            # Base operators need their prompt from the _PROMPT keys (e.g., COT_PROMPT)
            base_prompt = self.operator_prompts.get(f"{op_name.upper()}_PROMPT", "")
            if not base_prompt:
                base_prompt = self.operator_prompts.get(op_name, "")

            self.operator_pool[op_name] = {
                "base_template": op_name,
                "prompt": base_prompt,
            }

        def _sanitize_prompt_text(_s: str) -> str:
            if not isinstance(_s, str):
                return str(_s)
            m = re.search(r"(?mi)^\s*Variant\s+\d+\s*:", _s)
            if m:
                _s = _s[: m.start()].rstrip()
            _s = re.sub(r"(?mi)^\s*Variant\s+\d+\s*:.*$", "", _s)
            return _s.strip()

        for op_name, op_data in specialized_prompts.items():
            base_template_name = op_data.get("base_template")
            if not base_template_name:
                base_template_name = str(op_name).split("_")[0]
                logger.info(f"Inferred base_template '{base_template_name}' for specialized operator '{op_name}'")

            # Use specialist memory files as single source of truth
            composed_prompt, specialist_data = self._reconstruct_specialist_prompt(op_name, op_data, base_template_name)
            mode_label = "Test" if self.is_test else "Training"
            if composed_prompt != op_data.get("prompt", ""):
                logger.info(f"{mode_label} mode: Generated complete prompt for '{op_name}' from memory")
            else:
                logger.warning(f"{mode_label} mode: No base template found for '{op_name}', using raw memory")

            self.operator_pool[op_name] = {
                "base_template": base_template_name,
                "prompt": _sanitize_prompt_text(composed_prompt),
                "specialist_data": specialist_data if isinstance(specialist_data, dict) else {},
            }

        logger.info(f"Initialized operator pool with {len(self.operator_pool)} operators")

        logger.info("Creating MetaController")
        self.controller = MetaController(input_dim=384, arch_dim=384, hidden_dim=128, device=self.device)

        if self.preloaded_weights_path and not os.path.exists(self.preloaded_weights_path):
            logger.warning(f"Preloaded weights not found, starting from random init: {self.preloaded_weights_path}")
        if self.preloaded_weights_path and os.path.exists(self.preloaded_weights_path):
            logger.info(f"Loading preloaded weights from: {self.preloaded_weights_path}")
            try:
                checkpoint = torch.load(self.preloaded_weights_path, map_location=self.device)
                if "controller_state_dict" in checkpoint:
                    self.controller.load_state_dict(checkpoint["controller_state_dict"])
                    logger.info("Successfully loaded controller weights from checkpoint")
                else:
                    self.controller.load_state_dict(checkpoint)
                    logger.info("Successfully loaded controller weights directly")

                if self.is_test:
                    self.controller.eval()
                else:
                    self.controller.train()

            except Exception as e:
                logger.error(f"Failed to load preloaded weights: {e}")
                logger.info("Continuing with randomly initialized controller")

        if self.is_test:
            self.controller.eval()

        self.operator_embedder = OperatorEmbedder(self.operator_pool, self.operator_pool)
        self.encoder = ArchitectureEncoder(
            operator_embedder=self.operator_embedder,
            output_dim=384,
        )

        self.llm = create_llm_instance(opt_llm_config)
        self.exec_llm = create_llm_instance(exec_llm_config)

        from aspec.llm import CostManager

        shared_cost_manager = CostManager()

        self.llm.cost_manager = shared_cost_manager
        self.exec_llm.cost_manager = shared_cost_manager

        self.architecture_mutator = LLMArchitectureMutator(self.llm)

        self.torch_optimizer = torch.optim.Adam(self.controller.parameters(), lr=self.lr, weight_decay=1e-5)

        self.experience_buffer: dict[int, list[Experience]] = {}
        self.past_queries: list[str] = []

        if self.dataset == "SciCode":
            self.current_architecture: Architecture = [["CoT"]]

        self.best_score_so_far: float = 0.0
        self.best_score_checkpoint_path: str | None = None

        self.operator_pool_embeddings: dict[str, torch.Tensor] = {}
        for op_name in self.operator_pool:
            full_text = self._get_operator_full_text(op_name)
            self.operator_pool_embeddings[op_name] = self._get_embedding_with_cache(full_text)

        self.operator_embeddings_tensor: torch.Tensor = self._get_updated_embeddings()

        self.graph = self._load_graph(f"{self.root_path}/{self.mode_dir}")

    def _reconstruct_specialist_prompt(
        self, op_name: str, op_data: dict[str, Any], base_template_name: str
    ) -> tuple[str, dict[str, Any]]:
        """Reconstruct a specialist prompt from memory data and a base template.

        Returns (composed_prompt, specialist_data).
        """
        memory_text = op_data.get("prompt", "")

        # Resolve the base prompt template
        base_prompt_template = self.operator_prompts.get(base_template_name)
        if not base_prompt_template:
            base_prompt_template = self._resolve_base_prompt_template(base_template_name)

        try:
            specialist_data = extract_specialist_knowledge_from_memory(memory_text)
            if base_prompt_template:
                composed_prompt = create_specialist_prompt(base_prompt_template, specialist_data)
            else:
                composed_prompt = memory_text
        except Exception as e:
            logger.warning(f"Failed to reconstruct complete prompt for '{op_name}': {e}")
            try:
                specialist_data = extract_specialist_knowledge_from_memory(memory_text)
            except Exception as e2:
                logger.warning(f"Failed to re-extract specialist knowledge for '{op_name}': {e2}")
                specialist_data = {}
            composed_prompt = memory_text

        return composed_prompt, specialist_data if isinstance(specialist_data, dict) else {}

    def _resolve_base_prompt_template(self, base_template_name: str) -> str | None:
        mapping = {
            "ReAct": "REACT_PROMPT",
            "CoT": "COT_PROMPT",
            "Debate": "DEBATE_PROMPT",
            "SelfConsistency": "SELFCONSISTENCY_PROMPT",
            "SelfRefine": "SELFREFINE_PROMPT",
            "Ensemble": "ENSEMBLE_MEMBER_PROMPT",
            "Testing": "TESTING_PROMPT",
            "EarlyExit": "EARLYEXIT_PROMPT",
        }
        key = mapping.get(base_template_name)
        if key and key in self.operator_prompts:
            return self.operator_prompts[key]
        # fallback: UPPER + _PROMPT
        fallback_key = f"{base_template_name.upper()}_PROMPT"
        return self.operator_prompts.get(fallback_key)

    async def optimize(self, mode: OptimizerType = "Graph") -> float:
        try:
            score = await self._optimize_graph()
        except Exception as e:
            logger.exception(f"Error occurred during optimization: {e}")
            score = 0.0

        score = 0.0 if score is None else float(score)
        logger.info(f"Optimization completed. Score for round {self.round}: {score}")
        return score

    async def _optimize_graph(self) -> float:
        graph_path = f"{self.root_path}/{self.mode_dir}"

        directory = self._create_round_directory(graph_path, self.round)

        params: dict[str, Any] = {
            "operator_embeddings": self.operator_embeddings_tensor,
            "controller": self.controller,
            "execute_llm_config": self.execute_llm_config,
            "dataset": self.dataset,
            "optimizer": self.torch_optimizer,
            "sample": self.sample,
            "is_textgrad": True,
        }

        avg_score = await self._evaluate_with_dynamic_architecture(directory, params)
        logger.info(f"Average score for this round: {avg_score}")

        return avg_score

    def _get_operator_full_text(self, operator_name: str) -> str:
        """Get the full text for an operator for embedding."""
        op_data = self.operator_pool.get(operator_name, {})
        base_template = op_data.get("base_template", operator_name)
        prompt = op_data.get("prompt", "")

        return f"Operator: {operator_name}. Base: {base_template}. {prompt[:200]}"

    def _get_embedding_with_cache(self, text: str) -> torch.Tensor:
        """Gets a sentence embedding, using a cache to avoid re-computation."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        embedding = get_sentence_embedding(text).to(self.device)
        self.embedding_cache[text] = embedding
        return embedding

    def _rebuild_embeddings_tensor(self) -> torch.Tensor:
        """Rebuild the stacked embeddings tensor from operator_pool_embeddings.

        Uses a deterministic order: base operators first, then sorted specialists.
        Falls back to base-only if the full set is empty.
        """
        base_order = list(self.operators)
        extras = sorted([n for n in self.operator_pool if n not in base_order])
        stacked_order = base_order + extras
        embeddings = [
            self.operator_pool_embeddings[name] for name in stacked_order if name in self.operator_pool_embeddings
        ]
        if not embeddings:
            # Fallback to base operators only
            embeddings = [
                self.operator_pool_embeddings[name] for name in base_order if name in self.operator_pool_embeddings
            ]
        if embeddings:
            return torch.stack(embeddings).to(self.device)
        return torch.zeros(1, 384, device=self.device)

    def _get_updated_embeddings(self) -> torch.Tensor:
        """Create/refresh the stacked embeddings tensor while avoiding recomputation for existing operators."""
        if not hasattr(self, "operator_pool_embeddings") or self.operator_pool_embeddings is None:
            self.operator_pool_embeddings = {}
        for op_name in self.operator_pool:
            if op_name not in self.operator_pool_embeddings:
                full_text = self._get_operator_full_text(op_name)
                self.operator_pool_embeddings[op_name] = self._get_embedding_with_cache(full_text)
        return self._rebuild_embeddings_tensor()

    def _get_round_memory_dir(self) -> Path | None:
        base = Path(self.root_path) / (self.mode_dir or "train")
        rnd = getattr(self, "round", None)
        if isinstance(rnd, int) and rnd > 0:
            return base / f"round_{rnd}" / "specialist_memory"
        return None

    def _enforce_pool_disk_parity(self, pool: OperatorPool | None = None, mem_dir: Path | None = None) -> None:
        if mem_dir is None:
            mem_dir = self._get_round_memory_dir()
        if isinstance(mem_dir, str):
            mem_dir = Path(mem_dir)
        if not mem_dir or not mem_dir.exists():
            return
        active_pool = pool if isinstance(pool, dict) else self.operator_pool
        pool_specialists = {name for name in active_pool if "_" in name}
        for p in mem_dir.glob("*.md"):
            name = p.stem
            if "_" not in name or name in pool_specialists:
                continue
            try:
                p.unlink(missing_ok=True)
                logger.info(f"[POOL->DISK PARITY] Removed stray specialist file: {p}")
            except OSError as e:
                logger.warning(f"[POOL->DISK PARITY] Failed to remove {p}: {e}")
            # Also remove backups
            bdir = mem_dir / "backups"
            if bdir.exists():
                for bp in bdir.glob(f"{name}_*.md"):
                    try:
                        bp.unlink(missing_ok=True)
                        logger.info(f"[POOL->DISK PARITY] Removed backup: {bp}")
                    except OSError as e:
                        logger.warning(f"[POOL->DISK PARITY] Failed to remove backup {bp}: {e}")

    def _get_architecture_embedding(
        self,
        architecture: Architecture | None = None,
        operator_pool: OperatorPool | None = None,
        query_embedding: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """
        Get the embedding for a given architecture, optionally conditioned on a query.
        If operator_pool is not provided, uses the optimizer's main pool.
        If query_embedding is provided, uses attention-weighted combination for better signal preservation.
        """
        pool_to_use = operator_pool if operator_pool is not None else self.operator_pool
        arch_to_use = architecture if architecture is not None else getattr(self, "current_architecture", None)
        if arch_to_use is None or not any(arch_to_use):
            arch_to_use = [["CoT"]]
        # Use a fresh embedder without the shared cache to ensure identities are reflected in architecture embeddings
        mem_dir = self._get_round_memory_dir()

        # Get base operator definitions
        op_embedder = OperatorEmbedder(
            base_op_definitions={},
            specialist_pool=pool_to_use,
            cache=None,
            memory_dir=str(mem_dir) if mem_dir else None,
        )
        arch_encoder = ArchitectureEncoder(operator_embedder=op_embedder)

        # Use query-aware encoding with high temperature for sharp attention
        arch_embedding = arch_encoder.encode(arch_to_use, query_embedding=query_embedding, temperature=20.0)
        return arch_embedding.to(self.device)

    def _get_pool_embeddings_and_mask(
        self,
        architecture: Architecture | None = None,
        operator_pool: OperatorPool | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Compute operator pool embeddings and boolean mask for ops in current architecture.
        Returns (pool_embeddings [N, D], in_arch_mask [N]).
        """
        pool = operator_pool if operator_pool is not None else getattr(self, "operator_pool", {})
        # Resolve target architecture for mask
        arch_struct = architecture if architecture is not None else getattr(self, "current_architecture", None)
        if arch_struct is None or not any(arch_struct):
            arch_struct = [["CoT"]]

        # Prepare embedder
        mem_dir = self._get_round_memory_dir()
        op_embedder = OperatorEmbedder(
            base_op_definitions={},
            specialist_pool=pool,
            cache=None,
            memory_dir=str(mem_dir) if mem_dir else None,
        )

        op_names: list[str] = list(pool.keys())
        embeddings: list[torch.Tensor] = []
        for name in op_names:
            try:
                emb = op_embedder.get_embedding(name)
            except Exception as e:
                logger.warning(f"Failed to get embedding for operator '{name}': {e}")
                emb = torch.zeros(384, dtype=torch.float32)  # default dim
            embeddings.append(emb)
        pool_embeddings = torch.stack(embeddings, dim=0).to(self.device)

        # Build mask
        in_arch: set[str] = set()
        for layer in arch_struct:
            for op in layer:
                in_arch.add(op)
        mask_list = [name in in_arch for name in op_names]
        in_arch_mask = torch.tensor(mask_list, dtype=torch.bool, device=self.device)
        return pool_embeddings, in_arch_mask

    def _get_action(
        self, arch_embedding: torch.Tensor, query_embedding: torch.Tensor, similarity: float = 0.0
    ) -> tuple[int, torch.Tensor, torch.Tensor]:
        """Return (action:int, log_prob:Tensor, logits:Tensor) for compatibility with evaluator."""
        self.controller.eval()
        with torch.no_grad():
            probs, log_probs, logits = self.controller.forward(query_embedding, arch_embedding, similarity)
            if self.is_test:
                action = int(probs.argmax(dim=-1).item())
            else:
                action = int(torch.distributions.Categorical(probs).sample().item())
            action_log_prob = log_probs[0, action]
        return action, action_log_prob, logits

    async def _update_policy(self) -> None:
        """Batch REINFORCE update with batch-wise utilities via RewardCalculator.
        Works for both CoreOptimizer and subclasses; no-op in test mode.
        """

        # Extract and clear buffer atomically
        async def _swap_buffer() -> dict[int, list[Experience]] | None:
            total = sum(len(v) for v in self.experience_buffer.values())
            if total < self.batch_size:
                return None
            buf = self.experience_buffer
            self.experience_buffer = {}
            return buf

        if hasattr(self, "_exp_buffer_lock"):
            async with self._exp_buffer_lock:
                buffer_to_process = await _swap_buffer()
        else:
            buffer_to_process = await _swap_buffer()

        if not buffer_to_process:
            return

        # Never train in test mode
        if self.is_test:
            return

        # Guard: need controller and torch optimizer
        if self.controller is None or self.torch_optimizer is None:
            return

        # Build batch tensors and log-probs
        all_log_probs: list[torch.Tensor] = []
        batch_scores: list[float] = []
        batch_exec_costs: list[float] = []
        batch_mutation_costs: list[float] = []
        batch_actions: list[int] = []

        for episode_experiences in buffer_to_process.values():
            if not episode_experiences:
                continue
            for exp in episode_experiences:
                try:
                    q = exp.get("query_embedding")
                    if q is None:
                        q = get_sentence_embedding(exp.get("query", "")).to(self.device)
                    else:
                        q = q.to(self.device)
                    a = exp.get("arch_embedding")
                    if a is None:
                        arch = exp.get("architecture", getattr(self, "current_architecture", [["CoT"]]))
                        a = self._get_architecture_embedding(arch)
                    else:
                        a = a.to(self.device)
                    similarity = float(exp.get("similarity", 0.0))
                    probs, log_probs, _ = self.controller.forward(q, a, similarity)
                    action_index = int(exp.get("action_index", exp.get("action", 0)))
                    all_log_probs.append(log_probs[0, action_index])
                except Exception as e:
                    logger.warning(f"Failed to compute log-prob for experience: {e}")
                    all_log_probs.append(torch.tensor(0.0, device=self.device))

                batch_scores.append(float(exp.get("score", 0.0)))
                batch_exec_costs.append(float(exp.get("cost", 0.0) or 0.0))
                batch_mutation_costs.append(float(exp.get("mutation_cost", 0.0) or 0.0))
                batch_actions.append(int(exp.get("action_index", exp.get("action", 0))))

        if not all_log_probs:
            return

        action_log_probs = torch.stack(all_log_probs)

        # Compute policy loss via RewardCalculator
        rc = getattr(self, "reward_calculator", None)
        if rc is None:
            from aspec.meta.optimization.reward import RewardCalculator

            self.reward_calculator = RewardCalculator(self)
            rc = self.reward_calculator
        try:
            policy_loss = rc.compute_batch_policy_loss(
                action_log_probs=action_log_probs,
                scores=batch_scores,
                exec_costs=batch_exec_costs,
                mutation_costs=batch_mutation_costs,
                actions=batch_actions,
            )
        except Exception as e:
            logger.error(f"RewardCalculator failure: {e}")
            logger.error(traceback.format_exc())
            raise

        # Optimize
        self.controller.train()
        self.torch_optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.controller.parameters(), max_norm=1.0)
        self.torch_optimizer.step()

        # Reset batch-scoped state
        self.creation_action_points_current = self.creation_action_points_max
        self.current_batch_created_operators.clear()
        if hasattr(self, "window_events"):
            self.window_events = []

    async def _mutate_architecture_with_llm(
        self,
        query_text: str,
        file_context: str = "",
        file_name: str = "",
        file_content: str = "",
        with_background: bool = False,
        operator_pool: OperatorPool | None = None,
        current_architecture: Architecture | None = None,
        problem_idx: int = 0,
        total_problems: int = 0,
        round_directory: str = "",
    ) -> tuple[Architecture, float, dict[str, OperatorSpec], list[str], list[str], list[dict[str, Any]], OperatorPool]:
        """Fallback mutator for base Optimizer to match evaluator expectations."""
        past_experiences: list[dict[str, Any]] = []
        strategic_principles = ""
        max_specs = self.max_specialized_operators
        pool = operator_pool if operator_pool is not None else self.operator_pool
        arch = (
            current_architecture
            if current_architecture is not None
            else getattr(self, "current_architecture", [["CoT"]])
        )

        log_path_for_mutator = round_directory or f"{self.root_path}/{self.mode_dir}/round_{self.round}"

        # Enforce epoch/test freeze policy for mutator actions
        allowed_actions_for_epoch = self.epoch_manager.get_allowed_mutator_actions()
        (
            new_architecture,
            mutation_cost,
            newly_created_operators,
            pruned_operators,
            modified_operators,
            turn_history,
        ) = await self.architecture_mutator.mutate_architecture(
            current_architecture=arch,
            query=query_text,
            past_experiences=past_experiences,
            available_operators=self.operators,
            operator_pool=pool,
            log_path=log_path_for_mutator,
            max_specialized_operators=max_specs,
            strategic_principles=strategic_principles,
            dataset=self.dataset,
            allowed_actions=allowed_actions_for_epoch,
            problem_idx=problem_idx,
            total_problems=total_problems,
        )
        # Synchronize global operator pool with mutator updates to avoid stale counts
        self.operator_pool = pool
        # Prune chat histories for removed operators
        if pruned_operators:
            for _p in pruned_operators:
                if hasattr(self, "memory_manager") and self.memory_manager:
                    self.memory_manager.prune_specialist_history(_p)
        return (
            new_architecture,
            mutation_cost,
            newly_created_operators,
            pruned_operators,
            modified_operators,
            turn_history,
            pool,
        )

    @staticmethod
    def _create_round_directory(graph_path: str, round_number: int) -> str:
        directory = os.path.join(graph_path, f"round_{round_number}")
        os.makedirs(directory, exist_ok=True)
        return directory

    @staticmethod
    def _load_graph(workflows_path: str) -> type[Any]:
        workflows_path = workflows_path.replace("\\", ".").replace("/", ".")
        graph_module_name = f"{workflows_path}.graph"
        try:
            graph_module = __import__(graph_module_name, fromlist=[""])
            return graph_module.Workflow
        except ImportError as e:
            logger.info(f"Error loading graph: {e}")
            raise

