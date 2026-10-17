# Stochastic Sparse Attention for Memory-Bound Inference

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/lee26j.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/lee26j/lee26j.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/lee26j/lee26j.pdf) |
| Official code | [https://github.com/OPUSLab/SANTA](https://github.com/OPUSLab/SANTA) |
| Upstream revision | `2e5f861196ec3d634d4b64729609fa7d687937b5` |
| Covered directions | Context management and compression, Model selection and resource allocation |
| Training-free integration boundary | We present Stochastic Additive No-mulT Attention (SANTA), a method that sparsifies value-cache access by sampling $S \ll n_k$ indices from the post-softmax distribution and aggregates only those value rows. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
