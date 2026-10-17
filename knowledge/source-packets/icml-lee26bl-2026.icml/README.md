# How to Correctly Report LLM-as-a-Judge Evaluations

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/lee26bl.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/lee26bl/lee26bl.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/lee26bl/lee26bl.pdf) |
| Official code | [https://github.com/UW-Madison-Lee-Lab/LLM-judge-reporting](https://github.com/UW-Madison-Lee-Lab/LLM-judge-reporting) |
| Upstream revision | `082884d075188bed2f2645234fa2cc3050a517c5` |
| Covered directions | Fault tolerance and recovery, Model selection and resource allocation, Runtime observation, traces, and integration interfaces, Verification, evaluation, and feedback |
| Training-free integration boundary | We propose a simple plug-in framework that corrects this bias and enables statistically principled uncertainty quantification. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
