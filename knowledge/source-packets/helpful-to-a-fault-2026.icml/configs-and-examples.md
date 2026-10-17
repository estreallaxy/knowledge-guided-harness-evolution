# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/.pre-commit-config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentharm/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/agentharm/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config/config_ollama.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/config_sglang.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/prompts/attacker_agent_prompts.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/prompts/judge_prompts.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/prompts/plan_generation_prompts.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agentharm/benchmark/benign_tools/verify_database_security.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/gpt_evaluator.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/benign_tools/search_asset_libraries.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/benign_tools/search_web_hosting.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/benign_tools/search_hotels.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/harmful_tools/search_asset_libraries.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/harmful_tools/search_web_hosting.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/benign_tools/query_onion_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/benign_tools/query_bing_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/harmful_tools/search_hotels.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/harmful_tools/query_bing_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agentharm/benchmark/benign_tools/query_google_search.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
