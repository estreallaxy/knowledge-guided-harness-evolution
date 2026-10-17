# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/code/environment_deepseek.txt` | Dependency, configuration, or usage evidence. |
| `official-code/code/environment_qwen3.txt` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/eagle3/configs.py` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/rest/datastore/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/config/default_tree.json` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/config/default_tree_1_1.json` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/config/default_tree_6_60.json` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/config/eagle.json` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/config/token_recycle.json` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/samd_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/tree_model/eagle/eagle_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/tree_model/eagle2/eagle2_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/samd/tree_model/eagle3/eagle3_config.py` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/sps/tmp_config/Qwen3_0.6B_tmp_config/generation_config.json` | Dependency, configuration, or usage evidence. |
| `official-code/code/model/sps/tmp_config/Qwen3_8B_tmp_config/generation_config.json` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/code/evaluation/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
