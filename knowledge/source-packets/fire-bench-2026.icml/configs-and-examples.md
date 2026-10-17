# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agents/openhands/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/agents/openhands/config.toml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/agentbench_llm_agents_rq0/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/agentbench_llm_agents_rq1/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/agentbench_llm_agents_rq2/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/gcg_adversarial_attacks_rq0/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/gcg_adversarial_attacks_rq1/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/geval_llm_evaluator_rq0/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/geval_llm_evaluator_rq1/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/geval_llm_evaluator_rq2/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/irrelevant_context_distraction_rq0/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/irrelevant_context_distraction_rq1/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/jailbroken_safety_failure_modes_rq0/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/jailbroken_safety_failure_modes_rq1/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/loft_long_context_subsume_rag_rq0/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/loft_long_context_subsume_rag_rq1/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/loft_long_context_subsume_rag_rq2/task_config.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/benchmark/papers_unverified/loft_long_context_subsume_rag_rq3/task_config.yaml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agents/claude/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/codex/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/openhands/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/simple/run.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_agent.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
