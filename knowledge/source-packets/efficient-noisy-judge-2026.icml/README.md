# Efficient Inference for Noisy LLM-as-a-Judge Evaluation

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/chen26cq.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/chen26cq/chen26cq.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/chen26cq/chen26cq.pdf) |
| Official code | [https://github.com/yiqunchen/debias-llm-as-a-judge](https://github.com/yiqunchen/debias-llm-as-a-judge) |
| Upstream revision | `632a89565883be25d94d38b7cd3ca78d62a491f4` |
| Covered directions | Model selection and resource allocation |
| Training-free integration boundary | Large language models (LLMs) are increasingly used as automatic evaluators of generative AI outputs, a paradigm often referred to as "LLM-as-a-judge." In practice, LLM judges are imperfect predictions for the underlying truth and can exhibit systematic, non-random errors. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
