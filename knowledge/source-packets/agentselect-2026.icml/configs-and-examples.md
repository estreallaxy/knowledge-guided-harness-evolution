# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agent_rec/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/other/Deployment_Section9.2/Readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/other/MuleRun_Section9.1/Readme.md` | Dependency, configuration, or usage evidence. |
| `official-code/other/PartIII_Compositional_Agents_Process/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/other/PartIII_Compositional_Agents_Process/partiii_compositional_agents/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/other/PartIII_Compositional_Agents_Process/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/other/PartIII_Compositional_Agents_Process/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/other/data_cleansing/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agent_rec/cli_common.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent_rec/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agent_rec/run_common.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/other/MuleRun_Section9.1/run_easyrec_benchmark_eval_mulerun.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_Table4.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_bpr_bert.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_dnn.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_dnn_bge.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_generative.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_kgat.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_lightfm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_lightgcn.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_mf.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_ngcf.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
