"""
Master-Worker Batch Processing Coordinator

Single master process handles all architecture mutations.
Worker processes only evaluate problems.
"""

from __future__ import annotations

import asyncio
import contextlib
import copy
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from aspec.meta.types import Architecture, ChatHistory, OperatorPool, OperatorSpec

if TYPE_CHECKING:
    from aspec.meta.optimizer import Optimizer

logger = logging.getLogger(__name__)


@dataclass
class MutationRequest:
    """Request for architecture mutation from a worker process."""

    worker_id: int
    problem_idx: int
    query_text: str
    file_context: str = ""
    file_name: str = ""
    file_content: str = ""
    request_id: str = ""


@dataclass
class MutationResponse:
    """Response to mutation request from master process."""

    request_id: str
    new_architecture: Architecture
    mutation_cost: float
    newly_created_operators: dict[str, OperatorSpec]
    pruned_operators: list[str]
    modified_operators: list[str]
    updated_operator_pool: OperatorPool
    success: bool = True
    error: str | None = None


class BatchCoordinator:
    """Coordinates batch processing with master-worker architecture."""

    def __init__(self, optimizer: Optimizer) -> None:
        self.optimizer = optimizer
        self.mutation_queue: asyncio.Queue[MutationRequest] = asyncio.Queue()
        self.response_queues: dict[int, asyncio.Queue[MutationResponse]] = {}
        self.master_task: asyncio.Task[None] | None = None
        self.is_running: bool = False

        self.master_operator_pool: OperatorPool = {}
        self.master_chat_histories: dict[str, ChatHistory] = {}
        self.master_architecture: Architecture = []
        self.master_pruned: list[str] = []

    async def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self.master_task = asyncio.create_task(self._master_loop())

    async def stop(self) -> None:
        if not self.is_running:
            return
        self.is_running = False
        if self.master_task:
            self.master_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.master_task

    async def _master_loop(self) -> None:
        with contextlib.suppress(asyncio.CancelledError):
            while self.is_running:
                try:
                    request = await asyncio.wait_for(self.mutation_queue.get(), timeout=1.0)
                    response = await self._process_mutation_request(request)
                    if request.worker_id in self.response_queues:
                        await self.response_queues[request.worker_id].put(response)
                except TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Master loop error: {e}")
                    await asyncio.sleep(0.1)

    async def _process_mutation_request(self, request: MutationRequest) -> MutationResponse:
        try:
            past_experiences = self._get_past_experiences()
            strategic_principles = self._get_strategic_principles(request.query_text)
            total_problems = getattr(self.optimizer, "total_problems_evaluated", 1)

            (
                new_architecture,
                mutation_cost,
                newly_created_operators,
                pruned_operators,
                modified_operators,
                turn_history,
            ) = await self.optimizer.architecture_mutator.mutate_architecture(
                current_architecture=self.master_architecture.copy(),
                query=request.query_text,
                past_experiences=past_experiences,
                available_operators=self.optimizer.operators,
                operator_pool=self.master_operator_pool,
                log_path=f"{self.optimizer.root_path}/{self.optimizer.mode_dir}/round_{self.optimizer.round}",
                max_specialized_operators=self.optimizer.max_specialized_operators,
                strategic_principles=strategic_principles,
                dataset=self.optimizer.dataset,
                allowed_actions=self.optimizer.epoch_manager.get_allowed_mutator_actions(),
                problem_idx=request.problem_idx,
                total_problems=total_problems,
                current_round=self.optimizer.round,
            )

            self.master_architecture = new_architecture
            self.master_operator_pool.update(newly_created_operators)
            for op_name in pruned_operators:
                self.master_operator_pool.pop(op_name, None)
            self.master_pruned.extend(pruned_operators)

            # Ensure memory files exist for newly created specialists
            if newly_created_operators and hasattr(self.optimizer, "memory_manager"):
                mm = self.optimizer.memory_manager
                for op_name, op_data in newly_created_operators.items():
                    if "_" in op_name:
                        try:
                            mm.record_specialist_creation(op_name, 0.0, op_data.get("prompt", ""))
                            mm.ensure_memory_file(op_name)
                            doc = mm.store.load_document(op_name)
                            prompt = op_data.get("prompt", "")
                            if prompt and (doc is None or not doc.specialist_prompt):
                                mm.append_memory_block(op_name, f"## Specialist Prompt\n{prompt}\n")
                        except Exception as e:
                            logger.error(f"Failed to ensure memory file for {op_name}: {e}")

            return MutationResponse(
                request_id=request.request_id,
                new_architecture=new_architecture,
                mutation_cost=mutation_cost,
                newly_created_operators=newly_created_operators,
                pruned_operators=pruned_operators,
                modified_operators=modified_operators,
                updated_operator_pool=self.master_operator_pool.copy(),
                success=True,
            )

        except Exception as e:
            logger.error(f"Master failed to process mutation: {e}")
            return MutationResponse(
                request_id=request.request_id,
                new_architecture=self.master_architecture,
                mutation_cost=0.0,
                newly_created_operators={},
                pruned_operators=[],
                modified_operators=[],
                updated_operator_pool=self.master_operator_pool.copy(),
                success=False,
                error=str(e),
            )

    async def request_mutation(
        self,
        worker_id: int,
        problem_idx: int,
        query_text: str,
        file_context: str = "",
        file_name: str = "",
        file_content: str = "",
    ) -> MutationResponse:
        """Request a mutation from the master process."""
        if not self.is_running:
            raise RuntimeError("Batch coordinator not running")

        if worker_id not in self.response_queues:
            self.response_queues[worker_id] = asyncio.Queue()

        request_id = f"worker_{worker_id}_problem_{problem_idx}"
        request = MutationRequest(
            worker_id=worker_id,
            problem_idx=problem_idx,
            query_text=query_text,
            file_context=file_context,
            file_name=file_name,
            file_content=file_content,
            request_id=request_id,
        )

        await self.mutation_queue.put(request)

        try:
            while True:
                response = await asyncio.wait_for(self.response_queues[worker_id].get(), timeout=300.0)
                if response.request_id == request_id:
                    return response
                logger.warning(f"Worker {worker_id} discarding stale response {response.request_id}")
        except TimeoutError:
            logger.error(f"Worker {worker_id} mutation request timed out")
            return MutationResponse(
                request_id=request_id,
                new_architecture=self.master_architecture,
                mutation_cost=0.0,
                newly_created_operators={},
                pruned_operators=[],
                modified_operators=[],
                updated_operator_pool=self.master_operator_pool.copy(),
                success=False,
                error="Mutation request timed out",
            )

    def get_current_state_snapshot(self) -> tuple[OperatorPool, dict[str, ChatHistory], Architecture]:
        return (
            copy.deepcopy(self.master_operator_pool),
            copy.deepcopy(self.master_chat_histories),
            self.master_architecture.copy(),
        )

    def initialize_master_state(
        self, operator_pool: OperatorPool, chat_histories: dict[str, ChatHistory], architecture: Architecture
    ) -> None:
        self.master_operator_pool = copy.deepcopy(operator_pool)
        self.master_chat_histories = copy.deepcopy(chat_histories)
        self.master_architecture = architecture.copy()
        self.master_pruned = []

        try:
            if hasattr(self.optimizer, "memory_manager") and self.optimizer.memory_manager:
                from pathlib import Path

                # Use the round-specific directory to avoid writing outside the current round
                round_dir = getattr(getattr(self.optimizer, "evaluator", None), "_current_round_dir", None)
                if round_dir:
                    memory_dir = Path(round_dir) / "specialist_memory"
                else:
                    memory_dir = (
                        Path(self.optimizer.root_path)
                        / self.optimizer.mode_dir
                        / f"round_{self.optimizer.round}"
                        / "specialist_memory"
                    )
                memory_dir.mkdir(parents=True, exist_ok=True)
                self.optimizer.memory_manager.memory_dir = memory_dir
        except OSError as e:
            logger.warning(f"Failed to configure memory directory: {e}")

    def _get_past_experiences(self) -> list[dict[str, Any]]:
        if not hasattr(self.optimizer, "experience_buffer"):
            return []
        past_experiences = []
        for problem_idx, episode_experiences in self.optimizer.experience_buffer.items():
            if episode_experiences:
                latest_exp = episode_experiences[-1]
                past_experiences.append(
                    {
                        "problem_idx": problem_idx,
                        "architecture_before": latest_exp.get("architecture_before", []),
                        "architecture_after": latest_exp.get("architecture", []),
                        "action": latest_exp.get("action_index", 0),
                        "reward": latest_exp.get("reward", 0.0),
                        "cost": latest_exp.get("cost", 0.0),
                        "newly_created_operators": latest_exp.get("newly_created_operators", {}),
                        "modified_operators": latest_exp.get("modified_operators", []),
                        "pruned_operators": latest_exp.get("pruned_operators", []),
                    }
                )
        return past_experiences[-10:] if past_experiences else []

    def _get_strategic_principles(self, query_text: str = "") -> str:
        try:
            if hasattr(self.optimizer, "reflection_manager") and self.optimizer.reflection_manager:
                principles = self.optimizer.reflection_manager.get_strategic_principles(query_text)
                return principles if isinstance(principles, str) else ""
            return ""
        except Exception as e:
            logger.warning(f"Failed to get strategic principles: {e}")
            return ""
