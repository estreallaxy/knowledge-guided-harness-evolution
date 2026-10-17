# Towards Feedback-to-Plan Decisions for Self-Evolving LLM Agents in CUDA Kernel Generation

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/chong26b.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/chong26b/chong26b.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/chong26b/chong26b.pdf) |
| Official code | [https://github.com/yuxuan-z19/cudanalyst](https://github.com/yuxuan-z19/cudanalyst) |
| Upstream revision | `3c56c68775e8a7cf67e3fc935241030abb8822bb` |
| Covered directions | Long-term memory and experience reuse, Execution loop and scheduling, Planning and progress management |
| Training-free integration boundary | We introduce CUDAnalyst, a unified analysis layer for controlled, generation-level attribution of planning decisions to feedback components via trajectory freezing and selective feedback injection. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
