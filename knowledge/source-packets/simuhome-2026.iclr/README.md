# SimuHome: A Temporal- and Environment-Aware Benchmark for Smart Home LLM Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/43456e781fac3a034842f0807860474a-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/43456e781fac3a034842f0807860474a-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/43456e781fac3a034842f0807860474a-Paper-Conference.pdf) |
| Official code | [https://github.com/holi-lab/SimuHome](https://github.com/holi-lab/SimuHome) |
| Upstream revision | `83d28837b69f0cbf1bc02ed5334cb8b561a9d54d` |
| Covered directions | Execution loop and scheduling, Session and environment state management |
| Training-free integration boundary | Use a time-accelerated, stateful smart-home simulator to pre-validate schedules and observe delayed environmental effects. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
