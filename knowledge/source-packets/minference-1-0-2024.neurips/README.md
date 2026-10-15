# MInference 1.0: Accelerating Pre-filling for Long-Context LLMs via Dynamic Sparse Attention

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://openreview.net/forum?id=fPBACAbqSN |
| Official code | https://github.com/microsoft/MInference |
| Upstream revision | `29ef1974fcb5a1440ccf92d7d7996900230fddcf` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Profile attention patterns, choose sparse templates, and dynamically build sparse indices for each prompt during prefill. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
