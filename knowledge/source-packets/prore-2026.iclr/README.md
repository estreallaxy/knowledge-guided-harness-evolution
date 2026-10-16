# ProRe: A Proactive Reward System for GUI Agents via Reasoner–Actor Collaboration

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/74bb6042258daa72bedc9616b1b93eda-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/74bb6042258daa72bedc9616b1b93eda-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/74bb6042258daa72bedc9616b1b93eda-Paper-Conference.pdf) |
| Official code | [https://github.com/V-Droid-Agent/ProRe](https://github.com/V-Droid-Agent/ProRe) |
| Upstream revision | `67cdbea86102235de901e98efbd0d641241cf925` |
| Covered directions | Tools and environment interaction, Fault tolerance and recovery, Execution loop and scheduling, Planning and progress management, Model selection and resource allocation, Sub-agent and multi-agent collaboration, Extension mechanisms and lifecycle hooks, Runtime observation, traces, and integration interfaces |
| Training-free integration boundary | Have a reasoner schedule targeted state probes and evaluator actors collect fresh evidence before assigning a reward. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
