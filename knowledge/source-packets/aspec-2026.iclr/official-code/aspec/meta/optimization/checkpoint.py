from __future__ import annotations

import contextlib
import json
import os
import time
from typing import TYPE_CHECKING, Any

import torch

from loguru import logger

if TYPE_CHECKING:
    from aspec.meta.optimizer import Optimizer


class CheckpointManager:
    def __init__(self, optimizer: Optimizer) -> None:
        self.optimizer = optimizer
        self.root_path: str = optimizer.root_path
        self.dataset: str = optimizer.dataset
        self.sample: int = optimizer.sample
        self.device = optimizer.device
        self.read_only: bool = False

    def _build_checkpoint_data(self) -> dict[str, Any]:
        return {
            "controller_state_dict": self.optimizer.controller.state_dict(),
            "operator_pool_embeddings": self.optimizer.operator_pool_embeddings,
            "embedding_cache": self.optimizer.embedding_cache,
            "operator_embeddings_tensor": self.optimizer.operator_embeddings_tensor,
        }

    def save_controller_checkpoint(self, problem_count: int) -> None:
        """Save controller weights and operator embeddings as a checkpoint."""
        if self.read_only:
            return
        try:
            if not hasattr(self.optimizer, "controller") or self.optimizer.controller is None:
                return

            checkpoint_dir = f"{self.root_path}/train"
            os.makedirs(checkpoint_dir, exist_ok=True)
            rep = getattr(self.optimizer, "current_epoch", 0)
            checkpoint_path = os.path.join(
                checkpoint_dir,
                f"{self.dataset}_controller_sample{self.sample}_rep{rep}_problem{problem_count}.pth",
            )

            checkpoint_data = self._build_checkpoint_data()
            torch.save(checkpoint_data, checkpoint_path)

        except Exception as e:
            logger.error(f"Failed to save controller checkpoint: {e}")

    def save_best_score_checkpoint(self, score: float, problem_count: int) -> None:
        """Save controller weights and operator embeddings with score metadata when a new best score is achieved."""
        if self.read_only:
            return
        try:
            checkpoint_dir = f"{self.root_path}/train"
            os.makedirs(checkpoint_dir, exist_ok=True)
            rep = getattr(self.optimizer, "current_epoch", 0)
            checkpoint_path = os.path.join(
                checkpoint_dir,
                f"{self.dataset}_controller_sample{self.sample}_best.pth",
            )

            metadata_path = os.path.join(
                checkpoint_dir, f"{self.dataset}_controller_sample{self.sample}_best_score_metadata.json"
            )
            if os.path.exists(metadata_path):
                with contextlib.suppress(OSError, json.JSONDecodeError, ValueError, TypeError):
                    with open(metadata_path) as f:
                        if float(json.load(f).get("best_score", 0.0)) >= score:
                            return

            checkpoint_data = self._build_checkpoint_data()
            torch.save(checkpoint_data, checkpoint_path)

            metadata = {
                "best_score": score,
                "problem_count": problem_count,
                "checkpoint_path": checkpoint_path,
                "dataset": self.dataset,
                "sample": self.sample,
                "rep": rep,
                "timestamp": time.time(),
            }

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            self.optimizer.best_score_checkpoint_path = checkpoint_path

        except Exception as e:
            logger.error(f"Failed to save best score checkpoint: {e}")

    def get_best_score_checkpoint_path(self) -> str | None:
        """Get the path to the best performing checkpoint."""
        if self.optimizer.best_score_checkpoint_path:
            return self.optimizer.best_score_checkpoint_path

        try:
            metadata_path = os.path.join(
                f"{self.root_path}/train", f"{self.dataset}_controller_sample{self.sample}_best_score_metadata.json"
            )

            if os.path.exists(metadata_path):
                with open(metadata_path) as f:
                    metadata = json.load(f)

                checkpoint_path = metadata.get("checkpoint_path")
                if checkpoint_path and os.path.exists(checkpoint_path):
                    self.optimizer.best_score_checkpoint_path = checkpoint_path
                    logger.info(f"Found best score checkpoint from metadata: {checkpoint_path}")
                    return checkpoint_path

        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load best score metadata: {e}")

        return None
