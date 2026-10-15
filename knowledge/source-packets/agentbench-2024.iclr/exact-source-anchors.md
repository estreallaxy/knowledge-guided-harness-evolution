# Exact source anchors

## Selected mechanism

Normalize eight interactive environments behind a common agent protocol, record multi-turn trajectories, and attribute failures by environment and capability.

## Paper anchors

- p. 5: evaluation metric. (Cf. Appendix E for more details)
- p. 5: evaluation of LLMs as web agents. Compared to Mind2Web’s original setting, we make adaptations
- p. 6: Evaluation Prompt Setup. To accommodate most existing dialogue models, our dialogue paradigm
- p. 8: results are unchanged. We think that it indicates llama-2-70b’s insufficient pre-training. While
- p. 9: Evaluation of LLMs. The general capabilities of self-supervised (Liu et al., 2021) LLMs (Brown
- p. 9: evaluation frameworks consider multi-round interactions. A concurrent work InterCode (Yang et al.,
- p. 20: framework with the following features:
- p. 21: algorithm to optimize interactions. This optimization results in client workers seamlessly engaging
- p. 21: evaluation triples.
- p. 22: Evaluation Setup. For each problem (i.e., instruction), the execution can be divided into 3 parts.
- p. 25: Evaluation Setup. We assess each problem in the dataset through the following procedure:
- p. 26: methodology, we have accrued a dataset consisting of 1,663 questions. Each data entry in the dataset

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `src/server/tasks/dbbench/requirements.txt`
- `src/server/tasks/knowledgegraph/requirements.txt`
- `src/server/tasks/webshop/requirements.txt`
- `configs/assignments/test_avalon.yaml`
- `configs/agents/api_agents.yaml`
- `configs/agents/fs_agent.yaml`
- `configs/agents/openai-chat.yaml`
- `configs/agents/openai-text.yaml`
- `src/client/agent_test.py`
- `src/client/agents/test_agent.py`
- `configs/start_task.yaml`
- `configs/start_task_lite.yaml`
- `scripts/validate_lite_configs.py`
- `src/configs.py`
- `src/server/tasks/knowledgegraph/environment.py`
- `src/server/tasks/os_interaction/environment.py`
- `src/server/tasks/alfworld/prompts/alfworld_multiturn_plan_first.json`
- `configs/assignments/default.yaml`
- `configs/assignments/definition.yaml`
- `configs/assignments/lite.yaml`
- `configs/tasks/alfworld.yaml`
- `configs/tasks/avalon.yaml`
- `configs/tasks/card_game.yaml`
- `configs/tasks/dbbench.yaml`
- `configs/tasks/kg.yaml`
- `configs/tasks/ltp.yaml`
- `configs/tasks/mind2web.yaml`
- `configs/tasks/os.yaml`
- `configs/tasks/task_assembly.yaml`
- `configs/tasks/webshop.yaml`
- `src/typings/config.py`
- `src/server/tasks/alfworld/configs/base_config.yaml`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. It is a reusable execution/evaluation harness requiring no training. The paper reports 29-model analyses and the repository exposes environment servers, configs, runners, and scorers.

## Symbol-level code anchors

- `src/client/agent_test.py:8` — `parse_args`
- `src/client/agents/test_agent.py:6` — `CountHistoryAgent`
- `scripts/validate_lite_configs.py:25` — `load_yaml`
- `src/configs.py:9` — `deep_merge`
- `src/server/tasks/knowledgegraph/environment.py:9` — `KnowledgeGraphEnvironmentDelegation`
- `src/server/tasks/os_interaction/environment.py:6` — `OSEnvironmentDelegation`
- `src/typings/config.py:12` — `ConcurrencyConfig`
- `src/analysis.py:56` — `analyze_output`
- `src/assigner.py:29` — `std_out_err_redirect_tqdm`
- `src/client/agent.py:4` — `AgentClient`
- `src/client/agents/claude_agent.py:9` — `Claude`
- `src/client/agents/fastchat_client.py:14` — `Prompter`
