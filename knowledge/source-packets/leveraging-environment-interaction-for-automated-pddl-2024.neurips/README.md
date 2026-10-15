# Leveraging Environment Interaction for Automated PDDL Translation and Planning with LLMs

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2024/hash/44af065477781e7f8a8589b14a62c489-Abstract.html |
| Official code | https://github.com/BorealisAI/llm-pddl-planning |
| Upstream revision | `325b5fb40ffb3bc886a183060ab5425ccf6acc82` |
| Covered directions | execution-loop-and-scheduling, planning-and-progress-management |
| Training-free integration boundary | Environment-feedback loop generates and repairs domain/problem PDDL; Exploration Walk scores executability and guides tree refinement. The 66% vs. 29% comparison is produced without model training. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
