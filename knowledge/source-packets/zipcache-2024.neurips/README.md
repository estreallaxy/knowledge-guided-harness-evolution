# ZipCache: Accurate and Efficient KV Cache Quantization with Salient Token Identification

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2024/hash/7e57131fdeb815764434b65162c88895-Abstract-Conference.html |
| Official code | https://github.com/ThisisBillhe/ZipCache |
| Upstream revision | `8833f675a938b019fccc531bfdf932abe6e622ad` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Estimate token saliency from normalized attention, assign mixed 2/4-bit KV precision, and periodically recompress during decoding. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
