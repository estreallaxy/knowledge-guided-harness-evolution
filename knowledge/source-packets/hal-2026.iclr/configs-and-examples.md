# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/agents/colbench_example_agent/code_agent_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/colbench_example_agent/html_agent_prompt.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/colbench_example_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/example_reliability_agent/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agents/example_reliability_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/gaia_example_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/sab_example_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/scicode_tool_calling_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/swebench_example_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/taubench_example_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/taubench_tool_calling/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/agents/usaco_example_agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/tests/agents/test_taubench_example_agent.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/agents/Moatless/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/USACO/USACOBench/evaluation/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/USACO/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/USACO/evaluate_solution_sets.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/USACO/run_usaco.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/appworld_agent/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/assistantbench_browser_agent/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/list_files_agent/main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/replicatorbench_agent/validator/cli/evaluate_design_cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/replicatorbench_agent/validator/cli/evaluate_execute_cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/replicatorbench_agent/validator/cli/evaluate_extracted_info.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/replicatorbench_agent/validator/cli/evaluate_interpret_cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/replicatorbench_agent/validator/cli/evaluate_summary_cli.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/replicatorbench_agent/validator/evaluate_execute.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/replicatorbench_agent/validator/evaluate_interpret.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/agents/replicatorbench_agent/validator/evaluate_replication_preregistration.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
