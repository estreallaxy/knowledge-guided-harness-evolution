# Benchmarking LLM Tool-Use in the Wild

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4fb6b4482e4e24a33a3de5b01a011eb0-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/4fb6b4482e4e24a33a3de5b01a011eb0-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/4fb6b4482e4e24a33a3de5b01a011eb0-Paper-Conference.pdf) |
| Official code | [https://github.com/yupeijei1997/WildToolBench](https://github.com/yupeijei1997/WildToolBench) |
| Upstream revision | `69647d60b990b169267598573d91fdc00ba69bfb` |
| Covered directions | Tools and environment interaction, Runtime observation, traces, and integration interfaces |
| Training-free integration boundary | Replay realistic multi-turn tool-use interactions and score orchestration, implicit intent, and instruction transitions. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
