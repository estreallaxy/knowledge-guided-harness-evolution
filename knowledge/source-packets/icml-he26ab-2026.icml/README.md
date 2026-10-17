# Understand and Accelerate Memory Processing Pipeline for Large Language Model Inference

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/he26ab.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26ab/he26ab.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/he26ab/he26ab.pdf) |
| Official code | [https://github.com/OswaldHe/HeteroLLM](https://github.com/OswaldHe/HeteroLLM) |
| Upstream revision | `71524a94fc48c08d349fcbc47ced6e51581754a6` |
| Covered directions | Context management and compression, Long-term memory and experience reuse, Execution loop and scheduling, Model selection and resource allocation |
| Training-free integration boundary | Retain the four-stage memory-processing interface—Prepare Memory, Compute Relevancy, Retrieval, and Apply to Inference—and its stage-wise profiling and heterogeneous dispatch logic. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
