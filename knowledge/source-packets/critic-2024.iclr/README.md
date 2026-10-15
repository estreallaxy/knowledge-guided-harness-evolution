# CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2024 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2024/hash/fef126561bbf9d4467dbb8d27334b8fe-Abstract-Conference.html |
| Official code | https://github.com/microsoft/ProphetNet |
| Upstream revision | `5cf70eb41cdaa1d8faa3e1265d95ee5792d49a53` |
| Covered directions | instructions-and-skills, tools-and-environments, long-term-memory-and-experience-reuse, fault-tolerance-and-recovery |
| Training-free integration boundary | Route an initial answer to an appropriate external checker, turn tool output into a grounded critique, revise, and repeat under a stopping rule. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
