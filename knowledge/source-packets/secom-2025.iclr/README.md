# SeCom: On Memory Construction and Retrieval for Personalized Conversational Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2025 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2025/hash/e56f394bbd4f0ec81393d767caa5a31b-Abstract-Conference.html |
| Official code | https://github.com/microsoft/SeCom |
| Upstream revision | `1738e563b5dc7c51df762247e3d0379f1132ad23` |
| Covered directions | context-management-and-compression, long-term-memory-and-experience-reuse |
| Training-free integration boundary | Segment conversations by topical coherence, compress each memory unit to remove retrieval noise, and retrieve via BM25/vector backends through one memory API. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
