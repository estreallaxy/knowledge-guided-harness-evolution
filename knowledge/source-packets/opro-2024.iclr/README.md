# Large Language Models as Optimizers

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2024 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2024/hash/3339f19c5fcee3ad74502947a32be9e6-Abstract-Conference.html |
| Official code | https://github.com/google-deepmind/opro |
| Upstream revision | `a76bdce2cbf6d4a0d1e570a6fcfe17be9c2abdd7` |
| Covered directions | instructions-and-skills |
| Training-free integration boundary | Maintain candidate–score history in a meta-prompt; ask an LLM to propose the next instruction and evaluate it as a black-box optimization loop. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
