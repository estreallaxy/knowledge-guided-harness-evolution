# FreeKV: Boosting KV Cache Retrieval for Efficient LLM Inference

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/5137e40ee586c4f1fc3615cf8cee4f87-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/5137e40ee586c4f1fc3615cf8cee4f87-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/5137e40ee586c4f1fc3615cf8cee4f87-Paper-Conference.pdf) |
| Official code | [https://github.com/sjtu-zhao-lab/FreeKV](https://github.com/sjtu-zhao-lab/FreeKV) |
| Upstream revision | `2c8a7d25c9f3c7c15ce15b2f84cd03f477bd7469` |
| Covered directions | Context management and compression |
| Training-free integration boundary | Retrieve and retain useful KV-cache entries at inference time without training a new compressor. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
