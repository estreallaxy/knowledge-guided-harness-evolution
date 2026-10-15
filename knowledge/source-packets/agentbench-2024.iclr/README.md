# AgentBench: Evaluating LLMs as Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2024 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html |
| Official code | https://github.com/THUDM/AgentBench |
| Upstream revision | `d1e4a10db08c87075c78972e48ecc182be03e2d5` |
| Covered directions | tools-and-environments |
| Training-free integration boundary | Normalize eight interactive environments behind a common agent protocol, record multi-turn trajectories, and attribute failures by environment and capability. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
