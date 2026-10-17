# When Replanning Becomes the Bottleneck: Budgeted Replanning for Embodied Agents

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/liu26fo.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/liu26fo/liu26fo.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/liu26fo/liu26fo.pdf) |
| Official code | [https://github.com/NEBULIS-Lab/BRACE](https://github.com/NEBULIS-Lab/BRACE) |
| Upstream revision | `92e91e6e69aa2f5d16cec9ff24ec1b02827a862e` |
| Covered direction | Model selection and resource allocation |
| Selected non-training mechanism | A rule-based controller decides whether to replan, selects full, partial, reuse, or defer mode, allocates token and latency budgets, stabilizes repeated replanning, and records auditable decisions. |

The retained snapshot excludes the optional learned E-RECAP module and keeps the deterministic BRACE controller, typed state, schedules, telemetry schema, and audits.
