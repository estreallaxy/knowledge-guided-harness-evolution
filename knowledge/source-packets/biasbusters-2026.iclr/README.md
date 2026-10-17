# BiasBusters: Uncovering and Mitigating Tool Selection Bias in Large Language Models

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a79875cc0d046ce7ce65f03f3affaa9e-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/a79875cc0d046ce7ce65f03f3affaa9e-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/a79875cc0d046ce7ce65f03f3affaa9e-Paper-Conference.pdf) |
| Official code | [https://github.com/thierry123454/tool-selection-bias](https://github.com/thierry123454/tool-selection-bias) |
| Upstream revision | `bdebc4ae796509222be24c7e985ebe183aa280f0` |
| Covered directions | Fault tolerance and recovery, Permissions, approval, and runtime isolation |
| Training-free integration boundary | Measure provider-selection bias and apply inference-time tool presentation and selection controls; exclude model-training paths. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
