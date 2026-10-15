# WorkArena: How Capable are Web Agents at Solving Common Knowledge Work Tasks?

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICML 2024 |
| Paper | https://proceedings.mlr.press/v235/drouin24a.html |
| Official code | https://github.com/ServiceNow/WorkArena |
| Upstream revision | `e885130962f61fb64ac305497996a46cfc7d18f0` |
| Covered directions | execution-loop-and-scheduling, session-and-environment-state |
| Training-free integration boundary | BrowserGym standardizes reset/step/observation/action/termination and WorkArena supplies reproducible task state and validation. The extractable contribution is environment/session harnessing. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
