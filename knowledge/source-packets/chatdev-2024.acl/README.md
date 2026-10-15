# ChatDev: Communicative Agents for Software Development

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ACL 2024 |
| Paper | https://aclanthology.org/2024.acl-long.810/ |
| Official code | https://github.com/OpenBMB/ChatDev |
| Upstream revision | `4fb2db0ea90375ce1059f44fe03ffbd191a7a169` |
| Covered directions | execution-loop-and-scheduling, planning-and-progress-management, session-and-environment-state, subagents-and-multiagent-collaboration |
| Training-free integration boundary | Phase/subtask chat chain, instructor–assistant role pairs, communicative dehallucination, and executable review/test feedback. Uses prompted agents without model training. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
