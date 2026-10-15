# Configs and examples

## Paper configuration

| Configuration surface | Paper setting | Source |
| --- | --- | --- |
| Domains | Retail and airline | §4.1, PDF p.5 |
| Interaction | Agent talks to a simulated user and calls domain APIs | §3, PDF pp.3–5 |
| Scoring | Final database match plus required communicated information | §3.3, PDF p.4 |
| Reliability | pass^k across k repeated trials on each task | §3.4, PDF p.5 |
| Baseline style | Native function calling or text ReAct/Act | §5.1, PDF p.7 |

## Official entry point

```bash
git clone https://github.com/sierra-research/tau-bench.git
git -C tau-bench checkout 59a200c6d575d595120f1cb70fea53cef0632f6b
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

- `run.py`
- `tau_bench/run.py`
- `setup.py`
