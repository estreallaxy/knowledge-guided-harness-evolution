# Tests and reported results

## Official verification entry points

- `agentverse/environments/simulation_env/sde_team_given_tests.py`
- `agentverse/environments/simulation_env/rules/order/sde_team_given_tests.py`
- `agentverse/environments/simulation_env/rules/selector/sde_team_given_tests.py`
- `agentverse/environments/tasksolving_env/rules/executor/code_test.py`
- `agentverse/environments/tasksolving_env/rules/executor/coverage_test.py`
- `agentverse/tasks/tasksolving/humaneval/gpt-3.5/config.yaml`
- `agentverse/tasks/tasksolving/humaneval/gpt-4/config.yaml`
- `agentverse/environments/tasksolving_env/rules/evaluator/__init__.py`
- `agentverse/environments/tasksolving_env/rules/evaluator/base.py`
- `agentverse/environments/tasksolving_env/rules/evaluator/basic.py`
- `agentverse/agents/tasksolving_agent/evaluator.py`

## Published result anchors

- p. 4: Table 1: The results on different tasks that evaluate the agents’ general capabilities.
- p. 19: Table 3: The performance under different group size settings. Group-x means there are x decision-
- p. 43: Table 4: We provide a comparison of our framework with other existing agent frameworks (up to the

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/OpenBMB/AgentVerse at `f90c4bd9680fdd3bcff8c52c9170911a59b23478` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
