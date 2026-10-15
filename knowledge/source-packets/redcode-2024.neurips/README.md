# RedCode: Risky Code Execution and Generation Benchmark for Code Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | 2024, NeurIPS Datasets and Benchmarks |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2024/hash/bfd082c452dffb450d5a5202b0419205-Abstract-Datasets_and_Benchmarks_Track.html |
| Official code | https://github.com/AI-secure/RedCode |
| Upstream revision | `c84b6db88fd8bd258e29f12e692ccfd4287a454d` |
| Covered directions | permissions-approval-and-isolation, verification-evaluation-and-feedback |
| Training-free integration boundary | Docker-isolated execution, 25 vulnerability classes, scenario-specific environment preparation, refusal/attack-success metrics, and deterministic post-execution checks. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
