# Configurations and examples

## Selected runtime surface

| Official location | Use |
| --- | --- |
| `official-code/configs/smoke/proxy_controller.json` | Minimal controller configuration for a proxy run. |
| `official-code/docs/CONTROLLER.md` | Controller fields, modes, hazards, and integration contract. |
| `official-code/docs/SCHEMA.md` | Event and metric schema required for auditable decisions. |
| `official-code/brace/selfcheck_controller.py` | Lightweight deterministic controller self-check. |

## Integration sequence

1. Build a trigger from periodic, failure, deadlock, or safety evidence.
2. Supply current progress, latency, churn, clarification allowance, remaining tokens, and persistent controller state.
3. Invoke `BraceController.step` to select a replanning mode and allocate token and time budgets.
4. Execute the selected mode while preserving protected context blocks.
5. Record the decision, phase costs, outcome, and updated state; use cooldown and commit windows in the next call.

No model parameter is updated in this sequence.
