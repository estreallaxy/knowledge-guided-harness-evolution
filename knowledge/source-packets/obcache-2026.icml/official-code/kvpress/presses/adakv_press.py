# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass

import torch

from kvpress.presses.base_press import BasePress
from kvpress.presses.scorer_press import ScorerPress


def masked_indices_from_adakv_scores(
    scores: torch.Tensor,
    compression_ratio: float,
    alpha_safeguard: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Compute the `(batch, head, seq)` indices that AdaKV should mask.
    """
    bsz, num_key_value_heads, k_len = scores.shape

    # Make sure to keep at least alpha * (1 - compression_ratio) KV pairs per head.
    n_kept = int(k_len * (1 - compression_ratio))
    n_safe = int(n_kept * alpha_safeguard)
    if n_safe > 0:
        top_indices = torch.topk(scores, n_safe, dim=-1).indices
        scores = scores.clone()
        scores.scatter_(-1, top_indices, torch.finfo(scores.dtype).max)

    # Compute bottom-k across heads.
    n_pruned = num_key_value_heads * (k_len - n_kept)
    if n_pruned == 0:
        empty = torch.empty(0, dtype=torch.long, device=scores.device)
        return empty, empty, empty

    indices = torch.topk(-scores.reshape(bsz, -1), n_pruned, dim=1).indices.flatten()
    batch_indices = torch.arange(bsz, device=scores.device).repeat_interleave(n_pruned)
    head_indices = indices // k_len
    seq_indices = indices % k_len
    return batch_indices, head_indices, seq_indices


@dataclass
class AdaKVPress(BasePress):
    """
    AdaKV: Adaptive head-wise KV cache compression.

    Performs head-specific compression by selecting top-k tokens across all heads
    based on importance scores. Applies safeguards to ensure each head retains
    a minimum fraction of tokens.

    Based on AdaKV (https://arxiv.org/abs/2407.11550).

    Parameters
    ----------
    press : ScorerPress
        AdaKVPress and ObservedAttention are currently not supported.
    alpha_safeguard : float, default=0.20
        Minimum fraction of KV pairs that each head must retain.
        Ensures no attention head is compressed too aggressively. Even if tokens
        receive low global importance scores, each head retains at least this
        fraction of its original tokens.
    """

    press: ScorerPress
    alpha_safeguard: float = 0.20

    def __post_init__(self):
        assert isinstance(self.press, ScorerPress), "AdaKVPress requires a ScorerPress as input"
        assert 0 <= self.alpha_safeguard <= 1, "alpha_safeguard should be in [0, 1]"

    def post_init_from_model(self, model):
        self.press.post_init_from_model(model)

    @property
    def compression_ratio(self):
        return self.press.compression_ratio

    @compression_ratio.setter
    def compression_ratio(self, value):
        self.press.compression_ratio = value

    def compress(self, module, hidden_states, keys, values, attentions, kwargs):
        if self.compression_ratio == 0:
            return keys, values

        assert module.config._attn_implementation != "eager", "eager mode not supported"

        # Compute scores
        scores = self.press.score(module, hidden_states, keys, values, attentions, kwargs)
        module.masked_key_indices = masked_indices_from_adakv_scores(
            scores=scores,
            compression_ratio=self.compression_ratio,
            alpha_safeguard=self.alpha_safeguard,
        )
        return keys, values
