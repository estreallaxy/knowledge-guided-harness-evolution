# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/README_zh.md` | Dependency, configuration, or usage evidence. |
| `official-code/ToolPro_Experiment/directus-docker/docker-compose.yml` | Dependency, configuration, or usage evidence. |
| `official-code/ToolPro_Experiment/docker-minio/docker-compose.yml` | Dependency, configuration, or usage evidence. |
| `official-code/ToolPro_Experiment/memos/docker-compose.yml` | Dependency, configuration, or usage evidence. |
| `official-code/client/performance_config.json` | Dependency, configuration, or usage evidence. |
| `official-code/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/core/debug_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/exp2/ToolPro/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/exp2/exp_case4/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/experiment/calculate/tools/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/exp2/ToolPro/run_toolpro.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/exp2/baseline/run_baseline_test.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/exp2/baseline/test_tools/run_patch_normalization_tests.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/experiment/calculate/tools/run_analysis.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
