# ScaleSim: Serving Large-Scale Multi-Agent Simulation with Invocation Distance-Based Memory Management

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/pan26k.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/pan26k/pan26k.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/pan26k/pan26k.pdf) |
| Official code | [https://github.com/PanZaifeng/KVFlow](https://github.com/PanZaifeng/KVFlow) |
| Upstream revision | `7ef897eaedc16626a281ccfe0d453fae80251e8f` |
| Covered directions | Long-term memory and experience reuse, Execution loop and scheduling, Model selection and resource allocation, Session and environment state management, Sub-agent and multi-agent collaboration |
| Training-free integration boundary | Based on an analysis of representative workload classes, we introduce invocation distance, a unified abstraction that estimates the relative order in which agents will issue future LLM requests. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
