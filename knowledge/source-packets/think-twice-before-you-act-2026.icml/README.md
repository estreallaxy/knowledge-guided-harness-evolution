# Think Twice Before You Act: Protecting LLM Agents Against Tool Description Poisoning via Isolated Planning

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/shi26ab.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/shi26ab/shi26ab.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/shi26ab/shi26ab.pdf) |
| Official code | [https://github.com/shishishi123/Tool-Guard](https://github.com/shishishi123/Tool-Guard) |
| Upstream revision | `b70f711d8710251a7c2503eff6582aff7d731eff` |
| Covered directions | Instructions and skills, Fault tolerance and recovery, Permissions, approval, and runtime isolation |
| Training-free integration boundary | Building on this insight, we propose Tool-Guard, a novel system-level defense based on a new concept called isolated planning , in which tool invocations that are detected as misaligned or suspicious cause the corresponding tool to be placed in a quarantined list (the influenced list ), breaking further influence from poisoned descriptions. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
