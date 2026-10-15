# Configs and examples

## Paper configuration

| Configuration surface | Paper setting | Source |
| --- | --- | --- |
| Evaluation set | 175 consequential workplace tasks | §7.1, PDF p.7 |
| Services | GitLab, OwnCloud, Plane, RocketChat and local workspace | §3, PDF pp.3–4 |
| Scoring | Weighted checkpoints; full and partial completion | §4.1, PDF p.5 |
| Efficiency | LLM calls and API cost per task | §4.1, PDF p.5 |
| Evaluator/NPC model | Claude-3.5-Sonnet-20241022 in reported experiments | §7, PDF p.7 |

## Official entry point

```bash
git clone https://github.com/TheAgentCompany/TheAgentCompany.git
git -C theagentcompany checkout 98b68ef82a47690c316f42fddb05baafaab56851
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

- `evaluation/build_oh_runtime_images.sh`
- `evaluation/run_eval.py`
- `evaluation/run_eval.sh`
- `workspaces/base_image/config.py`
- `workspaces/base_image/npc/run_multi_npc.py`
- `workspaces/base_image/npc/run_one_npc.py`
- `pyproject.toml`
