# PinTok: Tokenizers Deserve Dedicated Pinned CPU-Compute and Memory

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/choi26b.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/choi26b/choi26b.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/choi26b/choi26b.pdf) |
| Official code | [https://github.com/The-Cloud-Lab/PinTok](https://github.com/The-Cloud-Lab/PinTok) |
| Upstream revision | `92572ede9a9c17b7a14813c44449daee8514dac9` |
| Covered directions | Context management and compression, Model selection and resource allocation |
| Training-free integration boundary | In this paper, we present the Pinned Tokenizer (PinTok), a novel tokenizer architecture that reduces redundant hardware, operating system, and networking overhead through three key innovations: core and memory pinning, scheduling and context switch avoidance, and duplicate network packet copy and processing avoidance. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
