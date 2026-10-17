# Locomo-Plus: Beyond-Factual Cognitive Memory Evaluation Framework for LLM Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ACL 2026](https://aclanthology.org/2026.acl-long.1150/) |
| Publication date | 2026-07-05 |
| Paper | [https://aclanthology.org/2026.acl-long.1150.pdf](https://aclanthology.org/2026.acl-long.1150.pdf) |
| Official code | [https://github.com/xjtuleeyf/Locomo-Plus](https://github.com/xjtuleeyf/Locomo-Plus) |
| Upstream revision | `059f4e3d38f7f1f96765e8e2cb7de3097551bffb` |
| Covered directions | Long-term memory and experience reuse, Session and environment state management, Verification, evaluation, and feedback |
| Training-free integration boundary | Long-term conversational memory is a core capability for LLM-baseddialogue systems, yet existing benchmarks and evaluation protocolsprimarily focus on surface-level factual recall.In realistic interactions, appropriate responses often depend onimplicit constraints such as user state, goals, or values that are notexplicitly queried later.To evaluate this setting, we introduce LoCoMo-Plus , a benchmarkfor assessing cognitive memory under cue–trigger semantic disconnect,where models must retain and apply latent constraints across longconversational contexts.We further show that conventional string-matching metrics and explicittask-type prompting are misaligned with such scenarios, and propose aunified evaluation framework based on constraint consistency.Experiments across diverse backbone mod |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
