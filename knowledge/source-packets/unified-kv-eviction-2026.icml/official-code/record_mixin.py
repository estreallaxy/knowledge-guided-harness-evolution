# Copyright (c) 2026 Jiaming Yang.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import Any, Dict

import torch
import torch.nn as nn


@dataclass
class CapacityLoggerMixin:
    """
    Mixin for recording layer-wise KV-cache capacity before and after compression.

    The recorded metrics are diagnostic values used to analyze how much key,
    value, and joint key-value capacity is preserved by a compression method.
    Recording is disabled by default and can be enabled by setting
    `record_capacity=True`.
    """

    record_capacity: bool = False
    cap_eps: float = 1e-6
    layer_records: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    _pre_cache: Dict[str, Dict[str, Any]] = field(default_factory=dict, init=False)

    @torch.no_grad()
    def reset_layer_records(self) -> None:
        """
        Clear all capacity records for the current inference run.

        Args:
            None.

        Returns:
            None.
        """
        self.layer_records.clear()
        self._pre_cache.clear()

    @torch.no_grad()
    def pre_compression(
        self,
        module: nn.Module,
        hidden_states: torch.Tensor,
        keys: torch.Tensor,
        values: torch.Tensor,
        attentions: torch.Tensor,
        kwargs: Dict[str, Any],
    ) -> None:
        """
        Record capacity statistics before KV-cache compression.

        Args:
            module: Attention module associated with the current layer.
            hidden_states: Hidden states passed by the KVPress pipeline.
                This argument is unused by the logger and is kept for interface
                compatibility.
            keys: Key cache before compression, with shape [B, H_kv, T, D_k].
            values: Value cache before compression, with shape
                [B, H_kv, T, D_v].
            attentions: Attention tensor passed by the KVPress pipeline.
                This argument is unused by the logger and is kept for interface
                compatibility.
            kwargs: Additional metadata. If `layer_name` or `layer_idx` is
                present, it is used to construct a stable layer identifier.

        Returns:
            None.
        """
        del hidden_states, attentions

        if not self.record_capacity:
            return

        layer_id = self._layer_id(module, kwargs)

        pre_key_cap = self._logdet_I_plus_XtX(keys, eps=self.cap_eps)
        pre_val_cap = self._logdet_I_plus_XtX(values, eps=self.cap_eps)
        pre_total_cap = self._logdet_total_capacity(keys, values, eps=self.cap_eps)

        self._pre_cache[layer_id] = {
            "pre_key_capacity": float(pre_key_cap),
            "pre_value_capacity": float(pre_val_cap),
            "pre_total_capacity": float(pre_total_cap),
            "pre_k_shape": tuple(keys.shape),
            "pre_v_shape": tuple(values.shape),
        }

    @torch.no_grad()
    def post_compression(
        self,
        module: nn.Module,
        hidden_states: torch.Tensor,
        keys: torch.Tensor,
        values: torch.Tensor,
        attentions: torch.Tensor,
        kwargs: Dict[str, Any],
    ) -> None:
        """
        Record capacity statistics after KV-cache compression.

        Args:
            module: Attention module associated with the current layer.
            hidden_states: Hidden states passed by the KVPress pipeline.
                This argument is unused by the logger and is kept for interface
                compatibility.
            keys: Key cache after compression, with shape [B, H_kv, T', D_k].
            values: Value cache after compression, with shape
                [B, H_kv, T', D_v].
            attentions: Attention tensor passed by the KVPress pipeline.
                This argument is unused by the logger and is kept for interface
                compatibility.
            kwargs: Additional metadata. If `layer_name` or `layer_idx` is
                present, it is used to construct a stable layer identifier.

        Returns:
            None.
        """
        del hidden_states, attentions

        if not self.record_capacity:
            return

        layer_id = self._layer_id(module, kwargs)
        pre_record = self._pre_cache.pop(layer_id, None)

        post_key_cap = self._logdet_I_plus_XtX(keys, eps=self.cap_eps)
        post_val_cap = self._logdet_I_plus_XtX(values, eps=self.cap_eps)
        post_total_cap = self._logdet_total_capacity(keys, values, eps=self.cap_eps)

        record: Dict[str, Any] = {
            "layer_id": layer_id,
            "post_key_capacity": float(post_key_cap),
            "post_value_capacity": float(post_val_cap),
            "post_total_capacity": float(post_total_cap),
            "post_k_shape": tuple(keys.shape),
            "post_v_shape": tuple(values.shape),
        }

        if pre_record is not None:
            record.update(pre_record)

            ratio_eps = 1e-12
            record["key_capacity_ratio"] = float(
                record["post_key_capacity"] / (record["pre_key_capacity"] + ratio_eps)
            )
            record["value_capacity_ratio"] = float(
                record["post_value_capacity"] / (record["pre_value_capacity"] + ratio_eps)
            )
            record["total_capacity_ratio"] = float(
                record["post_total_capacity"] / (record["pre_total_capacity"] + ratio_eps)
            )

            pre_tokens = pre_record["pre_k_shape"][2]
            post_tokens = record["post_k_shape"][2]
            record["token_ratio"] = float(post_tokens / max(pre_tokens, 1))
        else:
            record["warning"] = "missing_pre_cache"

        self.layer_records[layer_id] = record

    def _layer_id(self, module: nn.Module, kwargs: Dict[str, Any]) -> str:
        """
        Build a stable identifier for the current layer.

        Args:
            module: Attention module associated with the current layer.
            kwargs: Additional metadata that may contain `layer_name` or
                `layer_idx`.

        Returns:
            A string identifier for the current layer.
        """
        if "layer_name" in kwargs:
            return str(kwargs["layer_name"])

        if "layer_idx" in kwargs:
            return f"{module.__class__.__name__}[{kwargs['layer_idx']}]"

        if hasattr(module, "layer_idx"):
            return str(module.layer_idx)

        return f"{module.__class__.__name__}[id={id(module)}]"

    @torch.no_grad()
    def _logdet_I_plus_XtX(self, X: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
        """
        Compute the log-determinant capacity proxy log det(I + X^T X).

        Args:
            X: Input tensor with shape [B, H, T, D].
            eps: Diagonal jitter used for numerical stability.

        Returns:
            Scalar tensor equal to the mean log determinant over B * H groups.
        """
        if X.dim() != 4:
            raise ValueError(f"Expected X with shape [B, H, T, D], got {tuple(X.shape)}.")

        batch_size, num_heads, _, feature_dim = X.shape
        X_flat = X.to(torch.float32).reshape(batch_size * num_heads, -1, feature_dim)
        gram = X_flat.transpose(-1, -2) @ X_flat

        identity = torch.eye(feature_dim, device=X.device, dtype=torch.float32).unsqueeze(0)
        matrix = gram + (1.0 + eps) * identity

        return self._spd_logdet_mean(matrix, eps=eps)

    @torch.no_grad()
    def _logdet_I_plus_XUUtXt(
        self,
        X: torch.Tensor,
        U: torch.Tensor,
        eps: float = 1e-6,
    ) -> torch.Tensor:
        """
        Compute the proxy log det(I + X^T U U^T X).

        Args:
            X: Input tensor with shape [B, H, T, D].
            U: Auxiliary tensor with shape [B, H, T, R].
            eps: Diagonal jitter used for numerical stability.

        Returns:
            Scalar tensor equal to the mean log determinant over B * H groups.
        """
        if X.dim() != 4 or U.dim() != 4:
            raise ValueError(
                "Expected X and U to have rank 4, got "
                f"X={tuple(X.shape)} and U={tuple(U.shape)}."
            )

        batch_size, num_heads, num_tokens, feature_dim = X.shape
        u_batch, u_heads, u_tokens, aux_dim = U.shape

        if (u_batch, u_heads, u_tokens) != (batch_size, num_heads, num_tokens):
            raise ValueError(
                "X and U must match in their [B, H, T] dimensions, got "
                f"X={tuple(X.shape)} and U={tuple(U.shape)}."
            )

        X_flat = X.to(torch.float32).reshape(batch_size * num_heads, num_tokens, feature_dim)
        U_flat = U.to(torch.float32).reshape(batch_size * num_heads, num_tokens, aux_dim)

        ux = U_flat.transpose(-1, -2) @ X_flat
        gram = ux.transpose(-1, -2) @ ux

        identity = torch.eye(feature_dim, device=X.device, dtype=torch.float32).unsqueeze(0)
        matrix = gram + (1.0 + eps) * identity

        return self._spd_logdet_mean(matrix, eps=eps)

    @torch.no_grad()
    def _logdet_I_plus_AAt(
        self,
        K: torch.Tensor,
        U: torch.Tensor,
        w: torch.Tensor | None = None,
        eps: float = 1e-6,
    ) -> torch.Tensor:
        """
        Compute log det(I + A A^T), where A = sum_t u_t k_t^T.

        If the output dimension is larger than the key dimension, the equivalent
        determinant log det(I + A^T A) is used for efficiency.

        Args:
            K: Key tensor with shape [B, H, T, D_k].
            U: Output-channel tensor with shape [B, H, T, D_u].
            w: Optional non-negative weights with shape [B, H, T].
            eps: Diagonal jitter used for numerical stability.

        Returns:
            Scalar tensor equal to the mean log determinant over B * H groups.
        """
        K_eff, U_eff = self._prepare_weighted_key_value(K, U, w)

        batch_size, num_heads, num_tokens, key_dim = K_eff.shape
        value_dim = U_eff.size(-1)

        K_flat = K_eff.to(torch.float32).reshape(batch_size * num_heads, num_tokens, key_dim)
        U_flat = U_eff.to(torch.float32).reshape(batch_size * num_heads, num_tokens, value_dim)

        channel = U_flat.transpose(-1, -2) @ K_flat
        matrix = self._channel_gram(channel)

        return self._spd_logdet_mean(matrix, eps=eps)

    @torch.no_grad()
    def _logdet_total_capacity(
        self,
        K: torch.Tensor,
        U: torch.Tensor,
        w: torch.Tensor | None = None,
        eps: float = 1e-6,
        scale_by_sqrtT: bool = True,
    ) -> torch.Tensor:
        """
        Compute the joint key-value capacity proxy used by the logger.

        The channel matrix is defined as A = U^T K. The returned metric is
        log det(I + A A^T) or the equivalent smaller-side determinant. When
        `scale_by_sqrtT=True`, A is divided by sqrt(T) to reduce sensitivity to
        the absolute cache length.

        Args:
            K: Key tensor with shape [B, H, T, D_k].
            U: Value or output-channel tensor with shape [B, H, T, D_u].
            w: Optional non-negative weights with shape [B, H, T].
            eps: Diagonal jitter used for numerical stability.
            scale_by_sqrtT: Whether to normalize the channel matrix by sqrt(T).

        Returns:
            Scalar tensor equal to the mean log determinant over B * H groups.
        """
        K_eff, U_eff = self._prepare_weighted_key_value(K, U, w)

        batch_size, num_heads, num_tokens, key_dim = K_eff.shape
        value_dim = U_eff.size(-1)

        if num_tokens <= 0:
            raise ValueError("The token dimension T must be positive.")

        K_flat = K_eff.to(torch.float32).reshape(batch_size * num_heads, num_tokens, key_dim)
        U_flat = U_eff.to(torch.float32).reshape(batch_size * num_heads, num_tokens, value_dim)

        channel = U_flat.transpose(-1, -2) @ K_flat
        if scale_by_sqrtT:
            channel = channel / (num_tokens ** 0.5)

        matrix = self._channel_gram(channel)

        return self._spd_logdet_mean(matrix, eps=eps)

    def _prepare_weighted_key_value(
        self,
        K: torch.Tensor,
        U: torch.Tensor,
        w: torch.Tensor | None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Validate key-value tensors and optionally apply non-negative weights.

        Args:
            K: Key tensor with shape [B, H, T, D_k].
            U: Value or output-channel tensor with shape [B, H, T, D_u].
            w: Optional non-negative weights with shape [B, H, T].

        Returns:
            A pair `(K_eff, U_eff)` with the same shapes as `K` and `U`.
        """
        if K.dim() != 4 or U.dim() != 4:
            raise ValueError(
                "Expected K and U to have rank 4, got "
                f"K={tuple(K.shape)} and U={tuple(U.shape)}."
            )

        batch_size, num_heads, num_tokens, _ = K.shape

        if U.shape[:3] != (batch_size, num_heads, num_tokens):
            raise ValueError(
                "K and U must match in their [B, H, T] dimensions, got "
                f"K={tuple(K.shape)} and U={tuple(U.shape)}."
            )

        if w is None:
            return K, U

        if w.dim() != 3 or w.shape != (batch_size, num_heads, num_tokens):
            raise ValueError(
                f"Expected w with shape [B, H, T] = {(batch_size, num_heads, num_tokens)}, "
                f"got {tuple(w.shape)}."
            )

        sqrt_weights = torch.sqrt(torch.clamp(w, min=0.0)).unsqueeze(-1)
        return K * sqrt_weights, U * sqrt_weights

    def _channel_gram(self, channel: torch.Tensor) -> torch.Tensor:
        """
        Build the smaller-side Gram matrix of a channel tensor.

        Args:
            channel: Channel matrix with shape [N, D_u, D_k].

        Returns:
            Gram matrix with shape [N, min(D_u, D_k), min(D_u, D_k)].
        """
        if channel.dim() != 3:
            raise ValueError(f"Expected channel with shape [N, D_u, D_k], got {tuple(channel.shape)}.")

        output_dim = channel.size(-2)
        key_dim = channel.size(-1)

        if output_dim <= key_dim:
            return channel @ channel.transpose(-1, -2)

        return channel.transpose(-1, -2) @ channel

    def _spd_logdet_mean(self, matrix: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
        """
        Compute the mean log determinant of I + matrix for SPD matrices.

        Args:
            matrix: Symmetric positive semi-definite matrix with shape [N, D, D].
            eps: Initial diagonal jitter used for Cholesky factorization.

        Returns:
            Scalar tensor equal to the mean log determinant over N matrices.
        """
        if matrix.dim() != 3 or matrix.size(-1) != matrix.size(-2):
            raise ValueError(f"Expected matrix with shape [N, D, D], got {tuple(matrix.shape)}.")

        matrix = matrix.to(torch.float32)
        matrix = 0.5 * (matrix + matrix.transpose(-1, -2))

        dim = matrix.size(-1)
        identity = torch.eye(dim, device=matrix.device, dtype=torch.float32).unsqueeze(0)

        base = identity + matrix
        jitter = eps

        for _ in range(6):
            try:
                chol = torch.linalg.cholesky(base + jitter * identity)
                diag = torch.diagonal(chol, dim1=-2, dim2=-1)
                logdet = 2.0 * torch.log(diag).sum(dim=-1)
                return logdet.mean()
            except RuntimeError:
                jitter *= 10.0

        sign, logabsdet = torch.linalg.slogdet(base + jitter * identity)
        if torch.any(sign <= 0):
            raise RuntimeError("Failed to compute a positive log determinant for the capacity matrix.")

        return logabsdet.mean()
