# Long-Context Modeling with Dynamic Hierarchical Sparse Attention for Memory-Constrained LLM Inference

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/xiong26q.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/xiong26q/xiong26q.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/xiong26q/xiong26q.pdf) |
| Official code | [https://github.com/xiongsiheng/DHSA](https://github.com/xiongsiheng/DHSA) |
| Upstream revision | `069d55321df04257840e9477489e7db34f7bceb0` |
| Covered directions | Context management and compression, Model selection and resource allocation, Session and environment state management |
| Training-free integration boundary | We propose Dynamic Hierarchical Sparse Attention (DHSA), a data-driven framework that predicts attention sparsity online while keeping the LLM backbone frozen. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
