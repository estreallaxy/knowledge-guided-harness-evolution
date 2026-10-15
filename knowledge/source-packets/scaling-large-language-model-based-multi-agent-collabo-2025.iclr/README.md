# Scaling Large Language Model-based Multi-Agent Collaboration (MacNet)

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2025 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2025/hash/66a026c0d17040889b50f0dfa650e5e0-Abstract-Conference.html |
| Official code | https://github.com/OpenBMB/ChatDev |
| Upstream revision | `e7a35824fd683ffe8fc237e28ecc47d7b1a5da63` |
| Covered directions | model-selection-and-resource-allocation, subagents-and-multiagent-collaboration |
| Training-free integration boundary | Agents are placed in a DAG and executed in topological order; topology and agent count control parallelism, communication, and cost. No model training is part of the mechanism. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
