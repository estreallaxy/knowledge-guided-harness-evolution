# SEC-bench: Automated Benchmarking of LLM Agents on Real-World Software Security Tasks

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | 2025, NeurIPS track |
| Paper | https://proceedings.neurips.cc/paper_files/paper/2025/hash/a9168f1c54e5147027f1e8cf83e1a775-Abstract-Conference.html |
| Official code | https://github.com/SEC-bench/SEC-bench |
| Upstream revision | `31eb43485a3de47da260be0f978528b1f2314415` |
| Covered directions | permissions-approval-and-isolation, observability-traces-and-interfaces, verification-evaluation-and-feedback |
| Training-free integration boundary | Hierarchical Docker images, vulnerability reproduction harness, isolated PoC/patch execution, gold artifacts, multi-agent construction pipeline, and deterministic evaluation commands. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
