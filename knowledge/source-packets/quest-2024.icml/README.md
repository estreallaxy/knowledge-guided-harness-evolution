# Quest: Query-Aware Sparsity for Efficient Long-Context LLM Inference

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICML 2024 |
| Paper | https://proceedings.mlr.press/v235/tang24l.html |
| Official code | https://github.com/mit-han-lab/Quest |
| Upstream revision | `01c1623bf9395009520874e989e29f683203b357` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Store per-page key minima/maxima, estimate query-dependent page criticality, and load only top-k KV pages for attention. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
