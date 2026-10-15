# Efficient Streaming Language Models with Attention Sinks

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2024 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2024/hash/5e5fd18f863cbe6d8ae392a93fd271c9-Abstract-Conference.html |
| Official code | https://github.com/mit-han-lab/streaming-llm |
| Upstream revision | `2e5042606d69933d88fbf909bd77907456b9b4dd` |
| Covered directions | context-management-and-compression |
| Training-free integration boundary | Retain initial attention-sink tokens plus a rolling recent-token window to support stable unbounded streaming inference. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
