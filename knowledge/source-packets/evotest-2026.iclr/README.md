# EvoTest: Evolutionary Test-Time Learning for Self-Improving Agentic Systems

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/aa5b64942bfef625403b355214b871e0-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/aa5b64942bfef625403b355214b871e0-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/aa5b64942bfef625403b355214b871e0-Paper-Conference.pdf) |
| Official code | [https://github.com/yf-he/EvoTest](https://github.com/yf-he/EvoTest) |
| Upstream revision | `f92474ce83c7aec69e45c30ccfaf2b69e66823de` |
| Covered directions | Instructions and skills, Long-term memory and experience reuse, Fault tolerance and recovery, Planning and progress management, Session and environment state management |
| Training-free integration boundary | Use an Evolver LLM to revise prompts, memory, hyperparameters, and tool routines from each episode transcript without gradients. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
