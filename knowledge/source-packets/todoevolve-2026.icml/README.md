# TodoEvolve: Learning to Architect Agent Planning Systems

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/liu26fz.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/liu26fz/liu26fz.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/liu26fz/liu26fz.pdf) |
| Official code | [https://github.com/EcthelionLiu/TodoEvolve](https://github.com/EcthelionLiu/TodoEvolve) |
| Upstream revision | `3a10c43c1eb6c1b73407d251d605e74695f9e302` |
| Covered directions | Instructions and skills, Execution loop and scheduling, Planning and progress management, Model selection and resource allocation, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Retain PlanFactory, including its modular planning design space and the topology, initialization, adaptation, and navigation interfaces; exclude IGPO and the trained Todo-14B planner. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
