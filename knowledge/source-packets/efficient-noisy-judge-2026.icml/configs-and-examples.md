# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE.md` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/docs/LICENSE-text.html` | Dependency, configuration, or usage evidence. |
| `official-code/docs/LICENSE.html` | Dependency, configuration, or usage evidence. |
| `official-code/inst/extdata/example_judge_data.json` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/reproduce/llm_judge_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/docs/lightswitch.js` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/docs/pkgdown.js` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/docs/deps/jquery-3.6.0/jquery-3.6.0.js` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
