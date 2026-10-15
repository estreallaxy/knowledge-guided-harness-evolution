# Hierarchical Context Merging: Better Long Context Understanding for Pre-trained LLMs

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2024 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2024/hash/06694da057cb15fef11542270a592627-Abstract-Conference.html |
| Official code | https://github.com/alinlab/HOMER |
| Upstream revision | `822ef84ad77999657ee14ba4aa03c5c9fcc6988d` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Split context, process chunks, repeatedly merge/prune KV representations into a fixed target budget, then decode from the compact prefix. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
