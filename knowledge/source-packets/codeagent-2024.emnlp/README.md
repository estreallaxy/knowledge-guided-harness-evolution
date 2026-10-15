# CodeAgent: Autonomous Communicative Agents for Code Review

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | EMNLP 2024 |
| Paper | https://aclanthology.org/2024.emnlp-main.632/ |
| Official code | https://github.com/Daniel4SE/codeagent |
| Upstream revision | `e61f419affcaec6ccde63d63e894bcb06bedcc60` |
| Covered directions | planning-and-progress-management, model-selection-and-resource-allocation, subagents-and-multiagent-collaboration |
| Training-free integration boundary | Specialized review roles plus a QA-Checker supervisor that checks relevance to the original question before aggregation. Ablations compare agent/supervisor contributions. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
