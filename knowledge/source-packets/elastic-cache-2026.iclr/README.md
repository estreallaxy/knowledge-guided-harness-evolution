# Attention Is All You Need for KV Cache in Diffusion LLMs

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/3afaa2102fb8ea44cbadc13e45bba718-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/3afaa2102fb8ea44cbadc13e45bba718-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/3afaa2102fb8ea44cbadc13e45bba718-Paper-Conference.pdf) |
| Official code | [https://github.com/VILA-Lab/Elastic-Cache](https://github.com/VILA-Lab/Elastic-Cache) |
| Upstream revision | `1960d8fc6231205a1ae4ebba3898d475e339f7e1` |
| Covered directions | Context management and compression |
| Training-free integration boundary | Adapt KV-cache allocation for diffusion language-model inference using attention-derived cache utility. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
