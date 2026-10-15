# Pack of LLMs: Model Fusion at Test-Time via Perplexity Optimization

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | COLM 2024 |
| Paper | https://openreview.net/pdf?id=5Nsl0nlStc |
| Official code | https://github.com/cmavro/PackLLM |
| Upstream revision | `479e77d5f47699b7395629d2a353a467668dc35f` |
| Covered directions | model-selection-and-resource-allocation, subagents-and-multiagent-collaboration |
| Training-free integration boundary | Prompt perplexity estimates per-model expertise; greedy test-time optimization derives selection/fusion weights. It is explicitly training-free and modular to model addition/removal. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
