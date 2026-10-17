# Helpful to a Fault: Measuring Illicit Assistance in Multi-Turn, Multilingual LLM Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/talokar26a.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/talokar26a/talokar26a.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/talokar26a/talokar26a.pdf) |
| Official code | [https://github.com/epfl-nlp/helpful-to-a-fault](https://github.com/epfl-nlp/helpful-to-a-fault) |
| Upstream revision | `c8053cf60737b3c43b24ec927ad77b995986a4c9` |
| Covered directions | Fault tolerance and recovery, Permissions, approval, and runtime isolation |
| Training-free integration boundary | We introduce STING ( Sequential Testing of Illicit N-step Goal execution ), an automated red-teaming framework that constructs a step-by-step illicit plan grounded in a benign persona and iteratively probes a target agent with adaptive follow-ups, using judge agents to track phase completion. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
