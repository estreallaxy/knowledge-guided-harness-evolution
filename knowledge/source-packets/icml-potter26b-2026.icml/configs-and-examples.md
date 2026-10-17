# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/environment.yml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/interaction/novelty_analysis/score.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/representation_similarity_main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/calculate_similarity.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stats_novelty.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/stats_coop.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/interaction/novelty_analysis/remove_single_agent_brainstorm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
