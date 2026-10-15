# ShadowKV: KV Cache in Shadows for High-Throughput Long-Context LLM Inference

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICML 2025 (Spotlight) |
| Paper | https://proceedings.mlr.press/v267/sun25b.html |
| Official code | https://github.com/ByteDance-Seed/ShadowKV |
| Upstream revision | `e51904cdeab7d4d34013370f09f2cf5fcd655e15` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Keep low-rank key representations on GPU, offload full values/keys, and fetch only sparse selected chunks for each query/head. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
