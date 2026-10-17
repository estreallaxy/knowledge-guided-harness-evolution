# SPDX-FileCopyrightText: Copyright (c) 1993-2025 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List, Literal
import sys
import os

import torch
from torch import nn

# Add kvpress to path if not installed
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'kvpress'))
from kvpress.presses.base_press import BasePress

logger = logging.getLogger(__name__)

@dataclass
class DeltaPressLNR(BasePress):
    # NOTE: This implementation prunes **attention only**. FFN is left intact for simplicity;
    # under the eval setting (no revival, no KV for skipped tokens), this is output-equivalent
    # to pruning FFN as well, but without actual FLOPs savings in FFN.
    """
    DeltaPress: second-order stability for token skipping (prefill, attention sublayer only).

    Design/semantics:
    - Hooks are attached to the **self-attention sublayer before residual add**.
    - We compare **attention deltas** across consecutive layers:
    Δ_attn^(l) = attn_out^(l)  (pre-residual delta)
    stability_i^(l) = metric(Δ_attn_i^(l), Δ_attn_i^(l-1)),  metric ∈ {cos (1-cos), l1, l2}.
    Smaller values ⇒ token i is more "converged"/stable across layers.
    - Decide-once: at the **first layer in [start_ratio, end_ratio)**, build a global mask,
    then **reuse the same mask** for all later layers in the flexible range.
    - Skipped tokens: set their **attention delta to 0** in post-hook.
    The outer residual `x <- x + delta` therefore behaves as **identity** for skipped tokens.
    - FFN is **not** pruned in this implementation (attn-only skipping); skipped tokens do not
    produce/receive K/V and will not enter the decode KV cache.
    - Optional thresholding is available via `stability_threshold` but is disabled by default
    (the code path is commented out).
    """

    compression_ratio: float = 0.333     # target drop ratio among eligible tokens (e.g. 0.333 -> drop ~1/3)
    start_ratio: float = 0.4             # flexible-layer range start as fraction of total layers (e.g. 0.5 -> begin at mid-layer)
    end_ratio: float = 1                 # flexible-layer range end as fraction of total layers (1.0 -> include top layers)
    keep_last_token: bool = True         # legacy variable; superseded by `keep_last_n` for clearer semantics
    keep_last_n: int = 32                # force-keep the last n tokens in the sequence
    keep_first_n: int = 64               # force-keep the first n tokens in the sequence
    stability_threshold: float = 0.0     # optional cutoff: drop only if stability <= threshold (***disabled by default***)

    metric: Literal["cos", "l1", "l2"] = "cos"     # distance metric for inter-layer stability (default: cosine similarity)
    decide_once_in_flexible: bool = True           # decide mask once at first flexible layer, reuse for later; False -> per-layer recompute
    order: Literal["first", "second"] = "second"   # "first" -> use magnitude of current delta; "second" -> layer-to-layer delta
    
    # ----------------------- states -----------------------
    def __post_init__(self):
        assert 0.0 <= self.compression_ratio <= 1.0
        assert 0.0 <= self.start_ratio < self.end_ratio <= 1.0
        assert self.metric in ("cos", "l1", "l2")
        assert self.order in ("first", "second")

        self._prev_output_hidden: Optional[torch.Tensor] = None     # previous layer's full-length attn delta (skipped positions are 0)
        self._global_active_mask: Optional[torch.Tensor] = None
        self._decision_layer_idx: Optional[int] = None
        self._prefill_stamp: Optional[int] = None
        
        # previous layer block delta for second order
        self._prev_block_delta: Optional[torch.Tensor] = None  # [B,S,H], full-length; skipped pos 0
        # caches for current layer
        self._h_in_block: Optional[torch.Tensor] = None        # [B,S,H] at ATTENTION-PRE
        self._attn_full_delta: Optional[torch.Tensor] = None   # [B,S,H] synthesized in ATTENTION-POST

        self._active_pairs: Dict[int, List[Tuple[int, int]]] = {}
        self._timings_ms: Dict[int, float] = {}
        self._mem_deltas: Dict[int, int] = {}

    # ----------------------- helpers -----------------------
    def _is_prefill(self, cache_position, seq_len: int) -> bool:
        """Simplified and reliable prefill detection for Qwen2.5."""
        if cache_position is None or not torch.is_tensor(cache_position):
            return True  # default to prefill
        try:
            return cache_position.min().item() == 0
        except Exception:
            return True


    def _flexible_range(self, module: nn.Module) -> Tuple[int, int]:
        """Compute [start_layer, end_layer) indices from ratios w.r.t. config.num_hidden_layers."""
        total_layers = getattr(module.config, "num_hidden_layers", 32)
        start_layer = int(total_layers * self.start_ratio)
        end_layer = int(total_layers * self.end_ratio)
        end_layer = max(start_layer + 1, end_layer)
        return start_layer, end_layer
    
    @staticmethod
    def _cos_1m(x: torch.Tensor, y: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
        # x,y: [B,S,H] -> return [S] (batch-mean)
        x_n = torch.clamp(x.norm(dim=-1), min=eps)
        y_n = torch.clamp(y.norm(dim=-1), min=eps)
        cos = (x * y).sum(dim=-1) / (x_n * y_n)
        cos = torch.clamp(cos, -1.0, 1.0)
        s = 1.0 - cos
        return s.mean(dim=0) if s.dim() == 2 else s
    
    def _maybe_slice_kwargs_in_attn_pre(self, layer_idx: int, kwargs, active_mask: torch.Tensor):
        # Trim inputs so skipped tokens do not enter attention.
        hidden_states = kwargs.get("hidden_states", None)
        cache_position = kwargs.get("cache_position", None)
        if hidden_states is None or cache_position is None:
            return  # nothing to do

        kwargs["hidden_states"] = hidden_states[:, active_mask, :]
        kwargs["cache_position"] = cache_position[active_mask]

        pos_ids = kwargs.get("position_ids", None)
        if torch.is_tensor(pos_ids):
            kwargs["position_ids"] = pos_ids[:, active_mask]

        attn_mask = kwargs.get("attention_mask", None)
        if torch.is_tensor(attn_mask):
            if attn_mask.dim() == 4:
                kwargs["attention_mask"] = attn_mask[:, :, active_mask, :][:, :, :, active_mask]
            elif attn_mask.dim() == 3:
                kwargs["attention_mask"] = attn_mask[:, active_mask, :][:, :, active_mask]
            elif attn_mask.dim() == 2:
                kwargs["attention_mask"] = attn_mask[:, active_mask]

        pos_emb = kwargs.get("position_embeddings", None)
        if isinstance(pos_emb, tuple) and len(pos_emb) == 2:
            cos_pe, sin_pe = pos_emb
            if torch.is_tensor(cos_pe) and torch.is_tensor(sin_pe):
                if cos_pe.dim() == 2:
                    kwargs["position_embeddings"] = (cos_pe[active_mask], sin_pe[active_mask])
                elif cos_pe.dim() == 3:
                    kwargs["position_embeddings"] = (cos_pe[:, active_mask], sin_pe[:, active_mask])


    # ----------------------- hooks -----------------------
    def attn_forward_pre_hook(self, module: nn.Module, args, kwargs):
        """Record original inputs and (during prefill & within flexible range) apply the global active mask.
        This hook trims hidden_states / cache_position (and attention_mask / rope params if present)
        so that skipped tokens DO NOT participate in attention or produce K/V.
        """
        hidden_states = kwargs.get("hidden_states", None)
        cache_position = kwargs.get("cache_position", None)
        if hidden_states is None or cache_position is None:
            print(f"hidden_states is None or cache_position is None")
            return args, kwargs

        bsz, seq_len, hidden_dim = hidden_states.shape
        layer_idx = getattr(module, "layer_idx", None)
        if layer_idx is None:
            print(f"layer_idx is None")
            return args, kwargs

        self._h_in_block = hidden_states
        start_layer, end_layer = self._flexible_range(module)
        in_flexible = start_layer <= layer_idx < end_layer

        # Reset states at layer 0
        if layer_idx == 0 and self._is_prefill(cache_position, seq_len):
            self._global_active_mask = None
            self._decision_layer_idx = None
            self._prefill_stamp = None

        # Only apply during prefill in flexible layers, otherwise exit the rest unchanged
        if not self._is_prefill(cache_position, seq_len) or not in_flexible:
            return args, kwargs
        
        # If mask already decided, apply trimming HERE so no KV is produced for skipped tokens
        if self._global_active_mask is not None and self._global_active_mask.shape[0] == seq_len:
            active_mask = self._global_active_mask.to(hidden_states.device)
            self._maybe_slice_kwargs_in_attn_pre(layer_idx, kwargs, active_mask)
            print(f"[DeltaPress] apply global mask at L={layer_idx}, "
                f"kept={active_mask.sum().item()}/{seq_len} "
                f"({active_mask.sum().item()/seq_len:.2%})")

        return args, kwargs

    def attn_forward_post_hook(self, module: nn.Module, inputs, kwargs, output):
        # Build full-length attention delta: kept = layer_out, skipped = 0
        hidden_in = self._h_in_block  # [B,S,H]
        if hidden_in is None:
            return output

        if isinstance(output, tuple):
            layer_out = output[0]
            extra = output[1:]  
        else:
            layer_out, extra = output, ()

        seq_len = hidden_in.shape[1]
        active_mask = (self._global_active_mask.to(hidden_in.device)
                        if self._global_active_mask is not None and
                            self._global_active_mask.shape[0] == seq_len
                        else torch.ones(seq_len, dtype=torch.bool, device=hidden_in.device))

        kept = int(active_mask.sum().item())

        if layer_out.dim() == 2:
            # [S_active, H] -> [1, S_active, H]
            assert layer_out.shape[0] == kept, \
                f"attn out len={layer_out.shape[0]} != kept={kept}"
            layer_out = layer_out.unsqueeze(0)
        elif layer_out.dim() == 3:
            assert layer_out.shape[1] == kept, \
                f"attn out len={layer_out.shape[1]} != kept={kept}"
        else:
            raise RuntimeError(f"Unexpected attn out dim: {layer_out.shape}")

        full_attn_delta = torch.zeros_like(hidden_in)
        if layer_out.dim() == 2:  # [S_active, H]
            layer_out = layer_out.unsqueeze(0)  # -> [1, S_active, H]
        full_attn_delta[:, active_mask, :] = layer_out
        self._attn_full_delta = full_attn_delta  # cache for block-delta

        # Return with original signature
        if isinstance(output, tuple):
            return (full_attn_delta,) + extra
        else:
            return full_attn_delta
    
    def ffn_forward_pre_hook(self, module: nn.Module, args, kwargs):
        return args, kwargs

    def ffn_forward_post_hook(self, module: nn.Module, inputs, kwargs, output):
        # Build full-length FFN delta and combine with attn delta to get block delta.
        # Also perform masking decision at the FIRST flexible layer (decide-once).
        h_in_block = self._h_in_block
        attn_full_delta = self._attn_full_delta
        
        if attn_full_delta is None or h_in_block is None:
            print(f"attn_full_delta or h_in_block is None")
            return output

        if isinstance(output, tuple):
            ffn_out, *extra = output
        else:
            ffn_out, extra = output, ()

        bsz, seq_len, _ = h_in_block.shape
        layer_idx = getattr(module, "layer_idx", None)
        if layer_idx is None:
            print(f"[DeltaPress] layer_idx is None")
            # return signature
            return output

        # Active mask as used in attention (if decided); otherwise "all-keep"
        if self._global_active_mask is not None and self._global_active_mask.shape[0] == seq_len:
            active_mask = self._global_active_mask.to(h_in_block.device)
        else:
            active_mask = torch.ones(seq_len, dtype=torch.bool, device=h_in_block.device)
        setattr(module, "_dp_active_mask", active_mask)  # for logging symmetry

        # Rebuild full-length FFN delta (skipped = 0)
        if ffn_out.shape[1] == seq_len:
            full_ffn_delta = ffn_out
        else:
            full_ffn_delta = torch.zeros_like(h_in_block)
            full_ffn_delta[:, active_mask, :] = ffn_out

        # Block delta = attn delta + ffn delta (both pre-residual deltas)
        block_delta = attn_full_delta + full_ffn_delta  # [B,S,H]
        block_out = h_in_block + attn_full_delta + full_ffn_delta  # [B,S,H]

        # ----- decide-once at first flexible layer -----
        start_layer, end_layer = self._flexible_range(module)
        in_flexible = start_layer <= layer_idx < end_layer

        cache_position = kwargs.get("cache_position", None)
        prefill = self._is_prefill(cache_position, seq_len)

        need_decide = (
            self.decide_once_in_flexible and
            in_flexible and
            prefill and
            (self._global_active_mask is None) and
            (layer_idx == start_layer)
        )

        if need_decide:
            with torch.no_grad():
                # stability: smaller => more stable => drop first
                if self.order == "first":
                    # 1 - cos(h_in_block, block_delta)
                    stability = self._cos_1m(h_in_block, block_out)  # [S]
                else:  # "second"
                    if self._prev_block_delta is None or self._prev_block_delta.shape != block_out.shape:
                        # No previous: fall back to first-order just for this decision
                        stability = self._cos_1m(h_in_block, block_out)
                    else:
                        stability = self._cos_1m(block_delta, self._prev_block_delta)  # [S]

                n_fix_first = max(0, min(int(self.keep_first_n), seq_len))
                n_fix_last  = max(0, min(int(self.keep_last_n), seq_len))
                elig = torch.arange(n_fix_first, seq_len - n_fix_last, device=h_in_block.device)
                elig_len = max(0, seq_len - n_fix_first - n_fix_last)

                active = torch.ones(seq_len, dtype=torch.bool, device=h_in_block.device)
                if elig_len > 0:
                    drop_target = int(round(self.compression_ratio * seq_len))
                    if drop_target > 0:
                        stab_elig = stability[elig]
                        sorted_idx = torch.argsort(stab_elig, dim=0, descending=False)  # small first
                        drop_idx = elig[sorted_idx[:drop_target]]
                        active[drop_idx] = False
                    # enforce head/tail keep
                    if n_fix_first > 0:
                        active[:n_fix_first] = True
                    if n_fix_last > 0:
                        active[-n_fix_last:] = True
                    elif self.keep_last_token and seq_len > 0:
                        active[-1] = True
                else:
                    active = torch.ones(seq_len, dtype=torch.bool, device=h_in_block.device)
                    if n_fix_first > 0:
                        active[:n_fix_first] = True
                    if n_fix_last > 0:
                        active[-n_fix_last:] = True
                    elif self.keep_last_token and seq_len > 0:
                        active[-1] = True

                self._global_active_mask = active
                self._decision_layer_idx = layer_idx

                kept = int(active.sum().item())
                print(f"[DeltaPress-L-NR] decide@L={layer_idx} kept={kept}/{seq_len} ({kept/seq_len:.2%})")

        # Update previous block delta only if using second-order
        if self.order == "second":
            self._prev_block_delta = block_delta.detach()

        # ----- return with preserved signature -----
        if isinstance(output, tuple):
            return (full_ffn_delta,) + extra
        else:
            return full_ffn_delta

    # ----------------------- KV interface -----------------------
    def compress(self, module, hidden_states, keys, values, attentions, kwargs):
        """KV interface is a no-op here because skipped tokens never produce K/V:
        already trimmed hidden_states/positions in pre-hook."""
        return keys, values

    # ----------------------- reporting -----------------------
    @property
    def skip_ratio(self) -> float:
        if not self._active_pairs:
            return 0.0
        ratios = []
        for pairs in self._active_pairs.values():
            for a, s in pairs:
                if s > 0:
                    ratios.append(1.0 - a / s)
        return sum(ratios) / len(ratios) if ratios else 0.0

    def speedup_estimate(self) -> float:
        if not self._active_pairs:
            return 1.0
        avg_skip = self.skip_ratio
        flexible_ratio = max(0.0, self.end_ratio - self.start_ratio)
        effective_skip = avg_skip * flexible_ratio
        if effective_skip <= 0:
            return 1.0
        attn_speedup = 1.0 / ((1.0 - effective_skip) ** 2)
        ffn_speedup = 1.0 / (1.0 - effective_skip)
        return min(0.7 * attn_speedup + 0.3 * ffn_speedup, 10.0)

    def dump_layer_skip_summary(self):
        lines = ["[DeltaPress] === LayerSkip summary (prefill) ==="]
        for lidx in sorted(self._active_pairs.keys()):
            pairs = self._active_pairs[lidx]
            ratios = [a / s for (a, s) in pairs if s > 0]
            avg_ratio = sum(ratios) / len(ratios) if ratios else 1.0
            ms = self._timings_ms.get(lidx, 0.0)
            dmem = self._mem_deltas.get(lidx, 0)
            lines.append(f"  layer {lidx:02d}: avg_active_ratio={avg_ratio:.3f} "
                         f"time~{ms:.1f} ms  dmem~{dmem/1024/1024:.2f} MB")
        lines.append(f"  avg_skip_ratio={self.skip_ratio:.3%}  est_speedup~{self.speedup_estimate():.2f}x")
        logger.info("\n".join(lines))

    # ----------------------- timing helpers -----------------------
    def _start_timing(self, module):
        if not torch.cuda.is_available():
            return None
        ev_start = torch.cuda.Event(enable_timing=True)
        ev_end = torch.cuda.Event(enable_timing=True)
        torch.cuda.synchronize()
        ev_start.record()
        setattr(module, "_dp_ev_start", ev_start)
        setattr(module, "_dp_ev_end", ev_end)
        setattr(module, "_dp_mem0", torch.cuda.memory_allocated())
        return ev_start

    def _end_timing(self, module, layer_idx: int):
        if not torch.cuda.is_available():
            return
        ev_start = getattr(module, "_dp_ev_start", None)
        ev_end = getattr(module, "_dp_ev_end", None)
        if ev_start is None or ev_end is None:
            return
        ev_end.record()
        torch.cuda.synchronize()
        dt = ev_start.elapsed_time(ev_end)
        self._timings_ms[layer_idx] = self._timings_ms.get(layer_idx, 0.0) + float(dt)
        mem0 = getattr(module, "_dp_mem0", None)
        if mem0 is not None:
            mem1 = torch.cuda.memory_allocated()
            self._mem_deltas[layer_idx] = self._mem_deltas.get(layer_idx, 0) + int(mem1 - mem0)
        for n in ("_dp_ev_start", "_dp_ev_end", "_dp_mem0"):
            if hasattr(module, n):
                delattr(module, n)
