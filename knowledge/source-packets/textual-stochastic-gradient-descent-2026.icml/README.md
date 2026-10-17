# Textual Stochastic Gradient Descent: Discrete Optimization of External Memory for Reasoning Language Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/li26bo.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/li26bo/li26bo.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/li26bo/li26bo.pdf) |
| Official code | [https://github.com/superlj666/TSGD](https://github.com/superlj666/TSGD) |
| Upstream revision | `bf7b467d2151e3d26d3543ba01322fd29c8f518f` |
| Covered directions | Instructions and skills, Context management and compression, Long-term memory and experience reuse, Model selection and resource allocation, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Retain the capacity-bounded external experience library and the failure-driven textual Add, Edit, and Delete operations with dual verification; textual gradients modify external memory, not model parameters. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
