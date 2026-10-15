# Exact source anchors

## Selected mechanism

Expert recruitment, collaborative decision, action execution, and evaluation form a configurable multi-agent harness; experiments span reasoning, coding, tools, and embodied tasks.

## Paper anchors

- p. 2: Evaluation - Assess the differences between the current state and desired outcomes. If the current
- p. 2: framework for promoting collaboration among multiple agents in problem-solving.
- p. 3: evaluation stage (Section 2.4). This allows AGENT V ERSE to employ the most suitable group based
- p. 6: Evaluation Evaluation
- p. 18: results are conveyed as the environment state to the evaluation module.
- p. 19: Evaluation To facilitate a feedback loop, an agent was tasked with the role of evaluator. This
- p. 25: Evaluation We directly exploit the inventory and the completed or failed sub-tasks of each agent as
- p. 35: Evaluation
- p. 36: Evaluation
- p. 37: Evaluation
- p. 41: Evaluation Evaluation
- p. 43: Framework Agent(s)

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `README_simulation_cases.md`
- `README_zh.md`
- `requirements.txt`
- `setup.py`
- `ui/LICENSE`
- `ui/README.md`
- `ui/package.json`
- `agentverse/tasks/simulation/db_diag/README.md`
- `agentverse/tasks/simulation/sde_team/readme.md`
- `ui/src/phaser3-rex-plugins/plugins/logic/behaviortree/LICENSE`
- `ui/src/phaser3-rex-plugins/plugins/logic/behaviortree/README.md`
- `ui/src/phaser3-rex-plugins/plugins/utils/jsdiff/LICENSE`
- `ui/src/phaser3-rex-plugins/plugins/utils/jsdiff/README.md`
- `ui/src/phaser3-rex-plugins/plugins/gameobjects/live2d/framework/LICENSE.md`
- `ui/src/phaser3-rex-plugins/plugins/gameobjects/live2d/framework/README.md`
- `ui/src/phaser3-rex-plugins/plugins/gameobjects/live2d/framework/package.json`
- `agentverse/environments/simulation_env/sde_team_given_tests.py`
- `agentverse/tasks/simulation/math_problem_2players_tools/config.yaml`
- `agentverse/tasks/simulation/nlp_classroom_3players_withtool/config.yaml`
- `agentverse/environments/simulation_env/rules/order/sde_team_given_tests.py`
- `agentverse/environments/simulation_env/rules/selector/sde_team_given_tests.py`
- `agentverse/environments/tasksolving_env/rules/executor/code_test.py`
- `agentverse/environments/tasksolving_env/rules/executor/coverage_test.py`
- `agentverse/tasks/tasksolving/humaneval/gpt-3.5/config.yaml`
- `agentverse/tasks/tasksolving/humaneval/gpt-4/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/24point/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/bmi/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/bookclub/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/car/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/date/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/diy/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/party/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/sudoku/config.yaml`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Expert recruitment, collaborative decision, action execution, and evaluation form a configurable multi-agent harness; experiments span reasoning, coding, tools, and embodied tasks.

## Symbol-level code anchors

- `agentverse/environments/simulation_env/sde_team_given_tests.py:19` — `SdeTeamGivenTestsEnvironment`
- `agentverse/environments/simulation_env/rules/order/sde_team_given_tests.py:16` — `SdeTeamGivenTestsOrder`
- `agentverse/environments/simulation_env/rules/selector/sde_team_given_tests.py:16` — `extract`
- `agentverse/environments/tasksolving_env/rules/executor/code_test.py:16` — `execute_command`
- `agentverse/environments/tasksolving_env/rules/executor/coverage_test.py:15` — `execute_command`
- `agentverse_command/main_simulation_cli.py:21` — `cli_main`
- `agentverse_command/main_simulation_gui.py:23` — `cli_main`
- `agentverse_command/main_tasksolving_cli.py:29` — `cli_main`
- `agentverse/environments/base.py:16` — `BaseRule`
- `agentverse/memory/base.py:9` — `BaseMemory`
- `agentverse/memory/chat_history.py:18` — `ChatHistoryMemory`
- `agentverse/memory/sde_team.py:16` — `SdeTeamMemory`
