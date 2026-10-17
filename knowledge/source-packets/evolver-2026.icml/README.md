# From Interactions to Principles: Experience-Driven Self-Distillation for Evolving LLM Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/wu26bf.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/wu26bf/wu26bf.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/wu26bf/wu26bf.pdf) |
| Official code | [https://github.com/KnowledgeXLab/EvolveR](https://github.com/KnowledgeXLab/EvolveR) |
| Upstream revision | `63834b727ee6e7af3410657de36eb845814249ba` |
| Covered directions | Instructions and skills; Long-term memory and experience reuse; Execution loop and scheduling; Planning and progress management; Model selection and resource allocation; Extension mechanisms and lifecycle hooks; Runtime observation, traces, and integration interfaces |
| Selected non-training mechanism | Convert successful and failed interaction trajectories into structured principles, deduplicate and merge related principles, maintain empirical utility, prune low-utility entries, and retrieve useful principles during later interactions. |

The retained code covers prompts, principle and trajectory stores, maintenance routes, and retrieval services. The paper's optional policy-reinforcement stage and its training dependencies are outside this packet boundary.
