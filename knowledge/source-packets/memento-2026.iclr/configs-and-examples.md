# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/prompts/0/prompt-episode_292_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/prompts/0/prompt-episode_293_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/prompts/0/prompt-episode_404_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/prompts/0/prompt-episode_439_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/prompts/0/prompt-episode_477_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/prompts/0/prompt-episode_478_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/prompts/0/prompt-episode_59_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_292_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_293_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_404_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_439_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_477_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_478_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_59_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_77_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_836_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/resource/memory/few_shot_examples/few_shot_examples/traces/0/trace-episode_838_0-0.txt` | Dependency, configuration, or usage evidence. |
| `official-code/src/agent/env/environment_interface.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/src/agent/env/environment_interface.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/user_profile_memory/graph_schema.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/prompts.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/user_profile_memory/prompt_based_encoder.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/motor_skills/object_states/oracle_fill_skills.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/motor_skills/object_states/oracle_clean_skills.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/motor_skills/object_states/oracle_pour_skills.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/tools/motor_skills/object_states/oracle_power_skills.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
