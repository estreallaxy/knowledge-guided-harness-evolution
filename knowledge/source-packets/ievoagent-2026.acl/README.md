# IEvoAgent: Evolving Conversational Agent based on User Implicit Feedback

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ACL 2026](https://aclanthology.org/2026.acl-long.441/) |
| Publication date | 2026-07-05 |
| Paper | [https://aclanthology.org/2026.acl-long.441.pdf](https://aclanthology.org/2026.acl-long.441.pdf) |
| Official code | [https://github.com/Hualeez/IEvoAgent](https://github.com/Hualeez/IEvoAgent) |
| Upstream revision | `c37e2f6c4e6643302b15bd74277feb075dbd6a58` |
| Covered directions | Instructions and skills, Long-term memory and experience reuse, Execution loop and scheduling, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Retain the conditional feedback distribution matrix and inference-time prompt-evolution mechanism driven by observed user reactions; exclude offline KTO alignment. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
