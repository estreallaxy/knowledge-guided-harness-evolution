# LightWM: Training-Free Hierarchical Working Memory for Small Language Model Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/wang26cv.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/wang26cv/wang26cv.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/wang26cv/wang26cv.pdf) |
| Official code | [https://github.com/BloomChant/LightWM](https://github.com/BloomChant/LightWM) |
| Upstream revision | `636f5f3893767e8ffa1ccaea152ef4adc8da370e` |
| Covered directions | Instructions and skills, Context management and compression, Long-term memory and experience reuse, Execution loop and scheduling, Planning and progress management, Model selection and resource allocation, Session and environment state management, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Retain the global/local structured working-memory hierarchy and one-time schema induction from successful traces; the selected mechanism requires no model-parameter update. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
