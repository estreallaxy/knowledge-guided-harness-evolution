# Tests and reported results

## Direct checks for reuse

| Check | Official location | Expected invariant |
| --- | --- | --- |
| Deterministic mode and budget selection | `official-code/brace/selfcheck_controller.py` | Identical state, trigger, telemetry, and remaining budget yield the same decision. |
| Trigger construction | `official-code/experiments/common/replan_schedule.py` | Periodic, failure, and deadlock evidence maps to explicit trigger fields. |
| Controller-field coverage | `official-code/analysis/controller_field_coverage.py` | Each decision record exposes the fields required for later audit. |
| Trigger audit | `official-code/analysis/trigger_audit_table.py` | Reported decisions can be grouped and checked by primary trigger. |
| Phase accounting | `official-code/analysis/phase_breakdown_table.py` | Replanning latency and token use remain separable by phase. |

## Reported paper evidence

The paper reports cross-platform results and ablations in Section 4 (PDF pp.6–9), including controller-only and controller-plus-E-RECAP variants. Only controller-only evidence is directly aligned with the retained snapshot. E-RECAP results involve a learned token-utility predictor and are outside this packet boundary.

## Exclusions

Model-training code, learned-pruner checkpoints, datasets, generated run directories, result dumps, credentials, benchmark answers, and simulator assets are not retained.
