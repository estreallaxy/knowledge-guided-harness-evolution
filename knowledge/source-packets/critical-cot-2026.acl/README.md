# Critical-CoT: A Robust Defense Framework against Reasoning-Level Backdoor Attacks in Large Language Models

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ACL 2026](https://aclanthology.org/2026.acl-long.495/) |
| Publication date | 2026-07-05 |
| Paper | [https://aclanthology.org/2026.acl-long.495.pdf](https://aclanthology.org/2026.acl-long.495.pdf) |
| Official code | [https://github.com/tuanvu171/Critical-CoT](https://github.com/tuanvu171/Critical-CoT) |
| Upstream revision | `d84cad007fc429b9092503d0aac6d66b831690cf` |
| Covered directions | Fault tolerance and recovery, Planning and progress management, Permissions, approval, and runtime isolation |
| Training-free integration boundary | To bridge this gap, we propose Critical-CoT, a novel defense mechanism that conducts a two-stage fine-tuning (FT) on LLMs to develop critical thinking behaviors, enabling them to automatically identify potential backdoors and refuse to generate malicious reasoning steps. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
