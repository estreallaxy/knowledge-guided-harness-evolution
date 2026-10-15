# ReCAP: Recursive Context-Aware Reasoning and Planning for LLM Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2025 |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2025/hash/88af3540325dd0b70617a9ab605f294d-Abstract-Conference.html |
| Official code | https://github.com/ReCAP-Stanford/ReCAP |
| Upstream revision | `2fb112ffad685c7c6f7de86d5487ecca6f566fcc` |
| Covered directions | execution-loop-and-scheduling, planning-and-progress-management, model-selection-and-resource-allocation, session-and-environment-state |
| Training-free integration boundary | Plan-ahead decomposition, execute-head/refine-tail recursion, parent-plan reinjection, bounded active context, and backtracking. Strict pass@1 experiments use frozen API models. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
