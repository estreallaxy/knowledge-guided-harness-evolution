# CItruS: Chunked Instruction-aware State Eviction for Long Sequence Modeling

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | EMNLP 2024 |
| Paper | https://aclanthology.org/2024.emnlp-main.338/ |
| Official code | https://github.com/ybai-nlp/CItruS |
| Upstream revision | `3e1c1b1653c9bdfd638665cc192a084520ffd4d3` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Process long input in chunks and evict recurrent/KV states according to their instruction-aware relevance under a fixed state budget. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
