# Just-In-Time Reinforcement Learning: Continual Learning in LLM Agents Without Gradient Updates

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/li26cv.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/li26cv/li26cv.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/li26cv/li26cv.pdf) |
| Official code | [https://github.com/liushiliushi/JitRL](https://github.com/liushiliushi/JitRL) |
| Upstream revision | `143d22185d95fbf633a0befe6861d5e8b732543b` |
| Covered directions | Long-term memory and experience reuse, Model selection and resource allocation, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Retain the dynamic non-parametric trajectory memory, on-the-fly advantage estimation, and inference-time logit modulation; the selected mechanism performs no gradient update or parameter training. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
