# PM-KVQ: Progressive Mixed-precision KV Cache Quantization for Long-CoT LLMs

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/afb8caec018d3c8f6ef8b81fa52386fe-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/afb8caec018d3c8f6ef8b81fa52386fe-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/afb8caec018d3c8f6ef8b81fa52386fe-Paper-Conference.pdf) |
| Official code | [https://github.com/thu-nics/PM-KVQ](https://github.com/thu-nics/PM-KVQ) |
| Upstream revision | `c8a2bff80628a3c476c057aa42e13d5e5c55196f` |
| Covered directions | Context management and compression, Model selection and resource allocation |
| Training-free integration boundary | Apply post-training progressive mixed-precision KV-cache quantization across layers and tokens for long reasoning traces. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
