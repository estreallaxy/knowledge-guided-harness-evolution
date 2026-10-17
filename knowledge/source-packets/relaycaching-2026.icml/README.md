# RelayCaching: Accelerating LLM Collaboration via Decoding KV Cache Reuse

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/geng26a.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/geng26a/geng26a.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/geng26a/geng26a.pdf) |
| Official code | [https://github.com/YingshengGeng/RelayCaching](https://github.com/YingshengGeng/RelayCaching) |
| Upstream revision | `6b0e9d37b74d89cfb0fbad276790150a0d9c0b49` |
| Covered directions | Context management and compression, Model selection and resource allocation |
| Training-free integration boundary | We present RelayCaching, a training-free inference method that directly reuses decoding phase KV caches from previous agents in subsequent prefill phases. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
