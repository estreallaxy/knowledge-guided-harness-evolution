from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from aspec.meta.memory.schema import MemorySection as _MemorySection

if TYPE_CHECKING:
    from aspec.meta.optimizer import Optimizer


class EpochManager:
    def __init__(self, optimizer: Optimizer) -> None:
        self.optimizer = optimizer
        self.current_epoch: int = 0

    def is_epoch1(self) -> bool:
        """Check if currently in epoch 1 (exploration phase)."""
        return self.current_epoch == 1

    def is_epoch2_or_later(self) -> bool:
        """Check if in epoch 2 or later (exploitation phase)."""
        return self.current_epoch >= 2

    def is_exploration_phase(self) -> bool:
        """True when specialist creation/mutation is allowed (epoch 1, not test)."""
        return not self.optimizer.is_test and self.is_epoch1()

    def should_freeze_pool(self) -> bool:
        """Determine if operator pool and embeddings should be frozen."""
        return self.optimizer.is_test or self.current_epoch >= 2

    def get_allowed_mutator_actions(self) -> list[str] | None:
        """Get allowed mutator actions based on current epoch."""
        if self.optimizer.is_test or self.is_epoch2_or_later():
            return ["FINALIZE_ARCHITECTURE"]

        if self.is_epoch1():
            return [
                "CREATE_OPERATOR",
                "COMBINE_OPERATORS",
                "PRUNE_OPERATOR",
                "INSPECT_OPERATOR",
                "FINALIZE_ARCHITECTURE",
            ]

        return None

    def set_epoch(self, epoch: int) -> None:
        """Set the current epoch."""
        self.current_epoch = epoch
        logger.info(f"--- STARTING EPOCH {self.current_epoch} ---")

    def log_batch_start(self, batch_idx: int, total_batches: int) -> None:
        logger.info(f"--- Starting Batch {batch_idx + 1}/{total_batches} in Epoch {self.current_epoch} ---")

    async def handle_epoch_transition(self) -> None:
        """Handle transition from epoch 1 to epoch 2."""
        if self.is_exploration_phase():
            await self.optimizer.memory_manager.select_specialists_for_epoch2()
            # After selecting specialists, distill all operator memories for epoch 1
            # Note: We increment epoch first, then call distill with the NEW epoch number
            old_epoch = self.current_epoch
            self.current_epoch += 1  # Move to epoch 2
            logger.info(f"Transitioning from epoch {old_epoch} to epoch {self.current_epoch}")
            await self.distill_memories_for_epoch()
            # Reset architect playbook at epoch boundary to avoid stale patterns
            try:
                from pathlib import Path as _Path

                p = _Path(self.optimizer.root_path) / self.optimizer.mode_dir / "architect_playbook.txt"
                if p.exists():
                    content = p.read_text(encoding="utf-8", errors="ignore")
                    lines = content.splitlines()
                    # keep summary only (up to first appended marker or finalized pattern)
                    cut = len(lines)
                    for i, ln in enumerate(lines):
                        if ("appended:" in ln) or ("Finalized architecture pattern:" in ln):
                            cut = i
                            break
                    kept = "\n".join(lines[:cut]).rstrip() + "\n"
                    p.write_text(kept, encoding="utf-8")
                    logger.info(f"Reset architect playbook entries, kept summary at {p}")
            except OSError as e:
                logger.warning(f"Failed to reset architect playbook: {e}")

    async def distill_memories_for_epoch(self) -> None:
        """Distill memories for all operators in the pool after an epoch."""
        logger.info(f"--- Distilling memories for Epoch {self.current_epoch} ---")
        operator_pool = self.optimizer.operator_pool.keys()
        for op_name in operator_pool:
            await self.optimizer.memory_manager.distill_and_update_memory_for_epoch(op_name, self.current_epoch)

    async def cleanup_and_distill_memories_after_epoch(self) -> None:
        """Cleanup incomplete memory files and distill memories with post-execution reflections after every epoch."""
        logger.info(f"Starting post-epoch cleanup and distillation for Epoch {self.current_epoch}")

        try:
            memory_dir = self.optimizer.memory_manager.memory_dir
            if not memory_dir.exists():
                return

            deleted_count = 0
            distilled_count = 0
            total_files = 0
            deleted_operators = []  # Track operators to remove from pool

            store = self.optimizer.memory_manager.store
            for op_name in store.list_specialists():
                total_files += 1

                try:
                    doc = store.load_document(op_name)
                    if doc is None:
                        continue

                    has_required = doc.has_required_sections()
                    has_post_execution_reflection = bool(doc.get_section(_MemorySection.POST_EXECUTION_REFLECTION))

                    if not has_required:
                        logger.info(f"Deleting incomplete memory file: {op_name}.md (missing required sections)")
                        store.backend.delete(op_name)
                        deleted_count += 1
                        deleted_operators.append(op_name)
                    elif has_post_execution_reflection:
                        # File is complete AND has post-execution reflections - distill it
                        logger.info(f"Distilling memory for specialist with reflections: {op_name}")
                        await self.optimizer.memory_manager.distill_memory_with_reflections(op_name, self.current_epoch)
                        distilled_count += 1

                except Exception as e:
                    logger.warning(f"Failed to process memory file {op_name}: {e}")

            # Remove deleted operators from the in-memory operator pool
            if deleted_operators:
                removed_from_pool = 0
                for op_name in deleted_operators:
                    if op_name in self.optimizer.operator_pool:
                        del self.optimizer.operator_pool[op_name]
                        removed_from_pool += 1
                        logger.info(f"Removed {op_name} from operator pool")

                    # Also remove from operator pool embeddings if present
                    if (
                        hasattr(self.optimizer, "operator_pool_embeddings")
                        and op_name in self.optimizer.operator_pool_embeddings
                    ):
                        del self.optimizer.operator_pool_embeddings[op_name]

                # Update the operator embeddings tensor after removal
                if removed_from_pool > 0 and hasattr(self.optimizer, "operator_pool_embeddings"):
                    try:
                        self.optimizer.operator_embeddings_tensor = self.optimizer._rebuild_embeddings_tensor()
                        logger.info(
                            f"Updated operator embeddings tensor after cleanup ({len(self.optimizer.operator_pool)} operators remaining)"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to update operator embeddings tensor after cleanup: {e}")

                logger.info(f"Removed {removed_from_pool} incomplete operators from in-memory operator pool")

            logger.info(
                f"Post-epoch cleanup complete: Deleted {deleted_count}/{total_files} incomplete files, distilled {distilled_count} specialists with reflections"
            )

            # Sync operator pool with memory files after cleanup (between epochs for stability)
            try:
                from aspec.meta.workflow.utils import WorkflowUtils

                # Prefer current round directory if available to ensure round-specific sync
                log_path = None
                if hasattr(self.optimizer, "evaluator") and hasattr(self.optimizer.evaluator, "_current_round_dir"):
                    log_path = self.optimizer.evaluator._current_round_dir
                if not log_path:
                    log_path = f"{self.optimizer.root_path}/{self.optimizer.mode_dir}"
                WorkflowUtils.sync_operator_pool_with_memory_files(log_path, self.optimizer.operator_pool)
                # Refresh embeddings to include any added/removed specialists
                try:
                    self.optimizer.operator_embeddings_tensor = self.optimizer._get_updated_embeddings()
                    logger.info("Refreshed operator embeddings tensor after pool sync")
                except Exception as e:
                    logger.warning(f"Failed to refresh operator embeddings tensor after pool sync: {e}")
                logger.info("Synced operator pool with specialist memory files after epoch cleanup")
            except Exception as e:
                logger.warning(f"Failed to sync operator pool with memory files after epoch: {e}")

        except Exception as e:
            logger.error(f"Failed to cleanup and distill memories after epoch: {e}")
