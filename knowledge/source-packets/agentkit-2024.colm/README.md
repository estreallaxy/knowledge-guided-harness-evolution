# AgentKit: Structured LLM Reasoning with Dynamic Graphs

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | COLM 2024 |
| Paper | https://arxiv.org/abs/2404.11483 |
| Official code | https://github.com/holmeswww/agentkit |
| Upstream revision | `c77e8e9ad59f9ca7142d62be73f341b2991c9003` |
| Covered directions | execution-loop-and-scheduling, planning-and-progress-management, model-selection-and-resource-allocation, session-and-environment-state |
| Training-free integration boundary | Explicit dependency graph of prompt nodes, topological evaluation, reusable subgraphs, token accounting, and context-overflow handling. The graph executor is entirely inference-time. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
