# Exact source anchors

## Paper

| Mechanism or evidence | Exact location | Supported claim and boundary |
| --- | --- | --- |
| Self-contained company environment | §3, PDF pp.3–4 | Combines GitLab, OwnCloud, Plane and RocketChat with an agent workspace and simulated colleagues. |
| Checkpoint task representation | §4, PDF pp.4–5 | Defines task intent, weighted checkpoints, deterministic or rubric-based checks and partial/full completion. |
| Evaluation metrics and lifecycle | §4.1–4.2, PDF p.5 | Defines full completion, partial completion, steps, cost and initialization/execution/finalization stages. |
| Results and recurrent failures | §7.1–7.3, PDF pp.7–9 | Reports model/agent outcomes and identifies looping, progress loss, context loss and cross-application coordination failures. |

## Official code

The paths below refer to the retained snapshot of [https://github.com/TheAgentCompany/TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany) at upstream revision `98b68ef82a47690c316f42fddb05baafaab56851`.

| Mechanism or evidence | Snapshot path | Role |
| --- | --- | --- |
| Solver/evaluator orchestration | `evaluation/run_eval.py` | Creates an OpenHands runtime, executes the solver, passes the trajectory to evaluators and saves results. |
| Checkpoint schema | `workspaces/base_image/scoring.py` | Defines weighted checkpoints, total/result aggregation and task-specific completion strategies. |
| Evaluator boundary | `workspaces/base_image/eval.py; common.py` | Loads a task evaluator and supplies deterministic service access or rubric-based checks. |
| Environment reset API | `servers/api-server/api-server.py` | Resets OwnCloud, RocketChat, Plane and GitLab between trials. |
| Workspace lifecycle | `workspaces/base_image/{init.sh,reset.sh,Dockerfile}` | Initializes and resets the isolated worker environment; task-specific data is excluded. |

The snapshot deliberately omits benchmark answers, task-specific target state, credentials, generated traces, datasets, model weights and files that are unnecessary to inspect the selected mechanism.

## Additional retained implementation anchors

- `evaluation/build_oh_runtime_images.sh`
- `evaluation/run_eval.py`
- `evaluation/run_eval.sh`
- `evaluation/browsing.py`
- `evaluation/generate_task_images.py`
- `evaluation/summarise_results.py`
- `workspaces/base_image/config.py`
- `workspaces/base_image/eval.py`
- `workspaces/base_image/npc/human_user_agent.py`
- `workspaces/base_image/npc/rocketchat_agent.py`
- `workspaces/base_image/npc/run_multi_npc.py`
- `workspaces/base_image/npc/run_one_npc.py`
- `pyproject.toml`
- `servers/api-server/api-server.py`
- `servers/api-server/docker-compose.yml`

## Symbol-level code anchors

- `evaluation/run_eval.py:31` — `get_config`
- `evaluation/browsing.py:14` — `ActionType`
- `evaluation/generate_task_images.py:14` — `check_llm_functions_in_evaluator`
- `evaluation/summarise_results.py:10` — `calculate_cost`
- `workspaces/base_image/eval.py:17` — `pad_key`
- `workspaces/base_image/npc/human_user_agent.py:10` — `agenerate_action_human`
- `workspaces/base_image/npc/rocketchat_agent.py:25` — `get_credentials`
- `workspaces/base_image/npc/run_one_npc.py:25` — `main`
- `servers/api-server/api-server.py:7` — `reset_owncloud`
- `servers/api-server/utils.py:32` — `login_to_plane`
- `workspaces/base_image/common.py:23` — `MockRocketChatClient`
- `workspaces/base_image/encrypt.py:8` — `pad_key`
