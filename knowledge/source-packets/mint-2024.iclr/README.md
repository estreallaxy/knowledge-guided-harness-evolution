# MINT: Evaluating LLMs in Multi-turn Interaction with Tools and Language Feedback

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | ICLR 2024 |
| Paper | https://proceedings.iclr.cc/paper_files/paper/2024/hash/8a0d3ae989a382ce6e50312bc35bf7e1-Abstract-Conference.html |
| Official code | https://github.com/xingyaoww/mint-bench |
| Upstream revision | `3f7f12c10bf763be1e6dbdeb42feb57624121f61` |
| Covered directions | tools-and-environments, fault-tolerance-and-recovery |
| Training-free integration boundary | Provide a Python execution tool and simulated natural-language feedback in a bounded multi-turn loop, recording gains and regressions after each feedback turn. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module. See the three evidence documents for paper/code anchors, runnable entry points, and reported evaluation evidence.
