# A Theoretical Understanding of Self-Correction through In-context Alignment

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2024/hash/a399456a191ca36c7c78dff367887f0a-Abstract-Conference.html |
| Official code | https://github.com/yifeiwang77/Self-Correction |
| Upstream revision | `435d592fafa3bd817e07e16b1afa906620464da4` |
| Covered directions | instructions-and-skills, fault-tolerance-and-recovery |
| Training-free integration boundary | Keep a model-generated check as explicit context (Checking-as-Context) and condition the next attempt on that evidence rather than invoking ungrounded self-correction. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
