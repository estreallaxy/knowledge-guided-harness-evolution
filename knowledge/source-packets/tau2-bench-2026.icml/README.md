# $τ^2$-Bench: Evaluating Conversational Agents in a Dual-Control Environment

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/barres26a.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/barres26a/barres26a.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/barres26a/barres26a.pdf) |
| Official code | [https://github.com/sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench) |
| Upstream revision | `96a3ef92329baf908ffe9dfe188cea34e8701d2a` |
| Covered directions | Tools and environment interaction, Execution loop and scheduling, Session and environment state management, Verification, evaluation, and feedback |
| Training-free integration boundary | In order to address this gap, we introduce $\tau^2$-bench, with four key contributions: (1) A novel Telecom dual-control domain modeled as a Dec-POMDP, where both agent and user make use of tools to act in a shared, dynamic environment that tests both agent coordination and communication; (2) A compositional task generator that programmatically creates diverse, verifiable tasks from atomic components, ensuring domain coverage and controlled complexity; (3) A reliable user simulator tightly coupled with the environment, whose behavior is constrained by tools and observable states, improving simulation fidelity; (4) Fine-grained analysis of agent performance through multiple ablations includin |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
