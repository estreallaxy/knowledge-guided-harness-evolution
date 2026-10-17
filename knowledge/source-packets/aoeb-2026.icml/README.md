# AOEB: Benchmarking Agent-Oriented Multimodal Embeddings

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/zhang26hf.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/zhang26hf/zhang26hf.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/zhang26hf/zhang26hf.pdf) |
| Official code | [https://github.com/vec-ai/aoeb](https://github.com/vec-ai/aoeb) |
| Upstream revision | `259eb6eb89a2764a696fabd4b5ba9e6abb2f3670` |
| Covered directions | Model selection and resource allocation, Runtime observation, traces, and integration interfaces, Verification, evaluation, and feedback |
| Training-free integration boundary | Retain the agent-oriented retrieval task taxonomy, task configurations, and evaluator covering code, tool, reasoning, and memory retrieval; no embedding model is trained. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
