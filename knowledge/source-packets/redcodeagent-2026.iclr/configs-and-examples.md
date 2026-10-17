# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/_experimental/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/_experimental/set_cover.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/_experimental/topset_distill.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/checker.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/filter_inputs.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/check_ground_truth.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v011.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v012.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v013.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v014.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v015.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v016.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v017.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v018.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/init_ground_truth.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/init_plus.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/to_original_fmt.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/mbpp/check_ground_truth.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/mbpp/init_ground_truth.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/mbpp/init_plus.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/environment/OpenCodeInterpreter/evaluation/evalplus/tools/tsr/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/redcodeagent/RA_evaluation/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/redcodeagent/run_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/scripts/run_agent.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
