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
class DeltaPress(BasePress):
    """
    Cosine-only true layer skipping (prefill).

    Design:
    - Measure token-wise stability by (1 - cosine) between the current layer's input
      and the previous layer's input (stored at the last pre-hook).
    - Rank-first: select the most stable tokens (smallest 1 - cos) up to the target
      compression ratio as drop candidates.
    - Threshold-second: only drop candidates whose stability <= stability_threshold.
    - For skipped tokens, the layer behaves like identity (pass-through) at post-hook,
      preserving residual semantics.
    """

    compression_ratio: float = 0.333
    start_ratio: float = 0.4
    end_ratio: float = 1
    keep_last_token: bool = True
    keep_last_n: int = 32
    keep_first_n: int = 64
    stability_threshold: float = 0.0  # e.g. drop if 1 - cos <= 0.02 (cos >= 0.98)

    metric: Literal["cos", "l1", "l2"] = "cos"
    decide_once_in_flexible: bool = True

    # internal states
    def __post_init__(self):
        assert 0.0 <= self.compression_ratio <= 1.0
        assert 0.0 <= self.start_ratio < self.end_ratio <= 1.0
        assert self.metric in ("cos", "l1", "l2")

        self._prev_output_hidden: Optional[torch.Tensor] = None
        self._global_active_mask: Optional[torch.Tensor] = None
        self._decision_layer_idx: Optional[int] = None
        self._prefill_stamp: Optional[int] = None

        self._active_pairs: Dict[int, List[Tuple[int, int]]] = {}
        self._timings_ms: Dict[int, float] = {}
        self._mem_deltas: Dict[int, int] = {}

    # ----------------------- helpers -----------------------
    def _compute_stability(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Compute per-token stability between tensors [B, S, H]."""
        eps = 1e-6
        if self.metric == "cos":
            x_norm = torch.clamp(x.norm(dim=-1), min=eps)
            y_norm = torch.clamp(y.norm(dim=-1), min=eps)
            cos = (x * y).sum(dim=-1) / (x_norm * y_norm)
            stability_b = (1.0 - cos)
        elif self.metric == "l1":
            stability_b = (x - y).abs().sum(dim=-1)
        else:  # "l2"
            stability_b = (x - y).norm(dim=-1)

        if stability_b.dim() == 2:
            return stability_b.mean(dim=0)  # [S]
        return stability_b  # [S]

    def _is_prefill(self, cache_position, seq_len: int) -> bool:
        """Return True if we are still in prefill (before first decode token)."""
        try:
            return int(cache_position.max().item()) < seq_len
        except Exception:
            return True

    def _flexible_range(self, module: nn.Module) -> Tuple[int, int]:
        total_layers = getattr(module.config, "num_hidden_layers", 32)
        start_layer = int(total_layers * self.start_ratio)
        end_layer = int(total_layers * self.end_ratio)
        end_layer = max(start_layer + 1, end_layer)
        return start_layer, end_layer

    # ----------------------- hooks -----------------------
    def forward_pre_hook(self, module: nn.Module, args, kwargs):
        """Record input hidden states, apply active mask if available.

        Args:
            module (nn.Module): the transformer layer module
            args (_type_): _positional args (ignored)
            kwargs (_type_): keyword args, should contain:
                - hidden_states: [B, S, H]
                - cache_position: [S] (int)
        Returns:
            _type_: possibly modified args, kwargs
        """
        hidden_states = kwargs.get("hidden_states", None)
        cache_position = kwargs.get("cache_position", None)
        if hidden_states is None or cache_position is None:
            return args, kwargs

        bsz, seq_len, hidden_dim = hidden_states.shape
        layer_idx = getattr(module, "layer_idx", None)

        setattr(module, "_ls_orig_h", hidden_states)
        setattr(module, "_ls_seq_len", seq_len)

        start_layer, end_layer = self._flexible_range(module)
        in_flexible = (layer_idx is not None and start_layer <= layer_idx < end_layer)

        # Reset states at layer 0
        if layer_idx == 0:
            self._global_active_mask = None
            self._decision_layer_idx = None
            self._prefill_stamp = None

        # Only apply during prefill in flexible layers, otherwise exit the rest unchanged
        if not self._is_prefill(cache_position, seq_len):
            self._global_active_mask = None
            self._decision_layer_idx = None
            self._prefill_stamp = None
            self._start_timing(module)
            return args, kwargs

        # Default: all tokens active
        active_mask = torch.ones(seq_len, dtype=torch.bool, device=hidden_states.device)

        # If global mask already decided(still in flexible zone), reuse it
        if self.decide_once_in_flexible and in_flexible and (self._global_active_mask is not None):
            # If length mismatch, fallback to all-keep
            if self._global_active_mask.shape[0] == seq_len:
                # Update active mask from global if valid
                active_mask = self._global_active_mask.to(hidden_states.device)
                ### LOG PATCH
                print(f"[DeltaPress] apply global mask at L={layer_idx}, "
                    f"kept={active_mask.sum().item()}/{seq_len} "
                    f"({active_mask.sum().item()/seq_len:.2%})")
            else:
                print(f"[DeltaPress] apply global mask length mismatch at L={layer_idx}, "
                    f"mask={self._global_active_mask.shape[0]}, seq={seq_len}, fallback=all-keep")
                active_mask = torch.ones(seq_len, dtype=torch.bool, device=hidden_states.device)

        # Store active mask for post-hook
        setattr(module, "_ls_active_mask", active_mask)

        # If not all active(in flexible zone), filter hidden_states and related kwargs
        if active_mask.sum().item() < seq_len:
            kwargs["hidden_states"] = hidden_states[:, active_mask, :]
            kwargs["cache_position"] = cache_position[active_mask]

            # also filter attention mask / position embeddings if any
            attn_mask = kwargs.get("attention_mask", None)
            if attn_mask is not None:
                if attn_mask.dim() == 4:
                    kwargs["attention_mask"] = attn_mask[:, :, active_mask, :][:, :, :, active_mask]
                elif attn_mask.dim() == 2:
                    kwargs["attention_mask"] = attn_mask[:, active_mask]

            pos_emb = kwargs.get("position_embeddings", None)
            if pos_emb is not None:
                cos_pe, sin_pe = pos_emb
                if cos_pe.dim() == 2:
                    kwargs["position_embeddings"] = (cos_pe[active_mask], sin_pe[active_mask])
                elif cos_pe.dim() == 3:
                    kwargs["position_embeddings"] = (cos_pe[:, active_mask], sin_pe[:, active_mask])

        kept = int(active_mask.sum().item())
        print(f"[DeltaPress] layer {layer_idx}: active={kept}/{seq_len}")
        logger.info(f"[DeltaPress] layer {layer_idx}: active={kept}/{seq_len}")

        self._active_pairs.setdefault(layer_idx, []).append((kept, seq_len))
        self._start_timing(module)
        return args, kwargs

    def forward_post_hook(self, module: nn.Module, inputs, kwargs, output):
        """ Restore full sequence by inserting skipped tokens as identity.

        Args:
            module (nn.Module): the transformer layer module
            inputs (_type_): _positional inputs (ignored)
            kwargs (_type_): keyword args, should contain:
                - cache_position: [S] (int)
            output (_type_): the output hidden states, or (hidden_states, attn_weights)

        Returns:
            _type_: the restored output, or (hidden_states, attn_weights)
        """
        # Retrieve stored states
        orig_h = getattr(module, "_ls_orig_h", None)
        active_in = getattr(module, "_ls_active_mask", None)
        seq_len = getattr(module, "_ls_seq_len", None)
        layer_idx = getattr(module, "layer_idx", None)

        # If any missing, return output unchanged
        if orig_h is None or active_in is None or seq_len is None:
            return output
        
        # If prefill stamp changed, reset states
        if isinstance(output, tuple):
            layer_out = output[0]
            attn_w = output[1] if len(output) > 1 else None
        else:
            layer_out = output
            attn_w = None

        # Pass-through if in flexible zone 
        full_out = orig_h.clone()
        full_out[:, active_in, :] = layer_out
        
        start_layer, end_layer = self._flexible_range(module)
        in_flexible = (layer_idx is not None and start_layer <= layer_idx < end_layer)
        cache_position = kwargs.get("cache_position", None)

        # Reset if not prefill
        if not self._is_prefill(cache_position, seq_len):
            self._global_active_mask = None
            self._decision_layer_idx = None
            self._prev_output_hidden = full_out.detach()
            self._end_timing(module, layer_idx if layer_idx is not None else -1)
            return (full_out, attn_w)

        # At layer 0, just store and return
        if layer_idx == 0:
            self._prev_output_hidden = full_out.detach()
            self._prefill_stamp = int(full_out.data_ptr())
            self._end_timing(module, layer_idx)
            return (full_out, attn_w)

        # Need mask decision if in flexible zone and not yet decided(first flexible layer)
        need_decide = (
            self.decide_once_in_flexible and
            in_flexible and
            (self._global_active_mask is None) and
            (layer_idx == start_layer)
        )

        # Decide active mask if in flexible zone and not yet decided(every flexible layer)
        if need_decide and self._prev_output_hidden is not None and \
           self._prev_output_hidden.shape == full_out.shape:
            with torch.no_grad():
                stability = self._compute_stability(full_out, self._prev_output_hidden)

                n_fix_first = max(0, min(int(self.keep_first_n), seq_len))
                n_fix_last = max(0, min(int(self.keep_last_n), seq_len))

                eligible = torch.arange(n_fix_first, seq_len - n_fix_last, device=full_out.device)
                eligible_len = max(0, seq_len - n_fix_first - n_fix_last)

                if eligible_len > 0:
                    drop_target = int(round(self.compression_ratio * eligible_len))
                    active_mask = torch.ones(seq_len, dtype=torch.bool, device=full_out.device)

                    if drop_target > 0:
                        stab_eligible = stability[eligible]
                        sorted_idx = torch.argsort(stab_eligible, dim=0, descending=False)
                        cand = sorted_idx[:drop_target]
                        drop_idx = eligible[cand]

                        '''if self.stability_threshold > 0:
                            ok = stab_eligible[cand] <= self.stability_threshold
                            drop_idx = drop_idx[ok]'''

                        active_mask[drop_idx] = False

                    # enforce front/back keep
                    if n_fix_first > 0:
                        active_mask[:n_fix_first] = True
                    if n_fix_last > 0:
                        active_mask[-n_fix_last:] = True
                    elif self.keep_last_token and seq_len > 0:
                        active_mask[-1] = True
                        
                # If no eligible tokens(not in felxible zone), just keep all
                else:
                    active_mask = torch.ones(seq_len, dtype=torch.bool, device=full_out.device)
                    if n_fix_first > 0:
                        active_mask[:n_fix_first] = True
                    if n_fix_last > 0:
                        active_mask[-n_fix_last:] = True
                    elif self.keep_last_token and seq_len > 0:
                        active_mask[-1] = True

                self._global_active_mask = active_mask
                self._decision_layer_idx = layer_idx

                kept = int(active_mask.sum().item())
                #print(f"[DeltaPress] decide mask at layer {layer_idx}: keep={kept}/{seq_len}")
                ### LOG PATCH
                print(f"[DeltaPress] decide mask at L={layer_idx}, "
                    f"S={seq_len}, eligible={eligible.numel()}, drop_target={drop_target}, "
                    f"keep_first={n_fix_first}, keep_last={n_fix_last}, "
                    f"kept={kept}/{seq_len} ({kept/seq_len:.2%}), "
                    f"thr={self.stability_threshold}")
        else:
            if need_decide:
                print(f"[DeltaPress] warn: no prev_output to decide at layer {layer_idx}, skip.")

        self._prev_output_hidden = full_out.detach()

        kept = int(self._global_active_mask.sum().item()) if self._global_active_mask is not None else seq_len
        self._active_pairs.setdefault(layer_idx, []).append((kept, seq_len))
        self._end_timing(module, layer_idx if layer_idx is not None else -1)

        return (full_out, attn_w)

    # ----------------------- KV interface -----------------------
    def compress(self, module, hidden_states, keys, values, attentions, kwargs):
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
        setattr(module, "_ls_ev_start", ev_start)
        setattr(module, "_ls_ev_end", ev_end)
        setattr(module, "_ls_mem0", torch.cuda.memory_allocated())
        return ev_start

    def _end_timing(self, module, layer_idx: int):
        if not torch.cuda.is_available():
            return
        ev_start = getattr(module, "_ls_ev_start", None)
        ev_end = getattr(module, "_ls_ev_end", None)
        if ev_start is None or ev_end is None:
            return
        ev_end.record()
        torch.cuda.synchronize()
        dt = ev_start.elapsed_time(ev_end)
        self._timings_ms[layer_idx] = self._timings_ms.get(layer_idx, 0.0) + float(dt)
        mem0 = getattr(module, "_ls_mem0", None)
        if mem0 is not None:
            mem1 = torch.cuda.memory_allocated()
            self._mem_deltas[layer_idx] = self._mem_deltas.get(layer_idx, 0) + int(mem1 - mem0)
        for n in ("_ls_ev_start", "_ls_ev_end", "_ls_mem0"):
            if hasattr(module, n):
                delattr(module, n)
