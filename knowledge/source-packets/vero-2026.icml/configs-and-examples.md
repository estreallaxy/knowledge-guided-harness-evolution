# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/legacy/vero-agents/agents/tau-bench/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/legacy/vero-agents/agents/web_search_agent/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/legacy/vero/examples/gsm8k-agent/src/gsm8k_agent/agent.py` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harbor-circle-packing/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-baseline/packing.py` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-baseline/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-seed/packing.py` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harbor-circle-packing/environment/agent-seed/pyproject.toml` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harbor-circle-packing/environment/docker-compose.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harbor-circle-packing/environment/sidecar/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harbor-circle-packing/environment/sidecar/harness/evaluate.py` | Dependency, configuration, or usage evidence. |
| `official-code/vero/examples/harness-conformance/target/src/conformance_agent/__init__.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/legacy/vero-agents/agents/generic-agent/src/generic_agent/vero_tasks/gaia/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/legacy/vero-benchmarking/src/vero_benchmarking/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/vero/examples/harbor-circle-packing/environment/sidecar/harness/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
