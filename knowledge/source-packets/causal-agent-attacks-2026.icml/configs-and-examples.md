# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/CausalBench/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/CausalTrace/graph/agentdojo_inference.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/CausalTrace/detection/metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/CausalTrace/detection/evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/CausalBench/core/trajectory_logger.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/CausalTrace/graph/validators.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/CausalTrace/graph/edge_enhancer.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/CausalTrace/graph/provenance.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
