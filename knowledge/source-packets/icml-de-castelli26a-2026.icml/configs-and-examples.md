# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config/general.py` | Dependency, configuration, or usage evidence. |
| `official-code/config/paths.py` | Dependency, configuration, or usage evidence. |
| `official-code/config/rules.py` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/A3TGCN.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/DCRNN.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/DynGESN.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/EvolveGCN_H.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/EvolveGCN_O.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/GCLSTM.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/GCRN_GRU.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/GCRN_LSTM.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/LAMP.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/leaf_counting/SpiderW5H10/TGCN.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/link_prediction/As-733/LAMP.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/link_prediction/BitcoinAlpha/LAMP.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/node_prediction/ChickenPox/LAMP.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/node_prediction/TwitterTennis/LAMP.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configurations/hyperparameters/node_prediction/WikiMat/LAMP.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_reinit.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/traffic_forecasting/run_traffic_experiment.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
