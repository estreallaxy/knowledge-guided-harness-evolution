import torch

try:
    import triton
    import triton.language as tl

    _TRITON_AVAILABLE = True
except Exception:
    triton = None
    tl = None
    _TRITON_AVAILABLE = False


def triton_is_available() -> bool:
    return _TRITON_AVAILABLE


def require_triton():
    if not _TRITON_AVAILABLE:
        raise RuntimeError(
            "Triton is not available. Please `pip install triton` with a supported CUDA stack."
        )


if _TRITON_AVAILABLE:

    @triton.jit
    def _v_score_kernel(
        A_ptr,
        V_ptr,
        OUT_ptr,
        P: tl.constexpr,
        Qw: tl.constexpr,
        D: tl.constexpr,
        stride_Ah: tl.constexpr,
        stride_Aq: tl.constexpr,
        stride_Ap: tl.constexpr,
        stride_Vh: tl.constexpr,
        stride_Vp: tl.constexpr,
        stride_Vd: tl.constexpr,
        stride_Oh: tl.constexpr,
        stride_Op: tl.constexpr,
        BLOCK_P: tl.constexpr,
        BLOCK_D: tl.constexpr,
    ):
        pid_p = tl.program_id(0)
        pid_h = tl.program_id(1)

        p = pid_p * BLOCK_P + tl.arange(0, BLOCK_P)
        p_mask = p < P

        attention_norm = tl.zeros([BLOCK_P], dtype=tl.float32)
        for q in range(Qw):
            attention = tl.load(
                A_ptr + pid_h * stride_Ah + q * stride_Aq + p * stride_Ap,
                mask=p_mask,
                other=0.0,
            ).to(tl.float32)
            attention_norm += attention * attention

        value_norm = tl.zeros([BLOCK_P], dtype=tl.float32)
        for d0 in range(0, D, BLOCK_D):
            d = d0 + tl.arange(0, BLOCK_D)
            value = tl.load(
                V_ptr
                + pid_h * stride_Vh
                + p[:, None] * stride_Vp
                + d[None, :] * stride_Vd,
                mask=p_mask[:, None] & (d[None, :] < D),
                other=0.0,
            ).to(tl.float32)
            value_norm += tl.sum(value * value, axis=1)

        tl.store(
            OUT_ptr + pid_h * stride_Oh + p * stride_Op,
            attention_norm * value_norm,
            mask=p_mask,
        )

else:
    _v_score_kernel = None


def get_kernel_launch_config(num_positions: int, head_dim: int) -> tuple[int, int]:
    block_p = 128 if num_positions < 2048 else 256
    block_d = 64 if head_dim == 128 else 32
    return block_p, block_d


def run_v_score_kernel(attention: torch.Tensor, values: torch.Tensor) -> torch.Tensor:
    batch_size, num_heads, _, num_positions = attention.shape
    _, _, num_positions_values, head_dim = values.shape
    assert num_positions_values == num_positions

    block_p, block_d = get_kernel_launch_config(num_positions, head_dim)
    grid = (triton.cdiv(num_positions, block_p), num_heads)
    outputs = []

    for batch_idx in range(batch_size):
        batch_attention = attention[batch_idx].contiguous()
        batch_values = values[batch_idx].contiguous()
        batch_output = torch.empty(
            (num_heads, num_positions),
            device=attention.device,
            dtype=torch.float32,
        )
        _v_score_kernel[grid](
            batch_attention,
            batch_values,
            batch_output,
            P=num_positions,
            Qw=batch_attention.shape[1],
            D=head_dim,
            stride_Ah=batch_attention.stride(0),
            stride_Aq=batch_attention.stride(1),
            stride_Ap=batch_attention.stride(2),
            stride_Vh=batch_values.stride(0),
            stride_Vp=batch_values.stride(1),
            stride_Vd=batch_values.stride(2),
            stride_Oh=batch_output.stride(0),
            stride_Op=batch_output.stride(1),
            BLOCK_P=block_p,
            BLOCK_D=block_d,
            num_warps=4 if block_p == 128 else 8,
        )
        outputs.append(batch_output)

    return torch.stack(outputs, dim=0)


def triton_v_score(attention: torch.Tensor, values: torch.Tensor) -> torch.Tensor:
    require_triton()
    attention = attention.contiguous()
    values = values.contiguous()
    assert attention.dtype in (torch.float16, torch.bfloat16)
    assert values.dtype in (torch.float16, torch.bfloat16)
    return run_v_score_kernel(attention, values)
