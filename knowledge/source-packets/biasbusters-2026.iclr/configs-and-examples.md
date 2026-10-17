# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/toolbench/retrieval/inference_example.py` | Dependency, configuration, or usage evidence. |
| `official-code/toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_fn/config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_normalized/config.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/toolbench/retrieval/api_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/toolbench/tooleval/evaluators_comparison.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/toolbench/tooleval/evaluators/__init__.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/base.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/tooleval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/toolbench/tooleval/evaluators/registered_cls/rtl.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/toolbench/model/compression.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
