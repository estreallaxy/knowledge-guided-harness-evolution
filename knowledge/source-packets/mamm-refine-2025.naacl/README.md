# MAMM-Refine: A Recipe for Improving Faithfulness in Generation with Multi-Agent Collaboration

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NAACL 2025 |
| Paper | https://aclanthology.org/2025.naacl-long.498/ |
| Official code | https://github.com/meetdavidwan/mammrefine |
| Upstream revision | `67ac24cf706d4ba16983184c670fff1a3d83e029` |
| Covered directions | model-selection-and-resource-allocation, subagents-and-multiagent-collaboration |
| Training-free integration boundary | Multiple model instances perform detection, critique, candidate correction, and reranking; experiments show reranking is more reliable than free-form generation. Inference-time only. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
