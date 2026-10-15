# InfLLM: Training-Free Long-Context Extrapolation for LLMs with an Efficient Context Memory

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2024/hash/d842425e4bf79ba039352da0f658a906-Abstract-Conference.html |
| Official code | https://github.com/thunlp/InfLLM |
| Upstream revision | `12b70798f56e56ebb23c53c7018091a3f540a028` |
| Covered directions | context-management-and-compression, long-term-memory-and-experience-reuse |
| Training-free integration boundary | Move distant tokens into memory units and retrieve query-relevant units into a bounded active attention window. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
