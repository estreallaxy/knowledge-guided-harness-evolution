# AutoML-Agent: A Multi-Agent LLM Framework for Full-Pipeline AutoML

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICML 2025 |
| Paper | https://proceedings.mlr.press/v267/trirat25a.html |
| Official code | https://github.com/DeepAuto-AI/automl-agent |
| Upstream revision | `9e0d842959a09d96c00768c14d73bd9df6d39023` |
| Covered directions | execution-loop-and-scheduling, planning-and-progress-management, model-selection-and-resource-allocation, subagents-and-multiagent-collaboration |
| Training-free integration boundary | Extract retrieval-augmented plan search, parallel specialist execution, and multi-stage verification through off-the-shelf LLM APIs. The optional prompt-agent LoRA path is excluded. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
