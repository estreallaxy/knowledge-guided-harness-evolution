# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/configs/teams/coagent_with_situational_planning_simulated_user_team_config_claude_sonnet.toml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/teams/coagent_with_situational_planning_simulated_user_team_config_gpt4o.toml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/teams/coagent_with_situational_planning_simulated_user_team_config_gpt4turbo.toml` | Dependency, configuration, or usage evidence. |
| `official-code/configs/teams/coagent_with_situational_planning_simulated_user_team_config_llama3_70b.toml` | Dependency, configuration, or usage evidence. |
| `official-code/demo_agent/auto_agent/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/demo_agent/auto_agent/prompts.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/demo_agent/basic_collaborative_agent/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/demo_agent/basic_collaborative_agent/prompts.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/demo_agent/collaborative_agent_with_situational_planning/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/demo_agent/collaborative_agent_with_situational_planning/prompts.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/demo_agent/utils/memory.py` | Dependency, configuration, or usage evidence. |
| `official-code/environment.yml` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/secrets.example.toml` | Dependency, configuration, or usage evidence. |
| `official-code/setup.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/collaborative_gym/envs/travel_planner/tools/attractions/apis.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/travel_planner/tools/accommodations/apis.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/travel_planner/tools/restaurants/apis.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/travel_planner/tools/flights/apis.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/travel_planner/tools/googleDistanceMatrix/apis.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/computer_use/desktop_env/evaluators/metrics/pdf.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/computer_use/desktop_env/evaluators/metrics/libreoffice.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/computer_use/desktop_env/evaluators/metrics/basic_os.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/computer_use/desktop_env/evaluators/metrics/others.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/computer_use/desktop_env/evaluators/metrics/__init__.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/collaborative_gym/envs/computer_use/desktop_env/evaluators/metrics/thunderbird.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
