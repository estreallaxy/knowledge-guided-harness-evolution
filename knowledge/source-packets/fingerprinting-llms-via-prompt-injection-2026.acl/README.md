# Fingerprinting LLMs via Prompt Injection

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ACL 2026](https://aclanthology.org/2026.acl-long.541/) |
| Publication date | 2026-07-05 |
| Paper | [https://aclanthology.org/2026.acl-long.541.pdf](https://aclanthology.org/2026.acl-long.541.pdf) |
| Official code | [https://github.com/hifi-hyp/ACL-LLMPrint](https://github.com/hifi-hyp/ACL-LLMPrint) |
| Upstream revision | `3e577f98b2bb64780ec2995b074c5aeec9b017e1` |
| Covered directions | Permissions, approval, and runtime isolation |
| Training-free integration boundary | Retain fingerprint-prompt optimization and gray-box or black-box statistical verification; the mechanism modifies prompts and decision rules rather than model parameters. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
