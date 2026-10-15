# AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | 2025, ICLR |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2025/hash/c493d23af93118975cdbc32cbe7323f5-Abstract-Conference.html |
| Official code | https://github.com/UKGovernmentBEIS/inspect_evals |
| Upstream revision | `d2d3aac91a37a8c7c8ed3de8b4e899c2594f24a9` |
| Covered directions | permissions-approval-and-isolation, verification-evaluation-and-feedback |
| Training-free integration boundary | Proxy-tool environment, harmful/benign paired tasks, capability-aware safety scoring, narrow rubrics, and held-out task handling. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
