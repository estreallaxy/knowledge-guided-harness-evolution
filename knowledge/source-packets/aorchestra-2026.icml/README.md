# AOrchestra: Automating Sub-Agent Creation for Agentic Orchestration

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/ruan26e.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/ruan26e/ruan26e.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/ruan26e/ruan26e.pdf) |
| Official code | [https://github.com/FoundationAgents/AOrchestra](https://github.com/FoundationAgents/AOrchestra) |
| Upstream revision | `14a1a2051d6b03c479b706f8f555a60b8419e3b5` |
| Covered directions | Instructions and skills, Execution loop and scheduling, Planning and progress management, Model selection and resource allocation, Sub-agent and multi-agent collaboration, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Building on this abstraction, we introduce an agentic system AOrchestra, where the central orchestrator concretizes the tuple at each step: it curates task-relevant context, selects tools and models, and delegates execution via on-the-fly automatic agent creation. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
