# Exact source anchors

## Paper

| Mechanism or evidence | Exact location | Supported claim and boundary |
| --- | --- | --- |
| Tool-agent-user interaction loop | §3, PDF pp.3–5 | Defines a modular environment with domain databases/APIs, policy documents, user instructions and a simulated user. |
| End-state evaluation | §3.3 and §4.2, PDF pp.4–6 | Checks final database state and communicated information against annotated goals rather than using an unconstrained judge. |
| Reliability metric | §3.4, PDF p.5 | Defines pass^k as repeated success on the same task and distinguishes it from pass@k. |
| Results and failure analysis | §5.1–5.2, PDF pp.7–8 | Reports per-domain success, reliability collapse across repeated trials, cost and trace-level failure categories. |

## Official code

The paths below refer to the retained snapshot of [https://github.com/sierra-research/tau-bench](https://github.com/sierra-research/tau-bench) at upstream revision `59a200c6d575d595120f1cb70fea53cef0632f6b`.

| Mechanism or evidence | Snapshot path | Role |
| --- | --- | --- |
| Environment contract | `tau_bench/envs/base.py` | Implements reset, step, termination and final reward from database and action constraints. |
| Run-result schema | `tau_bench/types.py` | Defines actions, observations, rewards, reset responses and complete run results. |
| Experiment runner and pass^k | `tau_bench/run.py` | Runs task trials, persists checkpoints and computes average reward plus consistency counts. |
| User simulator | `tau_bench/envs/user.py` | Separates the simulated user lifecycle from the tested agent. |
| Domain tools and policies | `tau_bench/envs/{retail,airline}/tools; rules.py; wiki.md` | Defines bounded callable actions and explicit policy material; task instances and database records are omitted. |

The snapshot deliberately omits benchmark answers, task-specific target state, credentials, generated traces, datasets, model weights and files that are unnecessary to inspect the selected mechanism.

## Additional retained implementation anchors

- `tau_bench/agents/tool_calling_agent.py`
- `tau_bench/envs/airline/tools/transfer_to_human_agents.py`
- `tau_bench/envs/retail/tools/transfer_to_human_agents.py`
- `run.py`
- `tau_bench/run.py`
- `tau_bench/agents/base.py`
- `tau_bench/agents/chat_react_agent.py`
- `tau_bench/agents/few_shot_agent.py`
- `tau_bench/agents/__init__.py`
- `tau_bench/envs/tool.py`
- `tau_bench/model_utils/api/cache.py`
- `tau_bench/model_utils/func_tools/filter.py`
- `tau_bench/model_utils/func_tools/map.py`
- `tau_bench/model_utils/func_tools/__init__.py`
- `tau_bench/envs/airline/tools/book_reservation.py`

## Symbol-level code anchors

- `tau_bench/agents/tool_calling_agent.py:12` — `ToolCallingAgent`
- `tau_bench/envs/airline/tools/transfer_to_human_agents.py:7` — `TransferToHumanAgents`
- `tau_bench/envs/retail/tools/transfer_to_human_agents.py:7` — `TransferToHumanAgents`
- `run.py:10` — `parse_args`
- `tau_bench/run.py:20` — `run`
- `tau_bench/agents/base.py:9` — `Agent`
- `tau_bench/agents/chat_react_agent.py:17` — `ChatReActAgent`
- `tau_bench/agents/few_shot_agent.py:13` — `FewShotToolCallingAgent`
- `tau_bench/envs/tool.py:5` — `Tool`
- `tau_bench/model_utils/api/cache.py:20` — `disable_cache`
- `tau_bench/model_utils/func_tools/filter.py:10` — `filter`
- `tau_bench/model_utils/func_tools/map.py:8` — `map`
