# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/examples/igraph_graph_info.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/igraph_graph_visualization.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/longmemeval_gold_retrieval.py` | Dependency, configuration, or usage evidence. |
| `official-code/examples/openie/longmemeval_convert_output_to_cache.py` | Dependency, configuration, or usage evidence. |
| `official-code/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/requirements_nvemb.txt` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/remem/agent/agent_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/remem/evaluation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/remem/prompts/templates/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/remem/utils/config_utils.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/remem/utils/eval_utils.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
