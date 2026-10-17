# Preference Leakage: A Contamination Problem in LLM-as-a-judge

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/6297baf3f5c98146b62dd3a1bffe068e-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/6297baf3f5c98146b62dd3a1bffe068e-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/6297baf3f5c98146b62dd3a1bffe068e-Paper-Conference.pdf) |
| Official code | [https://github.com/David-Li0406/Preference-Leakage](https://github.com/David-Li0406/Preference-Leakage) |
| Upstream revision | `d6f7fcec4b8719c4b0a87c9b72548b2edb22a8c9` |
| Covered directions | Fault tolerance and recovery, Permissions, approval, and runtime isolation, Verification, evaluation, and feedback |
| Training-free integration boundary | Audit and mitigate contamination between generated data and LLM judges through controlled evaluator comparisons. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
