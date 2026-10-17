"""Defense effect: relative AHS reduction with paired bootstrap CI.

Posthoc defenses (PromptGuard, LlamaGuard, omni-moderation) re-score each
strategy by zeroing out the AHS for any strategy the defense flags as malicious.
This module compares the no-defense AHS against the defended AHS using a
paired bootstrap to produce a percent-reduction confidence interval.
"""
from __future__ import annotations

from typing import Dict, Iterable, Tuple

import numpy as np

from analysis.metrics.ahs import highest_ahs


def _flagged_by_defense(strategy: Dict, defense_field: str) -> bool:
    res = strategy.get("defense_results") or {}
    block = res.get(defense_field)
    if not isinstance(block, dict):
        return False
    return bool(block.get("detected_malicious"))


def defended_highest_ahs(behavior: Dict, defense_field: str = "promptguard", limit: int = 5) -> float:
    """``highest_ahs`` but skipping any strategy the defense flagged."""
    best = 0.0
    seen = 0
    for s in behavior.get("strategies", []):
        if len(s.get("conversation", [])) == 0:
            continue
        if seen >= limit:
            break
        if _flagged_by_defense(s, defense_field):
            seen += 1
            continue
        score = s.get("agent_harm_score", 0) or 0
        if score > best:
            best = float(score)
        seen += 1
    return best


def paired_bootstrap_relative_reduction(
    no_defense: Iterable[float],
    with_defense: Iterable[float],
    n_iterations: int = 1000,
    seed: int | None = 42,
) -> Tuple[float, Tuple[float, float]]:
    """Return ``(mean_pct, (lower_95, upper_95))`` of percent-reduction in mean score.

    pct = sum(no_defense - defense) / sum(no_defense) * 100, computed per
    bootstrap resample with paired indices.
    """
    nd = np.asarray(list(no_defense), dtype=float)
    wd = np.asarray(list(with_defense), dtype=float)
    if nd.shape != wd.shape:
        raise ValueError("no_defense and with_defense must have the same length")
    if nd.size == 0:
        return 0.0, (0.0, 0.0)
    rng = np.random.default_rng(seed)
    pct_list = []
    for _ in range(n_iterations):
        idx = rng.integers(0, nd.size, size=nd.size)
        nd_s = nd[idx]
        wd_s = wd[idx]
        denom = float(np.sum(nd_s))
        if denom == 0.0:
            continue
        pct_list.append(float(np.sum(nd_s - wd_s) / denom * 100.0))
    if not pct_list:
        return 0.0, (0.0, 0.0)
    arr = np.asarray(pct_list)
    return float(np.mean(arr)), (float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5)))


def compute_defense_effect(
    no_defense_behaviors: Dict,
    defended_behaviors: Dict,
    defense_field: str = "promptguard",
    limit: int = 5,
) -> Dict:
    """Compare AHS before vs after applying ``defense_field`` to the defended behaviors."""
    common_ids = sorted(set(no_defense_behaviors) & set(defended_behaviors))
    nd_scores = [highest_ahs(no_defense_behaviors[bid], limit=limit) for bid in common_ids]
    wd_scores = [defended_highest_ahs(defended_behaviors[bid], defense_field=defense_field, limit=limit) for bid in common_ids]
    mean_pct, ci = paired_bootstrap_relative_reduction(nd_scores, wd_scores)
    return {
        "n_behaviors": len(common_ids),
        "mean_no_defense": float(np.mean(nd_scores)) if nd_scores else 0.0,
        "mean_with_defense": float(np.mean(wd_scores)) if wd_scores else 0.0,
        "relative_reduction_pct": (mean_pct, ci),
    }
