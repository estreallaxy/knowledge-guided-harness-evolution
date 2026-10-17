# SafeHarbor: Defining Precise Decision Boundaries via Hierarchical Memory-Augmented Guardrail for LLM Agent Safety

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/liu26fn.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/liu26fn/liu26fn.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/liu26fn/liu26fn.pdf) |
| Official code | [https://github.com/ljj-cyber/SafeHarbor](https://github.com/ljj-cyber/SafeHarbor) |
| Upstream revision | `4aa2be3bce7117739950b0de8ad4a5cebd1f81d7` |
| Covered directions | Instructions and skills, Long-term memory and experience reuse, Fault tolerance and recovery, Execution loop and scheduling, Session and environment state management, Permissions, approval, and runtime isolation, Extension mechanisms and lifecycle hooks, Runtime observation, traces, and integration interfaces, Verification, evaluation, and feedback |
| Training-free integration boundary | Retain context-aware defense-rule extraction, hierarchical local memory, dynamic rule injection, and entropy-driven node splitting and merging; the selected guardrail is training-free. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
