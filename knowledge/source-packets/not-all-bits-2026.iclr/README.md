# Not All Bits Are Equal: Scale-Dependent Memory Optimization Strategies for Reasoning Models

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/71f003060ce1e8b6b4856023b67cda5d-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/71f003060ce1e8b6b4856023b67cda5d-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/71f003060ce1e8b6b4856023b67cda5d-Paper-Conference.pdf) |
| Official code | [https://github.com/krafton-ai/not-all-bits-are-equal](https://github.com/krafton-ai/not-all-bits-are-equal) |
| Upstream revision | `1c01319ad4d4069c8c0704ad965f25e079c4926f` |
| Covered directions | Context management and compression, Model selection and resource allocation |
| Training-free integration boundary | Allocate inference memory between model weights and KV cache according to model scale, task, and measured accuracy-throughput trade-offs. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
