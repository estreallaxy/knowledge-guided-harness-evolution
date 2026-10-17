import math
from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F
from transformers.models.llama.modeling_llama import repeat_kv, rotate_half

from kvpress.presses.obcache_scorer import triton_is_available, triton_v_score
from kvpress.presses.scorer_press import ScorerPress
from kvpress.utils import get_prerope_query_states


class OBCacheScoringMixin:
    pruning_score: str
    use_triton: bool
    gqa_aggregation: str
    kernel_size: int

    @staticmethod
    def compute_causal_attention(
        module: nn.Module,
        hidden_states: torch.Tensor,
        keys: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        query_start: int = 0,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        _, _, key_length, _ = keys.shape
        query_states = get_prerope_query_states(module, hidden_states[:, query_start:])
        query_length = query_states.shape[2]

        num_heads = module.config.num_attention_heads
        num_key_value_groups = num_heads // module.config.num_key_value_heads

        cos, sin = position_embeddings
        cos = cos[:, query_start : query_start + query_length]
        sin = sin[:, query_start : query_start + query_length]
        query_states = (query_states * cos.unsqueeze(1)) + (
            rotate_half(query_states) * sin.unsqueeze(1)
        )

        key_states = repeat_kv(keys, num_key_value_groups)
        logits = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(
            module.head_dim
        )

        query_positions = torch.arange(
            query_start, query_start + query_length, device=keys.device
        )
        key_positions = torch.arange(key_length, device=keys.device)
        causal_mask = key_positions.unsqueeze(0) > query_positions.unsqueeze(1)
        logits = logits.masked_fill(
            causal_mask.unsqueeze(0).unsqueeze(0), float("-inf")
        )
        attention = nn.functional.softmax(logits, dim=-1, dtype=torch.float32).to(
            query_states.dtype
        )
        return attention, logits.detach()

    def can_use_triton(
        self,
        attention: torch.Tensor,
        values: torch.Tensor,
    ) -> bool:
        if not self.use_triton or self.pruning_score != "obcache-v":
            return False
        if not triton_is_available() or not attention.is_cuda or not values.is_cuda:
            return False
        valid_dtypes = (torch.float16, torch.bfloat16)
        return attention.dtype in valid_dtypes and values.dtype in valid_dtypes

    @staticmethod
    def reduce_gqa_tensor(
        tensor: torch.Tensor,
        num_key_value_heads: int,
        num_key_value_groups: int,
    ) -> torch.Tensor:
        batch_size = tensor.shape[0]
        tail_shape = tensor.shape[2:]
        return tensor.view(
            batch_size, num_key_value_heads, num_key_value_groups, *tail_shape
        ).mean(dim=2)

    @staticmethod
    def reduce_gqa_scores(
        scores: torch.Tensor,
        num_key_value_heads: int,
        num_key_value_groups: int,
        reduction: str,
        normalize: bool = False,
    ) -> torch.Tensor:
        batch_size, _, key_length = scores.shape
        grouped_scores = scores.view(
            batch_size, num_key_value_heads, num_key_value_groups, key_length
        )
        if normalize:
            grouped_scores = grouped_scores.float()
            mean = grouped_scores.mean(dim=-1, keepdim=True)
            var = grouped_scores.var(dim=-1, keepdim=True, unbiased=False)
            grouped_scores = (grouped_scores - mean) / torch.sqrt(var + 1e-6)
        if reduction == "mean":
            return grouped_scores.mean(dim=2)
        if reduction == "max":
            return grouped_scores.max(dim=2).values
        raise ValueError(f"Unsupported score reduction: {reduction}")

    def pool_scores(self, scores: torch.Tensor, use_pooling: bool) -> torch.Tensor:
        if not use_pooling:
            return scores
        return F.avg_pool1d(
            scores,
            kernel_size=self.kernel_size,
            padding=self.kernel_size // 2,
            stride=1,
        )

    @staticmethod
    def share_head_scores(
        scores: torch.Tensor, num_key_value_heads: int, enabled: bool
    ) -> torch.Tensor:
        if not enabled:
            return scores
        return scores.mean(dim=1, keepdim=True).repeat(1, num_key_value_heads, 1)

    @staticmethod
    def pad_protected_window(
        scores: torch.Tensor, perturbation_window: int
    ) -> torch.Tensor:
        if perturbation_window == 0:
            return scores
        protected_score = scores.max().item()
        return F.pad(scores, (0, perturbation_window), value=protected_score)

    @staticmethod
    def compute_attention_score(attention: torch.Tensor) -> torch.Tensor:
        return attention.sum(dim=-2)

    def compute_v_score(
        self,
        attention: torch.Tensor,
        values: torch.Tensor,
        perturbation_window: int,
    ) -> torch.Tensor:
        if perturbation_window > 0:
            values = values[:, :, :-perturbation_window]
        if self.can_use_triton(attention, values):
            return triton_v_score(attention, values)
        return attention.pow(2).sum(dim=-2) * values.pow(2).sum(dim=-1)

    def compute_v_l1_score(
        self,
        attention: torch.Tensor,
        values: torch.Tensor,
        perturbation_window: int,
    ) -> torch.Tensor:
        if perturbation_window > 0:
            values = values[:, :, :-perturbation_window]
        return attention.abs().sum(dim=-2) * values.abs().sum(dim=-1)

    def compute_k_score(
        self,
        attention: torch.Tensor,
        logits: torch.Tensor,
        values: torch.Tensor,
        outputs: torch.Tensor,
        perturbation_window: int,
    ) -> torch.Tensor:
        if perturbation_window > 0:
            values = values[:, :, :-perturbation_window]
        value_norm = values.pow(2).sum(dim=-1)
        output_norm = outputs.pow(2).sum(dim=-1)
        value_output_dot = torch.einsum("bhqd,bhpd->bhqp", outputs, values)
        value_minus_output_norm = (
            value_norm[..., None, :] + output_norm[..., None] - 2.0 * value_output_dot
        )
        return ((attention * logits).pow(2) * value_minus_output_norm).sum(dim=-2)

    def compute_vk_score(
        self,
        attention: torch.Tensor,
        logits: torch.Tensor,
        values: torch.Tensor,
        outputs: torch.Tensor,
        perturbation_window: int,
    ) -> torch.Tensor:
        if perturbation_window > 0:
            values = values[:, :, :-perturbation_window]
        attention_norm = attention.pow(2).sum(dim=-2)
        value_norm = values.pow(2).sum(dim=-1)
        output_norm = outputs.pow(2).sum(dim=-1)
        value_output_dot = torch.einsum("bhqd,bhpd->bhqp", outputs, values)
        value_minus_output_norm = (
            value_norm[..., None, :] + output_norm[..., None] - 2.0 * value_output_dot
        )

        value_score = attention_norm * value_norm
        key_score = ((attention * logits).pow(2) * value_minus_output_norm).sum(dim=-2)
        cross_score = (
            2.0
            * attention.pow(2)
            * logits
            * (value_norm[..., None, :] - value_output_dot)
        ).sum(dim=-2)
        return value_score + key_score + cross_score

    def compute_pruning_score(
        self,
        attention: torch.Tensor,
        logits: torch.Tensor,
        values: torch.Tensor,
        outputs: torch.Tensor | None,
        perturbation_window: int,
    ) -> torch.Tensor:
        if self.pruning_score == "obcache-v":
            return self.compute_v_score(attention, values, perturbation_window)
        if self.pruning_score == "obcache-vL1":
            return self.compute_v_l1_score(attention, values, perturbation_window)
        if self.pruning_score == "obcache-k":
            assert outputs is not None
            return self.compute_k_score(
                attention, logits, values, outputs, perturbation_window
            )
        if self.pruning_score == "obcache-vk":
            assert outputs is not None
            return self.compute_vk_score(
                attention, logits, values, outputs, perturbation_window
            )
        if self.pruning_score == "attn":
            return self.compute_attention_score(attention)
        raise ValueError(f"Unsupported pruning score: {self.pruning_score}")

    def score_from_attention(
        self,
        attention: torch.Tensor,
        logits: torch.Tensor,
        values: torch.Tensor,
        num_key_value_heads: int,
        num_key_value_groups: int,
        perturbation_window: int,
        use_pooling: bool,
        head_score_sharing: bool = False,
    ) -> torch.Tensor:
        reduction = None
        normalize_scores = False
        if self.gqa_aggregation == "pre_redc":
            attention = self.reduce_gqa_tensor(
                attention, num_key_value_heads, num_key_value_groups
            )
            logits = self.reduce_gqa_tensor(
                logits, num_key_value_heads, num_key_value_groups
            )
        else:
            values = repeat_kv(values, num_key_value_groups)
            normalize_scores = self.gqa_aggregation.startswith("post_redc_norm_")
            reduction = "mean" if self.gqa_aggregation.endswith("_mean") else "max"

        outputs = None
        if self.pruning_score in {"obcache-k", "obcache-vk"}:
            outputs = torch.matmul(attention, values)

        if perturbation_window > 0:
            attention = attention[..., :-perturbation_window]
            logits = logits[..., :-perturbation_window]
        scores = self.compute_pruning_score(
            attention, logits, values, outputs, perturbation_window
        )

        if reduction is not None:
            scores = self.reduce_gqa_scores(
                scores,
                num_key_value_heads,
                num_key_value_groups,
                reduction,
                normalize_scores,
            )

        scores = self.pool_scores(scores, use_pooling)
        scores = self.share_head_scores(scores, num_key_value_heads, head_score_sharing)
        return self.pad_protected_window(scores, perturbation_window)

    def validate_config(self):
        supported_scores = {"obcache-v", "obcache-vL1", "obcache-k", "obcache-vk", "attn"}
        supported_gqa_modes = {
            "pre_redc",
            "post_redc_mean",
            "post_redc_max",
            "post_redc_norm_mean",
            "post_redc_norm_max",
        }
        assert (
            self.pruning_score in supported_scores
        ), f"Unsupported pruning score: {self.pruning_score}"
        assert (
            self.gqa_aggregation in supported_gqa_modes
        ), f"Unsupported GQA aggregation mode: {self.gqa_aggregation}"


@dataclass
class OBCacheObservedWindowPress(OBCacheScoringMixin, ScorerPress):
    compression_ratio: float = 0.0
    window_size: int = 64
    kernel_size: int = 5
    pruning_score: str = "obcache-v"
    use_triton: bool = True
    gqa_aggregation: str = "pre_redc"
    use_pooling: bool = False
    head_score_sharing: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.validate_config()

    def score(
        self,
        module: nn.Module,
        hidden_states: torch.Tensor,
        keys: torch.Tensor,
        values: torch.Tensor,
        attentions: torch.Tensor,
        kwargs,
    ) -> torch.Tensor:
        assert (
            hidden_states.shape[1] > self.window_size
        ), f"Query length {hidden_states.shape[1]} should be greater than the window size {self.window_size}"

        num_key_value_heads = keys.shape[1]
        num_key_value_groups = module.config.num_attention_heads // num_key_value_heads
        attention, logits = self.compute_causal_attention(
            module,
            hidden_states,
            keys,
            kwargs["position_embeddings"],
            query_start=hidden_states.shape[1] - self.window_size,
        )
        return self.score_from_attention(
            attention=attention,
            logits=logits,
            values=values,
            num_key_value_heads=num_key_value_heads,
            num_key_value_groups=num_key_value_groups,
            perturbation_window=self.window_size,
            use_pooling=self.use_pooling,
            head_score_sharing=self.head_score_sharing,
        )


@dataclass
class OBCacheSnapKVPress(OBCacheObservedWindowPress):
    """
    OBCache scoring driven by the SnapKV observation window.
    """

    use_pooling: bool = True


@dataclass
class OBCacheH2OPress(OBCacheObservedWindowPress):
    """
    OBCache scoring driven by observed attention, in the spirit of H2O.
    """

    use_pooling: bool = False


@dataclass
class OBCacheTOVAPress(OBCacheObservedWindowPress):
    """
    OBCache scoring driven by the last-token query, analogous to TOVA.
    """

    window_size: int = 1
    kernel_size: int = 1
    use_pooling: bool = False


class OBCachePyramidBudgetMixin:
    beta: int
    compression_ratio: float
    window_size: int

    def get_layer_budget(self, module: nn.Module, q_len: int) -> int:
        assert self.beta >= 1, "Beta should >= 1"

        max_capacity_prompt = self.window_size + q_len * (1 - self.compression_ratio)
        min_num = (max_capacity_prompt - self.window_size) / self.beta
        max_num = (max_capacity_prompt - self.window_size) * 2 - min_num

        if max_num >= q_len - self.window_size:
            max_num = q_len - self.window_size
            min_num = (max_capacity_prompt - self.window_size) * 2 - max_num

        if not (q_len >= max_num >= min_num >= self.window_size):
            return round(q_len * (1 - self.compression_ratio))

        steps = (max_num - min_num) / (module.config.num_hidden_layers - 1)
        return round(max_num - module.layer_idx * steps)

    def compress(
        self,
        module: nn.Module,
        hidden_states: torch.Tensor,
        keys: torch.Tensor,
        values: torch.Tensor,
        attentions: torch.Tensor,
        kwargs: dict,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if self.compression_ratio == 0:
            return keys, values

        scores = self.score(module, hidden_states, keys, values, attentions, kwargs)
        num_kept = self.get_layer_budget(module, keys.shape[2])
        indices = scores.topk(num_kept, dim=-1).indices
        indices = indices.unsqueeze(-1).expand(-1, -1, -1, module.head_dim)
        keys = keys.gather(2, indices).contiguous()
        values = values.gather(2, indices).contiguous()
        return keys, values


@dataclass
class OBCachePyramidKVPress(OBCachePyramidBudgetMixin, OBCacheSnapKVPress):
    """
    OBCache scoring with PyramidKV's layer-dependent budget allocation.
    """

    beta: int = 20
