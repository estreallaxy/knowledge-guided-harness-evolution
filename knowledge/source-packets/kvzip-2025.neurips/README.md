# KVzip: Query-Agnostic KV Cache Compression with Context Reconstruction

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2025 (Oral) |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2025/hash/f4eaa4b8f2d08edb3f0af990d56134ea-Abstract-Conference.html |
| Official code | https://github.com/snu-mllab/KVzip |
| Upstream revision | `5d8472975d286e3da6b52178af39d18904330c0d` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Score cached KV pairs by how well they reconstruct the original context, then evict low-importance pairs once for reuse across future queries. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
