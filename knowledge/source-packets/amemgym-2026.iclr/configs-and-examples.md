# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent/awe-2-4-30.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent/awi-evolve/complete.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent/awi-evolve/no-evolution.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent/awi-evolve/question-only.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent/awi-hack.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent/awi.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent/native.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agent/rag-2-4-30.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/env/v1.base.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/env/v1.extra.json` | Dependency, configuration, or usage evidence. |
| `official-code/configs/figure/example.json` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/amemgym/eval/metric.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/assistants/prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/env/sample_state_evolution.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/env/sample_state_schema.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/eval/random.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/eval/upperbound.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/eval/diagnosis.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/eval/overall.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/env/sample_evaluation_qa.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/amemgym/eval/evolution.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
