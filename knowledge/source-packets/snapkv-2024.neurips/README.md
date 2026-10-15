# SnapKV: LLM Knows What You are Looking for Before Generation

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2024/hash/28ab418242603e0f7323e54185d19bde-Abstract-Conference.html |
| Official code | https://github.com/FasterDecoding/SnapKV |
| Upstream revision | `e216ddc84c5bd210378cbdbbba12ba02102aa640` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Use an observation window to estimate head-specific salient prompt positions, pool nearby positions, and retain only the selected KV cache. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
