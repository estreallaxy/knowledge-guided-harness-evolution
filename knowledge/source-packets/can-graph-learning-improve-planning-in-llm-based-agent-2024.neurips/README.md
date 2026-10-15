# Can Graph Learning Improve Planning in LLM-based Agents?

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2024/hash/098d1bd3eb6156a4c2f834563cdcf617-Abstract-Conference.html |
| Official code | https://github.com/WxxShirley/GNN4TaskPlan |
| Upstream revision | `f1486690f4fa00030bc7035f0dcc41904889aa2c` |
| Covered directions | execution-loop-and-scheduling, planning-and-progress-management, model-selection-and-resource-allocation |
| Training-free integration boundary | Extract only the reported **training-free** GraphSearch/SGC planning variants: task dependency graph construction and connected subgraph/path selection. Trained GNN variants are excluded. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
