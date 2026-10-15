# Buffer of Thoughts: Thought-Augmented Reasoning with Large Language Models

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | NeurIPS 2024 |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2024/hash/cde328b7bf6358f5ebb91fe9c539745e-Abstract-Conference.html |
| Official code | https://github.com/YangLing0818/buffer-of-thought-llm |
| Upstream revision | `b46ac813cc2aa2c8f98aa93022d0e491b3862cfc` |
| Covered directions | instructions-and-skills, context-management-and-compression, long-term-memory-and-experience-reuse, fault-tolerance-and-recovery |
| Training-free integration boundary | Store abstract thought templates in a meta-buffer, retrieve and instantiate one for a new task, and let a buffer manager update reusable templates. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
