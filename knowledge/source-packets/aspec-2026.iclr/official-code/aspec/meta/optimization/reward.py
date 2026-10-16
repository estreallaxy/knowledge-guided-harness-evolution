from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch

from loguru import logger

if TYPE_CHECKING:
    from aspec.meta.optimizer import Optimizer


class RewardCalculator:
    """REINFORCE reward R_t = s_t - lambda * min(C_t / budget, 1) with per-action baselines.

    Contextual fit (query-architecture similarity) is a policy input feature,
    not a reward weight, so the return stays a pure success/cost tradeoff.
    """

    ENTROPY_BONUS_EPOCH1 = 0.05
    SHARPNESS_PENALTY = 0.05

    def __init__(self, optimizer: Optimizer) -> None:
        self.optimizer = optimizer
        self.lambda_cost: float = optimizer.lambda_cost_penalty
        self.cost_budget: float = optimizer.cost_budget_per_problem
        # Per-action EMA baselines (0 = RETAIN, 1 = RESAMPLE) so the systematic
        # cost difference between actions cancels out of the advantage.
        self._baselines: dict[int, float] = {0: 0.0, 1: 0.0}
        self._baseline_counts: dict[int, int] = {0: 0, 1: 0}
        self._baseline_decay: float = 0.95
        # Running reward std (Welford) for gradient scaling
        self._reward_n: int = 0
        self._reward_mean: float = 0.0
        self._reward_M2: float = 0.0

    def _norm_cost(self, cost: float) -> float:
        """Absolute cost penalty: fraction of the per-problem budget, capped at 1."""
        if self.cost_budget <= 0:
            return 0.0
        return min(cost / self.cost_budget, 1.0)

    def _update_baselines(self, rewards: torch.Tensor, actions: torch.Tensor) -> None:
        for r, a in zip(rewards.tolist(), actions.tolist()):
            a = int(a)
            self._baseline_counts[a] += 1
            if self._baseline_counts[a] == 1:
                self._baselines[a] = r
            else:
                self._baselines[a] = self._baseline_decay * self._baselines[a] + (1 - self._baseline_decay) * r
            self._reward_n += 1
            delta = r - self._reward_mean
            self._reward_mean += delta / self._reward_n
            self._reward_M2 += delta * (r - self._reward_mean)

    def calculate_reward(self, score: float, cost: float, action: int, mutation_cost: float) -> float:
        if self.optimizer.is_test:
            return 0.0

        cost_norm = self._norm_cost(cost + mutation_cost)
        reward = score - self.lambda_cost * cost_norm
        logger.info(
            f"Reward: {reward:.3f} = {score:.3f} - {self.lambda_cost} * cost_norm={cost_norm:.3f} "
            f"(action={'RETAIN' if action == 0 else 'RESAMPLE'})"
        )
        return reward

    def compute_batch_policy_loss(
        self,
        action_log_probs: torch.Tensor,
        scores: list[float],
        exec_costs: list[float],
        mutation_costs: list[float],
        actions: list[int],
    ) -> torch.Tensor:
        device = self.optimizer.device
        s = torch.tensor(scores, dtype=torch.float32, device=device)
        ce = torch.tensor(exec_costs, dtype=torch.float32, device=device)
        cm = torch.tensor(mutation_costs, dtype=torch.float32, device=device)
        a = torch.tensor(actions, dtype=torch.int64, device=device)

        cost_norm = ((ce + cm) / self.cost_budget).clamp(max=1.0) if self.cost_budget > 0 else torch.zeros_like(s)
        rewards = s - self.lambda_cost * cost_norm

        baselines = torch.tensor([self._baselines[int(x)] for x in actions], dtype=torch.float32, device=device)
        advantages = rewards - baselines
        self._update_baselines(rewards, a)

        # Scale by running reward std for gradient stability
        if self._reward_n > 1:
            reward_std = math.sqrt(self._reward_M2 / self._reward_n)
            if reward_std > 1e-8:
                advantages = advantages / reward_std

        policy_loss = -(action_log_probs * advantages.detach()).mean()

        # Entropy schedule: epoch 1 pays a bonus to keep both actions explored
        # while the per-action baselines warm up; later epochs pay a penalty so
        # the policy commits to sharp RETAIN/RESAMPLE probabilities instead of
        # hovering near 0.5.
        # Binary policy: H = -p*log(p) - (1-p)*log(1-p)
        p_selected = action_log_probs.exp()
        p_other = (1.0 - p_selected).clamp(min=1e-8)
        entropy = (-p_selected * action_log_probs - p_other * p_other.log()).mean()
        em = getattr(self.optimizer, "epoch_manager", None)
        entropy_coeff = self.ENTROPY_BONUS_EPOCH1 if em is not None and em.is_epoch1() else -self.SHARPNESS_PENALTY

        loss = policy_loss - entropy_coeff * entropy

        logger.info(
            f"BatchLoss n={s.numel()} reward={rewards.mean().item():.3f} "
            f"baseline_retain={self._baselines[0]:.3f} baseline_resample={self._baselines[1]:.3f} "
            f"adv={advantages.mean().item():.3f} cost_norm={cost_norm.mean().item():.3f} "
            f"retain={int((a == 0).sum().item())} resample={int((a == 1).sum().item())} "
            f"entropy={entropy.item():.3f} entropy_coeff={entropy_coeff:+.2f} loss={loss.item():.4f}"
        )
        return loss
