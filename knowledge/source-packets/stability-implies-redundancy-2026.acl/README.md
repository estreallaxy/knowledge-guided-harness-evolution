# Stability Implies Redundancy: Delta Attention Selective Halting for Efficient Long-Context Prefilling

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ACL 2026](https://aclanthology.org/2026.acl-long.1235/) |
| Publication date | 2026-07-05 |
| Paper | [https://aclanthology.org/2026.acl-long.1235.pdf](https://aclanthology.org/2026.acl-long.1235.pdf) |
| Official code | [https://github.com/verach3n/DASH](https://github.com/verach3n/DASH) |
| Upstream revision | `831cb45f2b41714aad719af1d7092604be94bc93` |
| Covered directions | Context management and compression, Model selection and resource allocation, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Retain the training-free Delta Attention Selective Halting policy that monitors layer-wise update stability and stops redundant token computation at inference time. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
