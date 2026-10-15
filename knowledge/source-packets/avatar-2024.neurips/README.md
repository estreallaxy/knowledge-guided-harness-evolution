# AvaTaR: Optimizing LLM Agents for Tool Usage via Contrastive Reasoning

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://arxiv.org/abs/2406.11200 |
| Official code | https://github.com/zou-group/avatar |
| Upstream revision | `244a0546fc4e882d3ab0f2e2670d66f89acac92f` |
| Covered directions | instructions-and-skills, tools-and-environments, long-term-memory-and-experience-reuse |
| Training-free integration boundary | Contrast high- and low-performing traces, attribute performance gaps to tool-use decisions, and update actor instructions with comparator-generated rules. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
