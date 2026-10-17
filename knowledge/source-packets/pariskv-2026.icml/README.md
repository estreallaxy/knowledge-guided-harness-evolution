# ParisKV: Fast and Drift-Robust KV-Cache Retrieval for Long-Context LLMs

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/qi26b.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/qi26b/qi26b.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/qi26b/qi26b.pdf) |
| Official code | [https://github.com/amy-77/ParisKV](https://github.com/amy-77/ParisKV) |
| Upstream revision | `db7ad7f59ebe5670f9f2e1092b1b689802dda7c5` |
| Covered directions | Context management and compression, Model selection and resource allocation |
| Training-free integration boundary | We introduce ParisKV , a drift-robust, GPU-native KV-cache retrieval framework based on collision-based candidate selection, followed by a quantized inner-product reranking estimator. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
