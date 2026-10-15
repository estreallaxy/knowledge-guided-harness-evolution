# L2MAC: Large Language Model Automatic Computer for Extensive Code Generation

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2024 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2024/hash/9e74900c3f6100c56add4bf417547848-Abstract-Conference.html |
| Official code | https://github.com/samholt/L2MAC |
| Upstream revision | `105e74afdc6721e4d530c65862a32b97b5434e61` |
| Covered directions | instructions-and-skills, tools-and-environments, context-management-and-compression, long-term-memory-and-experience-reuse, fault-tolerance-and-recovery |
| Training-free integration boundary | Split a long task into instructions, persist artifacts in a file-backed memory store, retrieve only needed state, execute/check each instruction, and continue under a controller. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
