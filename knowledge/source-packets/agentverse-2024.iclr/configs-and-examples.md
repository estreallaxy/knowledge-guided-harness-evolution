# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.py`
- `agentverse/tasks/simulation/math_problem_2players_tools/config.yaml`
- `agentverse/tasks/simulation/nlp_classroom_3players_withtool/config.yaml`
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
- `agentverse/tasks/tasksolving/tool_using/trending/config.yaml`
- `agentverse/tasks/tasksolving/tool_using/vacation/config.yaml`
- `agentverse_command/main_simulation_cli.py`
- `agentverse_command/main_simulation_gui.py`
- `agentverse_command/main_tasksolving_cli.py`
- `ui/src/phaser3-rex-plugins/plugins/logic/behaviortree/nodes/actions/Runner.js`
- `agentverse/tasks/simulation/alice_home/config.yaml`
- `agentverse/tasks/simulation/db_diag/config.yaml`
- `agentverse/tasks/simulation/nlp_classroom_3players/config.yaml`
- `agentverse/tasks/simulation/nlp_classroom_9players/config.yaml`
- `agentverse/tasks/simulation/nlp_classroom_9players_group/config.yaml`
- `agentverse/tasks/simulation/pokemon/config.yaml`
- `agentverse/tasks/simulation/prisoner_dilemma/config.yaml`
- `agentverse/tasks/tasksolving/brainstorming/config.yaml`
- `agentverse/tasks/tasksolving/pythoncalculator/config.yaml`
- `agentverse/tasks/tasksolving/pythoncalculator/config_html.yaml`

## Upstream command excerpts

```text
python agentverse_command/main_simulation_gui.py --task simulation/nlp_classroom_9players
```

```text
python agentverse_command/main_simulation_gui.py --task simulation/prisoner_dilemma
```

```text
python agentverse_command/main_simulation_gui.py --task simulation/sde_team/sde_team_2players
```

```text
python agentverse_command/main_simulation_gui.py --task simulation/db_diag
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
