# Configs and examples

## Paper configuration

| Configuration surface | Paper setting | Source |
| --- | --- | --- |
| World | 9 everyday apps plus ApiDocs and Supervisor; 457 APIs | §2.1, PDF p.3 |
| State control | Task-specific database and simulated time can be reset | §2.2, PDF p.4 |
| Splits | Train 60; Dev 60; Test-N 168; Test-C 417 | §3.4, PDF pp.6–7 |
| Termination | Special task_completed API or method-specific step threshold | §4, PDF p.7 |
| Evaluation | Task Goal Completion (TGC) and Scenario Goal Completion (SGC) | §3.3 and §4, PDF pp.6–8 |

## Official entry point

```bash
git clone https://github.com/StonyBrookNLP/appworld.git
git -C appworld checkout 42b5bcf3cd334fee33f0c37c02070a9f5807add5
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

- `pyproject.toml`
