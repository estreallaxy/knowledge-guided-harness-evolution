# delta_press.py
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List, Literal

import torch
from torch import nn
from kvpress.presses.base_press import BasePress

logger = logging.getLogger(__name__)


# ============================================================
# DeltaPress: pruning is applied at decoder layer input,
# decision is based ONLY on self-attention output change.
# ============================================================
@dataclass
class DeltaPress(BasePress):
    """
    Vision-only token pruning (compute skipping), with decision based ONLY on attention output change.

    How it works:
      - You provide vision_mask_1d [S] bool via set_vision_mask().
        True means "this position is a visual token" (<|image_pad|>/<|video_pad|> positions).
      - Non-vision tokens are always kept.
      - In prefill, at the first layer of flexible range (start_layer),
        we decide a GLOBAL active mask based on:
            stability = metric(attn_out[start_layer], attn_out[start_layer-1])
        (attention outputs are full-length at this time because mask is not decided yet)
      - Then in later layers (and in flexible range), forward_pre_hook prunes hidden/masks/rope
        based on this global active mask.
      - forward_post_hook reconstructs full sequence by identity for skipped tokens.

    No forced retention: no keep_first_n/keep_last_n/keep_last_token.
    """

    compression_ratio: float = 0.333
    start_ratio: float = 0.4
    end_ratio: float = 1.0

    metric: Literal["cos", "l1", "l2"] = "cos"
    decide_once_in_flexible: bool = True

    stability_threshold: float = 0.0  # optional; not enabled by default
    enable_timing: bool = False

    def __post_init__(self):
        assert 0.0 <= self.compression_ratio <= 1.0
        assert 0.0 <= self.start_ratio < self.end_ratio <= 1.0
        assert self.metric in ("cos", "l1", "l2")

        # global decision
        self._global_active_mask: Optional[torch.Tensor] = None
        self._decision_layer_idx: Optional[int] = None

        # for attn-only decision
        self._prev_attn_out_full: Optional[torch.Tensor] = None  # [B,S,H] on CPU

        # vision mask (1D [S] bool on CPU)
        self._vision_mask_1d: Optional[torch.Tensor] = None

        # stats
        self._active_pairs: Dict[int, List[Tuple[int, int]]] = {}
        self._timings_ms: Dict[int, float] = {}
        self._mem_deltas: Dict[int, int] = {}

    # ----------------------- public API -----------------------
    def set_vision_mask(self, vision_mask_1d: Optional[torch.Tensor]):
        """
        vision_mask_1d: [S] bool. True means visual token position(s).
        Only these positions are eligible to be dropped.
        """
        if vision_mask_1d is None:
            self._vision_mask_1d = None
            return
        if not torch.is_tensor(vision_mask_1d):
            raise TypeError("vision_mask_1d must be a torch.Tensor or None")
        if vision_mask_1d.dim() != 1:
            raise ValueError(f"vision_mask_1d must be 1D [S], got {vision_mask_1d.shape}")
        self._vision_mask_1d = vision_mask_1d.bool().detach().to("cpu")

    # ----------------------- helpers -----------------------
    def _vision_mask_on(self, seq_len: int, device) -> Optional[torch.Tensor]:
        if self._vision_mask_1d is None:
            return None
        if self._vision_mask_1d.numel() != seq_len:
            return None
        return self._vision_mask_1d.to(device)

    def _compute_stability(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """x,y: [B,S,H] -> stability [S]"""
        eps = 1e-6
        if self.metric == "cos":
            x_norm = torch.clamp(x.norm(dim=-1), min=eps)
            y_norm = torch.clamp(y.norm(dim=-1), min=eps)
            cos = (x * y).sum(dim=-1) / (x_norm * y_norm)
            stab = (1.0 - cos)
        elif self.metric == "l1":
            stab = (x - y).abs().sum(dim=-1)
        else:  # "l2"
            stab = (x - y).norm(dim=-1)

        return stab.mean(dim=0) if stab.dim() == 2 else stab

    def _is_prefill(self, cache_position, seq_len: int) -> bool:
        """True if still in prefill."""
        try:
            # common case: cache_position is [S] increasing
            return int(cache_position.max().item()) < seq_len
        except Exception:
            return True

    def _flexible_range(self, module: nn.Module) -> Tuple[int, int]:
        cfg = getattr(module, "config", None)
        total_layers = getattr(cfg, "num_hidden_layers", 32)
        start_layer = int(total_layers * self.start_ratio)
        end_layer = int(total_layers * self.end_ratio)
        end_layer = max(start_layer + 1, end_layer)
        return start_layer, end_layer

    # ============================================================
    # A) Decoder layer hooks: apply pruning + rebuild full length
    # ============================================================
    def forward_pre_hook(self, module: nn.Module, args, kwargs):
        hidden_states = kwargs.get("hidden_states", None)
        hidden_from_args = False
        if hidden_states is None and len(args) > 0 and isinstance(args[0], torch.Tensor):
            hidden_states = args[0]
            hidden_from_args = True

        cache_position = kwargs.get("cache_position", None)
        if hidden_states is None or cache_position is None:
            return args, kwargs

        if cache_position.device != hidden_states.device:
            cache_position = cache_position.to(hidden_states.device)
            kwargs["cache_position"] = cache_position

        bsz, seq_len, _ = hidden_states.shape
        layer_idx = getattr(module, "layer_idx", None)

        start_layer, end_layer = self._flexible_range(module)
        in_flexible = (layer_idx is not None and start_layer <= layer_idx < end_layer)
        in_prefill = self._is_prefill(cache_position, seq_len)

        # reset runtime states at start of a new prefill
        if layer_idx == 0 and in_prefill:
            self._global_active_mask = None
            self._decision_layer_idx = None
            self._prev_attn_out_full = None

        # decode stage: don't prune
        if not in_prefill:
            for n in ("_ls_orig_h", "_ls_seq_len", "_ls_active_mask"):
                if hasattr(module, n):
                    delattr(module, n)
            self._start_timing(module)
            return args, kwargs

        # save original input for reconstruction
        setattr(module, "_ls_orig_h", hidden_states)
        setattr(module, "_ls_seq_len", seq_len)

        # default keep all
        active_mask = torch.ones(seq_len, dtype=torch.bool, device=hidden_states.device)

        # reuse global mask once decided
        if self.decide_once_in_flexible and in_flexible and (self._global_active_mask is not None):
            if self._global_active_mask.shape[0] == seq_len:
                active_mask = self._global_active_mask.to(hidden_states.device)
            else:
                active_mask = torch.ones(seq_len, dtype=torch.bool, device=hidden_states.device)

        setattr(module, "_ls_active_mask", active_mask)

        # ---------- prune tokens ----------
        if active_mask.sum().item() < seq_len:
            new_hidden = hidden_states[:, active_mask, :]

            # replace args/kwargs
            if hidden_from_args:
                args = (new_hidden,) + tuple(args[1:])
                if "hidden_states" in kwargs:
                    kwargs.pop("hidden_states")
            else:
                kwargs["hidden_states"] = new_hidden

            # cache_position can be [S] or [B,S]
            if torch.is_tensor(cache_position):
                if cache_position.dim() == 1:
                    kwargs["cache_position"] = cache_position[active_mask]
                elif cache_position.dim() == 2:
                    kwargs["cache_position"] = cache_position[:, active_mask]

            # attention_mask crop
            attn_mask = kwargs.get("attention_mask", None)
            if attn_mask is not None:
                if attn_mask.device != hidden_states.device:
                    attn_mask = attn_mask.to(hidden_states.device)
                if attn_mask.dim() == 4:        # [B, nh, S, S] or [B,1,S,S]
                    attn_mask = attn_mask[:, :, active_mask, :][:, :, :, active_mask]
                elif attn_mask.dim() == 3:      # [B, S, S]
                    attn_mask = attn_mask[:, active_mask, :][:, :, active_mask]
                elif attn_mask.dim() == 2:      # [B, S]
                    attn_mask = attn_mask[:, active_mask]
                kwargs["attention_mask"] = attn_mask

            # RoPE position_embeddings crop (Qwen2-VL can be 4D [3,B,S,D])
            pos_emb = kwargs.get("position_embeddings", None)
            if pos_emb is not None:
                cos_pe, sin_pe = pos_emb
                dev = hidden_states.device
                cos_pe = cos_pe.to(dev)
                sin_pe = sin_pe.to(dev)

                if cos_pe.dim() == 2:           # [S, D]
                    cos_pe = cos_pe[active_mask]
                    sin_pe = sin_pe[active_mask]
                elif cos_pe.dim() == 3:         # [B, S, D]
                    cos_pe = cos_pe[:, active_mask]
                    sin_pe = sin_pe[:, active_mask]
                elif cos_pe.dim() == 4:         # [3, B, S, D]
                    cos_pe = cos_pe[:, :, active_mask, :]
                    sin_pe = sin_pe[:, :, active_mask, :]
                kwargs["position_embeddings"] = (cos_pe, sin_pe)

        kept = int(active_mask.sum().item())
        self._active_pairs.setdefault(layer_idx if layer_idx is not None else -1, []).append((kept, seq_len))
        self._start_timing(module)
        return args, kwargs

    def forward_post_hook(self, module: nn.Module, inputs, kwargs, output):
        orig_h = getattr(module, "_ls_orig_h", None)
        active_in = getattr(module, "_ls_active_mask", None)
        seq_len = getattr(module, "_ls_seq_len", None)
        layer_idx = getattr(module, "layer_idx", None)

        if orig_h is None or active_in is None or seq_len is None:
            return output
        if orig_h.dim() != 3 or orig_h.shape[1] != active_in.shape[0]:
            return output

        # unpack
        if isinstance(output, tuple):
            layer_out = output[0]
            rest = output[1:]
        else:
            layer_out = output
            rest = ()

        # rebuild full length: inactive positions keep identity
        full_out = orig_h.to(layer_out.device).clone()
        active_in = active_in.to(layer_out.device)
        full_out[:, active_in, :] = layer_out

        cache_position = kwargs.get("cache_position", None)
        in_prefill = self._is_prefill(cache_position, seq_len) if cache_position is not None else True

        # decode: reset
        if not in_prefill:
            self._global_active_mask = None
            self._decision_layer_idx = None
            self._prev_attn_out_full = None

        self._end_timing(module, layer_idx if layer_idx is not None else -1)

        if isinstance(output, tuple):
            return (full_out,) + rest
        return full_out

    # ============================================================
    # B) Attention post-hook: decide mask based on attn_out change
    # ============================================================
    def attn_forward_post_hook(self, module: nn.Module, inputs, kwargs, output):
        """
        Attach to layer.self_attn with with_kwargs=True.

        It does NOT modify attention output. It only:
          - stores attn_out at layer start_layer-1
          - decides global mask at layer start_layer (once)
        """
        layer_idx = getattr(module, "layer_idx", None)
        if layer_idx is None:
            return output

        # unpack attention output
        attn_out = output[0] if isinstance(output, tuple) else output
        if not torch.is_tensor(attn_out):
            return output

        # normalize shape to [B,S,H]
        if attn_out.dim() == 2:       # [S,H]
            attn_out = attn_out.unsqueeze(0)
        if attn_out.dim() != 3:
            return output

        bsz, seq_len, _ = attn_out.shape

        cache_position = kwargs.get("cache_position", None)
        if cache_position is None:
            return output
        in_prefill = self._is_prefill(cache_position, seq_len)
        if not in_prefill:
            return output

        start_layer, end_layer = self._flexible_range(module)
        in_flexible = (start_layer <= layer_idx < end_layer)

        # store prev attn_out at layer start_layer-1
        if layer_idx + 1 == start_layer:
            self._prev_attn_out_full = attn_out.detach().cpu()
            return output

        # decide at start_layer
        need_decide = (
            self.decide_once_in_flexible
            and in_flexible
            and (self._global_active_mask is None)
            and (layer_idx == start_layer)
        )
        if not need_decide:
            return output

        if self._prev_attn_out_full is None:
            return output
        if tuple(self._prev_attn_out_full.shape) != tuple(attn_out.shape):
            return output

        with torch.no_grad():
            prev = self._prev_attn_out_full.to(attn_out.device)
            stability = self._compute_stability(attn_out, prev)  # [S]

            vision_mask = self._vision_mask_on(seq_len, attn_out.device)

            # default: keep all
            active_mask = torch.ones(seq_len, dtype=torch.bool, device=attn_out.device)

            if vision_mask is None:
                eligible = torch.arange(seq_len, device=attn_out.device)
            else:
                # only vision tokens eligible
                eligible = vision_mask.nonzero(as_tuple=False).flatten()

            eligible_len = int(eligible.numel())
            drop_target = int(round(self.compression_ratio * eligible_len)) if eligible_len > 0 else 0

            if drop_target > 0 and eligible_len > 0:
                stab_elig = stability[eligible]
                sorted_idx = torch.argsort(stab_elig, dim=0, descending=False)
                drop_idx = eligible[sorted_idx[:drop_target]]

                # optional threshold gating (disabled by default)
                # if self.stability_threshold > 0:
                #     ok = stab_elig[sorted_idx[:drop_target]] <= self.stability_threshold
                #     drop_idx = drop_idx[ok]

                active_mask[drop_idx] = False

            # non-vision always kept
            if vision_mask is not None:
                active_mask[~vision_mask] = True

            self._global_active_mask = active_mask
            self._decision_layer_idx = layer_idx

            kept = int(active_mask.sum().item())
            print(
                f"[DeltaPress][attn-only] decide@L={layer_idx} S={seq_len} "
                f"eligible={eligible_len} drop={drop_target} kept={kept}/{seq_len} ({kept/seq_len:.2%})"
            )

        return output

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
            lines.append(
                f"  layer {lidx:02d}: avg_active_ratio={avg_ratio:.3f} "
                f"time~{ms:.1f} ms  dmem~{dmem/1024/1024:.2f} MB"
            )
        lines.append(
            f"  avg_skip_ratio={self.skip_ratio:.3%}  est_speedup~{self.speedup_estimate():.2f}x"
        )
        logger.info("\n".join(lines))

    # ----------------------- timing helpers -----------------------
    def _start_timing(self, module):
        if not self.enable_timing or not torch.cuda.is_available():
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
        if not self.enable_timing or not torch.cuda.is_available():
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


# ============================================================
# DeltaPressLNR: (optional) attn+ffn delta based decision (vision-only)
# kept here as a full file. If you don't use it, ignore.
# No forced retention.
# ============================================================
@dataclass
class DeltaPressLNR(BasePress):
    compression_ratio: float = 0.333
    start_ratio: float = 0.4
    end_ratio: float = 1.0

    metric: Literal["cos", "l1", "l2"] = "cos"
    decide_once_in_flexible: bool = True
    order: Literal["first", "second"] = "second"

    stability_threshold: float = 0.0
    enable_timing: bool = False

    def __post_init__(self):
        assert 0.0 <= self.compression_ratio <= 1.0
        assert 0.0 <= self.start_ratio < self.end_ratio <= 1.0
        assert self.metric in ("cos", "l1", "l2")
        assert self.order in ("first", "second")

        self._prev_block_delta: Optional[torch.Tensor] = None  # [B,S,H] CPU
        self._h_in_block: Optional[torch.Tensor] = None        # [B,S,H]
        self._attn_full_delta: Optional[torch.Tensor] = None   # [B,S,H]

        self._global_active_mask: Optional[torch.Tensor] = None
        self._decision_layer_idx: Optional[int] = None

        self._active_pairs: Dict[int, List[Tuple[int, int]]] = {}
        self._timings_ms: Dict[int, float] = {}
        self._mem_deltas: Dict[int, int] = {}

        self._vision_mask_1d: Optional[torch.Tensor] = None

    def set_vision_mask(self, vision_mask_1d: Optional[torch.Tensor]):
        if vision_mask_1d is None:
            self._vision_mask_1d = None
            return
        if not torch.is_tensor(vision_mask_1d) or vision_mask_1d.dim() != 1:
            raise ValueError("vision_mask_1d must be a 1D torch.Tensor [S].")
        self._vision_mask_1d = vision_mask_1d.bool().detach().to("cpu")

    def _vision_mask_on(self, seq_len: int, device) -> Optional[torch.Tensor]:
        if self._vision_mask_1d is None:
            return None
        if self._vision_mask_1d.numel() != seq_len:
            return None
        return self._vision_mask_1d.to(device)

    def _is_prefill(self, cache_position, seq_len: int) -> bool:
        if cache_position is None or not torch.is_tensor(cache_position):
            return True
        try:
            return int(cache_position.min().item()) == 0
        except Exception:
            return True

    def _flexible_range(self, module: nn.Module) -> Tuple[int, int]:
        cfg = getattr(module, "config", None)
        total_layers = getattr(cfg, "num_hidden_layers", 32)
        start_layer = int(total_layers * self.start_ratio)
        end_layer = int(total_layers * self.end_ratio)
        end_layer = max(start_layer + 1, end_layer)
        return start_layer, end_layer

    @staticmethod
    def _cos_1m(x: torch.Tensor, y: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
        x_n = torch.clamp(x.norm(dim=-1), min=eps)
        y_n = torch.clamp(y.norm(dim=-1), min=eps)
        cos = (x * y).sum(dim=-1) / (x_n * y_n)
        cos = torch.clamp(cos, -1.0, 1.0)
        s = 1.0 - cos
        return s.mean(dim=0) if s.dim() == 2 else s

    # ---------------- attention hooks ----------------
    def attn_forward_pre_hook(self, module: nn.Module, args, kwargs):
        hidden_states = kwargs.get("hidden_states", None)
        if hidden_states is None and len(args) > 0 and isinstance(args[0], torch.Tensor):
            hidden_states = args[0]

        cache_position = kwargs.get("cache_position", None)
        layer_idx = getattr(module, "layer_idx", None)
        if hidden_states is None or cache_position is None or layer_idx is None:
            return args, kwargs

        self._h_in_block = hidden_states

        bsz, seq_len, _ = hidden_states.shape
        start_layer, end_layer = self._flexible_range(module)
        in_flexible = start_layer <= layer_idx < end_layer
        in_prefill = self._is_prefill(cache_position, seq_len)

        if layer_idx == 0 and in_prefill:
            self._global_active_mask = None
            self._decision_layer_idx = None
            self._prev_block_delta = None

        if (not in_prefill) or (not in_flexible):
            return args, kwargs

        # apply global mask (if already decided)
        if self._global_active_mask is not None and self._global_active_mask.shape[0] == seq_len:
            active_mask = self._global_active_mask.to(hidden_states.device)
            kept = int(active_mask.sum().item())
            if kept < seq_len:
                new_hidden = hidden_states[:, active_mask, :]

                # update args/kwargs
                if len(args) > 0 and isinstance(args[0], torch.Tensor):
                    args = (new_hidden,) + tuple(args[1:])
                    kwargs.pop("hidden_states", None)
                else:
                    kwargs["hidden_states"] = new_hidden

                # cache_position
                if cache_position.dim() == 1:
                    kwargs["cache_position"] = cache_position[active_mask]
                elif cache_position.dim() == 2:
                    kwargs["cache_position"] = cache_position[:, active_mask]

                # attention_mask
                attn_mask = kwargs.get("attention_mask", None)
                if attn_mask is not None:
                    if attn_mask.dim() == 4:
                        attn_mask = attn_mask[:, :, active_mask, :][:, :, :, active_mask]
                    elif attn_mask.dim() == 3:
                        attn_mask = attn_mask[:, active_mask, :][:, :, active_mask]
                    elif attn_mask.dim() == 2:
                        attn_mask = attn_mask[:, active_mask]
                    kwargs["attention_mask"] = attn_mask

                # position_embeddings
                pos_emb = kwargs.get("position_embeddings", None)
                if isinstance(pos_emb, tuple) and len(pos_emb) == 2:
                    cos_pe, sin_pe = pos_emb
                    if torch.is_tensor(cos_pe) and torch.is_tensor(sin_pe):
                        if cos_pe.dim() == 2:
                            cos_pe = cos_pe[active_mask]
                            sin_pe = sin_pe[active_mask]
                        elif cos_pe.dim() == 3:
                            cos_pe = cos_pe[:, active_mask]
                            sin_pe = sin_pe[:, active_mask]
                        elif cos_pe.dim() == 4:
                            cos_pe = cos_pe[:, :, active_mask, :]
                            sin_pe = sin_pe[:, :, active_mask, :]
                        kwargs["position_embeddings"] = (cos_pe, sin_pe)

        return args, kwargs

    def attn_forward_post_hook(self, module: nn.Module, inputs, kwargs, output):
        hidden_in = self._h_in_block
        if hidden_in is None:
            return output

        layer_out = output[0] if isinstance(output, tuple) else output
        extra = output[1:] if isinstance(output, tuple) else ()

        bsz, seq_len, _ = hidden_in.shape

        if self._global_active_mask is not None and self._global_active_mask.shape[0] == seq_len:
            active_mask = self._global_active_mask.to(hidden_in.device)
        else:
            active_mask = torch.ones(seq_len, dtype=torch.bool, device=hidden_in.device)

        kept = int(active_mask.sum().item())

        # expand attn delta to full length
        full_attn_delta = torch.zeros_like(hidden_in)
        if torch.is_tensor(layer_out):
            if layer_out.dim() == 2:
                layer_out_b = layer_out.unsqueeze(0)
                full_attn_delta[:, active_mask, :] = layer_out_b
            elif layer_out.dim() == 3:
                if layer_out.shape[1] == seq_len:
                    full_attn_delta = layer_out
                else:
                    full_attn_delta[:, active_mask, :] = layer_out
        self._attn_full_delta = full_attn_delta

        return (full_attn_delta,) + extra if isinstance(output, tuple) else full_attn_delta

    # ---------------- FFN hooks ----------------
    def ffn_forward_pre_hook(self, module: nn.Module, args, kwargs):
        return args, kwargs

    def ffn_forward_post_hook(self, module: nn.Module, inputs, kwargs, output):
        h_in_block = self._h_in_block
        attn_full_delta = self._attn_full_delta
        if h_in_block is None or attn_full_delta is None:
            return output

        ffn_out = output[0] if isinstance(output, tuple) else output
        extra = output[1:] if isinstance(output, tuple) else ()

        bsz, seq_len, _ = h_in_block.shape
        layer_idx = getattr(module, "layer_idx", None)
        if layer_idx is None:
            return output

        if self._global_active_mask is not None and self._global_active_mask.shape[0] == seq_len:
            active_mask = self._global_active_mask.to(h_in_block.device)
        else:
            active_mask = torch.ones(seq_len, dtype=torch.bool, device=h_in_block.device)

        kept = int(active_mask.sum().item())
        self._active_pairs.setdefault(layer_idx, []).append((kept, seq_len))

        # expand ffn delta to full length
        full_ffn_delta = torch.zeros_like(h_in_block)
        if torch.is_tensor(ffn_out):
            if ffn_out.dim() == 2:
                full_ffn_delta[:, active_mask, :] = ffn_out.unsqueeze(0)
            elif ffn_out.dim() == 3:
                if ffn_out.shape[1] == seq_len:
                    full_ffn_delta = ffn_out
                else:
                    full_ffn_delta[:, active_mask, :] = ffn_out

        block_delta = attn_full_delta + full_ffn_delta
        block_out = h_in_block + block_delta

        start_layer, end_layer = self._flexible_range(module)
        in_flexible = start_layer <= layer_idx < end_layer

        cache_position = kwargs.get("cache_position", None)
        in_prefill = self._is_prefill(cache_position, seq_len)

        need_decide = (
            self.decide_once_in_flexible
            and in_flexible
            and in_prefill
            and (self._global_active_mask is None)
            and (layer_idx == start_layer)
        )

        if need_decide:
            with torch.no_grad():
                if self.order == "first":
                    stability = self._cos_1m(h_in_block, block_out)
                else:
                    if self._prev_block_delta is not None and self._prev_block_delta.shape == block_delta.shape:
                        stability = self._cos_1m(block_delta, self._prev_block_delta.to(block_delta.device))
                    else:
                        stability = self._cos_1m(h_in_block, block_out)

                vision_mask = self._vision_mask_on(seq_len, h_in_block.device)
                active = torch.ones(seq_len, dtype=torch.bool, device=h_in_block.device)

                if vision_mask is None:
                    eligible = torch.arange(seq_len, device=h_in_block.device)
                else:
                    eligible = vision_mask.nonzero(as_tuple=False).flatten()

                eligible_len = int(eligible.numel())
                drop_target = int(round(self.compression_ratio * eligible_len)) if eligible_len > 0 else 0

                if drop_target > 0 and eligible_len > 0:
                    stab_elig = stability[eligible]
                    sorted_idx = torch.argsort(stab_elig, dim=0, descending=False)
                    drop_idx = eligible[sorted_idx[:drop_target]]
                    active[drop_idx] = False

                if vision_mask is not None:
                    active[~vision_mask] = True

                self._global_active_mask = active
                self._decision_layer_idx = layer_idx
                kept2 = int(active.sum().item())
                print(
                    f"[DeltaPressLNR] decide(vision-only)@L={layer_idx} kept={kept2}/{seq_len} "
                    f"({kept2/seq_len:.2%}), eligible={eligible_len}, drop_target={drop_target}"
                )

        if self.order == "second":
            self._prev_block_delta = block_delta.detach().cpu()

        if not in_prefill:
            self._global_active_mask = None
            self._decision_layer_idx = None
            self._prev_block_delta = None

        return (full_ffn_delta,) + extra if isinstance(output, tuple) else full_ffn_delta

    def compress(self, module, hidden_states, keys, values, attentions, kwargs):
        return keys, values

    # timing helpers (optional)
    def _start_timing(self, module):
        if not self.enable_timing or not torch.cuda.is_available():
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
        if not self.enable_timing or not torch.cuda.is_available():
            return
        ev_start = getattr(module, "_dp_ev_start", None)
        ev_end = getattr(module, "_dp_ev_end", None)
        if ev_start is None or ev_end is None:
            return
        ev_end.record()
        torch.cuda.synchronize()
        dt = ev_start.elapsed_time(ev_end)
        # self._timings_ms[layer_idx] = self._timings_ms.get(layer_idx, 0.0) + float(dt)
        # self._timings_ms[layer_idx] = self._timings_ms.get(layer_idx, 0.0) + float(dt)
        self._timings_ms[layer_idx] = self._timings_ms.get(layer_idx, 0.0) + float(dt)

        mem0 = getattr(module, "_dp_mem0", None)
        if mem0 is not None:
            mem1 = torch.cuda.memory_allocated()
            self._mem_deltas[layer_idx] = self._mem_deltas.get(layer_idx, 0) + int(mem1 - mem0)
        for n in ("_dp_ev_start", "_dp_ev_end", "_dp_mem0"):
            if hasattr(module, n):
                delattr(module, n)
