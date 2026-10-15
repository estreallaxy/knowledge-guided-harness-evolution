# PRompt Optimization in Multi-Step Tasks (PROMST): Integrating Human Feedback and Heuristic-based Sampling

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | EMNLP 2024 |
| Paper | https://aclanthology.org/2024.emnlp-main.226/ |
| Official code | https://github.com/yongchao98/PROMST |
| Upstream revision | `64a0785e7520cb775980596d315394c05cd92d9c` |
| Covered directions | instructions-and-skills, long-term-memory-and-experience-reuse |
| Training-free integration boundary | Convert multi-step execution failures into structured feedback rules and let an LLM revise the task prompt; retain only the rule-conditioned revision path. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
