# A Dynamic LLM-Powered Agent Network for Task-Oriented Agent Collaboration (DyLAN)

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | COLM 2024 |
| Paper | https://openreview.net/forum?id=XII0Wp1XA9 |
| Official code | https://github.com/SALT-NLP/DyLAN |
| Upstream revision | `006e440a519f7cf21e2826f3b8033d84ae9bf07c` |
| Covered directions | model-selection-and-resource-allocation, subagents-and-multiagent-collaboration |
| Training-free integration boundary | Unsupervised Agent Importance Score, task/domain team selection, dynamic communication, and early stopping. Optimization is over the agent network at inference time, not model weights. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
