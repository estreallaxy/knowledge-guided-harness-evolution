# VideoSEAL: Mitigating Evidence Misalignment in Agentic Long Video Understanding by Decoupling Answer Authority

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/qiu26v.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/qiu26v/qiu26v.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/qiu26v/qiu26v.pdf) |
| Official code | [https://github.com/Echochef/VideoSEAL](https://github.com/Echochef/VideoSEAL) |
| Upstream revision | `d6561c9ab5defacdfe3c28e6a631a2c34a6953aa` |
| Covered directions | Instructions and skills, Fault tolerance and recovery, Planning and progress management, Model selection and resource allocation, Session and environment state management, Sub-agent and multi-agent collaboration, Permissions, approval, and runtime isolation, Extension mechanisms and lifecycle hooks, Runtime observation, traces, and integration interfaces, Verification, evaluation, and feedback |
| Training-free integration boundary | Retain the decoupled planner-inspector architecture, temporal and semantic groundedness diagnostics, pixel-level verification gate, and interpretable search trajectories; exclude outcome-only training. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
