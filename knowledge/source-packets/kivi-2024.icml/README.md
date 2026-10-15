# KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICML 2024 |
| Paper | https://proceedings.mlr.press/v235/liu24bz.html |
| Official code | https://github.com/jy-yuan/KIVI |
| Upstream revision | `876b4d2d08e3b1d5f70d0969c299d8c7c42ddfb6` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Quantize key cache per channel and value cache per token while preserving a recent full-precision residual window. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
