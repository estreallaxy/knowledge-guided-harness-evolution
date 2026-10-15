# Configs and examples

## Paper configuration

| Configuration surface | Paper setting | Source |
| --- | --- | --- |
| Tasks | 154 tasks over 11 Windows applications | §3.2, PDF p.5 |
| Isolation | Windows 11 VM inside Docker; QEMU/KVM | §3.3, PDF p.6 |
| Termination | DONE, FAIL or t > t_max | §3.1, PDF p.4 |
| Reward | Binary or similarity-based final-state evaluator | §3.1, PDF p.4 |
| Parallelization | Azure ML workers with Blob storage and aggregated results | §3.3, PDF p.6 |

## Official entry point

```bash
git clone https://github.com/microsoft/WindowsAgentArena.git
git -C windows-agent-arena checkout 6d39ed88c545a0d40a7a02e39b928e278df7332b
```

The local snapshot is intended for mechanism inspection and adaptation. Run the upstream setup from the fixed revision when reproducing the full benchmark because datasets, service state, VM images, secrets and task answers are intentionally absent here.

## Harness migration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task instruction and initial environment state | Reset the isolated environment and create a run identifier. | Initial observation plus immutable task metadata. |
| Model action or tool call | Validate the action against the exposed interface, execute it, and record the result. | Typed observation, execution status, timing and error evidence. |
| Termination or step limit | Freeze the final environment state and call the task evaluator. | Final score, evaluator details, full trajectory and resource usage. |
| Repeated trial | Restore the same initial state while changing only the declared seed or sampling source. | Per-trial result and reliability statistics without cross-trial state leakage. |

## Additional retained configuration anchors

- `src/win-arena-container/client/lib_run_single.py`
- `src/win-arena-container/client/run.py`
- `src/win-arena-container/client/desktop_env/controllers/setup.py`
