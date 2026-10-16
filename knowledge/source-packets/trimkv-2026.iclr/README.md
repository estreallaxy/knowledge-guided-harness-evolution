# Cache What Lasts: Token Retention for Memory-Bounded KV Cache in LLMs

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/c3887741ee4e655494770be95303383f-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/c3887741ee4e655494770be95303383f-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/c3887741ee4e655494770be95303383f-Paper-Conference.pdf) |
| Official code | [https://github.com/ngocbh/trimkv](https://github.com/ngocbh/trimkv) |
| Upstream revision | `49d2a2951ba12e6431a3986b418ee791b209d7c2` |
| Covered directions | Context management and compression |
| Training-free integration boundary | Retain tokens according to persistence evidence under a fixed inference-time KV-cache budget. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
