# Is Self-Repair a Silver Bullet for Code Generation?

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2024 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2024/hash/9ddc141bdbf9d1db510cefff56c586ad-Abstract-Conference.html |
| Official code | https://github.com/theoxo/self-repair |
| Upstream revision | `fcda7a193a732d89fc1f610074c719682228fbc4` |
| Covered directions | instructions-and-skills, fault-tolerance-and-recovery |
| Training-free integration boundary | Budget a generate–execute–diagnose–repair loop and use measured error/test feedback; compare repair against fresh sampling at equal token budget. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
