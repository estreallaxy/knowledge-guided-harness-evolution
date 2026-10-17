# Conjunctive Prompt Attacks in Multi-Agent LLM Systems

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ACL 2026](https://aclanthology.org/2026.acl-long.1577/) |
| Publication date | 2026-07-05 |
| Paper | [https://aclanthology.org/2026.acl-long.1577.pdf](https://aclanthology.org/2026.acl-long.1577.pdf) |
| Official code | [https://github.com/UCF-ML-Research/ConjunctiveAgents](https://github.com/UCF-ML-Research/ConjunctiveAgents) |
| Upstream revision | `2373a4f3f49bd37f45edfe59c2b1d6f315526b18` |
| Covered directions | Instructions and skills, Fault tolerance and recovery, Sub-agent and multi-agent collaboration, Permissions, approval, and runtime isolation |
| Training-free integration boundary | Conjunction attacks coordinate prompt perturbations across interacting agents while model parameters remain frozen; optimization changes attack inputs, not LLM weights. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
