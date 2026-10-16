# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/fast_ddrive/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/fast_ddrive/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/fast_ddrive/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/fast_dvlm/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/fast_dvlm/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/fast_dvlm/train_scripts/finetune_multimodal_example.sh` | Dependency, configuration, or usage evidence. |
| `official-code/v1/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/v1/dream/demo_multiturn_chat.py` | Dependency, configuration, or usage evidence. |
| `official-code/v1/dream/model/configuration_dream.py` | Dependency, configuration, or usage evidence. |
| `official-code/v1/llada/model/configuration_llada.py` | Dependency, configuration, or usage evidence. |
| `official-code/v1/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/v2/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/v2/configs/ds_config_zero0_no_offload.json` | Dependency, configuration, or usage evidence. |
| `official-code/v2/configs/ds_config_zero2.json` | Dependency, configuration, or usage evidence. |
| `official-code/v2/configs/ds_config_zero2_no_offload.json` | Dependency, configuration, or usage evidence. |
| `official-code/v2/configs/ds_config_zero3.json` | Dependency, configuration, or usage evidence. |
| `official-code/v2/configs/ds_config_zero3_no_offload.json` | Dependency, configuration, or usage evidence. |
| `official-code/v2/pyproject.toml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/fast_ddrive/eval/evaluate_waymo_metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fast_ddrive/run_chatbot.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fast_ddrive/run_eval.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fast_ddrive/run_metrics.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fast_dvlm/run_chatbot.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fast_dvlm/run_chatbot_sglang.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/fast_dvlm/run_eval.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v1/dream/demo_multiturn_chat.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v1/dream/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v1/dream/eval_gsm8k.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v1/dream/eval_humaneval.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v1/llada/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v1/llada/eval_gsm8k.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v1/llada/eval_humaneval.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v1/llada/eval_llada.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v2/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
