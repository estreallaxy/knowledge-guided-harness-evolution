# SkillTrojan: Backdoor Attacks on Skill-Based Agent Systems

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/feng26c.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/feng26c/feng26c.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/feng26c/feng26c.pdf) |
| Official code | [https://github.com/Yunhao-Feng/SkillTrojan](https://github.com/Yunhao-Feng/SkillTrojan) |
| Upstream revision | `2864c7524f3302d025647766c6b9f3aef6674097` |
| Covered directions | Instructions and skills, Tools and environment interaction, Fault tolerance and recovery, Permissions, approval, and runtime isolation, Extension mechanisms and lifecycle hooks, Verification, evaluation, and feedback |
| Training-free integration boundary | Retain skill-level payload partitioning, trigger-controlled composition, automated backdoored-skill synthesis, and clean-utility or attack-success evaluation; no model parameters are trained. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
