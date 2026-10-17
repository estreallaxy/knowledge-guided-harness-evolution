# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/config/general.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/config/light.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/docker/start_benchmark_sandbox.sh` | Dependency, configuration, or usage evidence. |
| `official-code/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/servers/math/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/servers/osint/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/servers/unit/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/run_benchmark.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/servers/chem/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/servers/crypto/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/servers/graphs/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/servers/lang/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/servers/math/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/servers/osint/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/servers/time/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/servers/unit/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/software/LightFlight/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/software/LightNews/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/software/LightShop/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/software/LightStock/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/software/LightSystem/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/software/LightTalk/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/software/LightWeather/app.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
