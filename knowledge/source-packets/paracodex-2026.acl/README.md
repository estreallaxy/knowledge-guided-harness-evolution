# ParaCodex: A Profiling-Guided Autonomous Coding Agent for Reliable Parallel Code Generation and Translation

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ACL 2026](https://aclanthology.org/2026.acl-long.732/) |
| Publication date | 2026-07-05 |
| Paper | [https://aclanthology.org/2026.acl-long.732.pdf](https://aclanthology.org/2026.acl-long.732.pdf) |
| Official code | [https://github.com/Scientific-Computing-Lab/ParaCodex](https://github.com/Scientific-Computing-Lab/ParaCodex) |
| Upstream revision | `5b4af3fdaffd3f63f4d66add52208d220a1914d3` |
| Covered directions | Instructions and skills, Tools and environment interaction, Fault tolerance and recovery, Execution loop and scheduling, Planning and progress management, Model selection and resource allocation |
| Training-free integration boundary | Autonomous coding agents can compile, test, and profile on target hardware, but outputs are brittle without domain scaffolding.We present ParaCodex, an HPC-engineer workflow that turns a Codex-based agent into an autonomous OpenMP GPU offload system using staged hotspot analysis, explicit data planning, correctness gating, and profiling-guided refinement. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
