# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.MD` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_Doubao.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_GLM4_5.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_Minimax.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_Mistral.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_baichuan.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_claude3_7.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_claude4.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_gemini2_0.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_gemini2_5.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_gemini2_5pro.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_gpt4o.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_grok4.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_internlm3.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_interns1.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_interns1_mini.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_internvl3_5.json` | Dependency, configuration, or usage evidence. |
| `official-code/agent/config_llama3_2.json` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/run_training_free_grpo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
