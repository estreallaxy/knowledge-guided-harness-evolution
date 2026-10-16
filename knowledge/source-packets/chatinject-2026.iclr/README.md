# ChatInject: Abusing Chat Templates for Prompt Injection in LLM Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/2a48e053db5f0cd57015a33bbc3f794b-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/2a48e053db5f0cd57015a33bbc3f794b-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/2a48e053db5f0cd57015a33bbc3f794b-Paper-Conference.pdf) |
| Official code | [https://github.com/hwanchang00/ChatInject](https://github.com/hwanchang00/ChatInject) |
| Upstream revision | `c6832ab413ebb4728f7b18640702df542e8b4142` |
| Covered directions | Permissions, approval, and runtime isolation |
| Training-free integration boundary | Expose and test prompt-injection paths created by chat-template boundaries and agent message serialization. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
