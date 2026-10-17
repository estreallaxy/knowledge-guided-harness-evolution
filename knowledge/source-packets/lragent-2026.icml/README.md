# LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/jeon26b.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/jeon26b/jeon26b.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/jeon26b/jeon26b.pdf) |
| Official code | [https://github.com/hjeon2k/LRAgent](https://github.com/hjeon2k/LRAgent) |
| Upstream revision | `578ff6021127d827bc46e0b00b0f62b0c32dd56c` |
| Covered directions | Context management and compression, Model selection and resource allocation |
| Training-free integration boundary | Retain runtime KV-cache decomposition, shared-base cache management, low-rank adapter-cache storage, and Flash-LoRA-Attention; existing adapters are inputs and are not trained by the selected mechanism. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
