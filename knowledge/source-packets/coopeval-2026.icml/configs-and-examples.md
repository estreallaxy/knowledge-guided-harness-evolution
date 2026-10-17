# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/configs/agents/cheap_llms_3.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agents/few_strong_llms.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agents/sota_llms.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agents/test_agents_3.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/agents/test_agents_6.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/src/coopeval/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/coopeval/config_loader.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/coopeval/llm_judge/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/src/coopeval/llm_judge/config/__init__.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/coopeval/llm_judge/config/cooperation_taxonomy.json` | Dependency, configuration, or usage evidence. |
| `official-code/src/coopeval/llm_judge/config/cooperation_taxonomy.py` | Dependency, configuration, or usage evidence. |
| `official-code/src/coopeval/llm_judge/config/example_taxonomy.json` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/coopeval/agents/test_llm.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/registry/agent_registry.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/utils/match_scheduler_reputation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/agents/agent_manager.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/config.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/config_loader.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/logger_manager.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/script_utils/reproducibility.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/mechanisms/no_mechanism.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/script_utils/llm_judge_helpers.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/coopeval/script_utils/colors.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
