# Exact source anchors

## Paper

| Mechanism or evidence | Exact location | Supported claim and boundary |
| --- | --- | --- |
| Controllable no-consequence app world and 457-API engine | §2–2.1, PDF pp.3–4 | Defines the app simulator, stateful execution shell, documented APIs, database-backed state transitions and safe error feedback. |
| Reproducible reset and validation construction | §2.2–3.3, PDF pp.4–6 | Connects task setup, database snapshots and state-based assertions; evaluation checks final state rather than matching an action trace. |
| Dataset split and difficulty | §3.4 and Table 2, PDF p.7 | Records Train/Dev/Test-N/Test-C roles and shows that Test-C requires unseen apps and more APIs, calls and evaluation tests. |
| Baseline and oracle-API evidence | §4.1–4.3 and Table 3, PDF pp.7–8 | Separates API retrieval from interactive execution; oracle APIs improve results but do not close the execution gap. |

## Official code

The paths below refer to the retained snapshot of [https://github.com/StonyBrookNLP/appworld](https://github.com/StonyBrookNLP/appworld) at upstream revision `42b5bcf3cd334fee33f0c37c02070a9f5807add5`.

| Mechanism or evidence | Snapshot path | Role |
| --- | --- | --- |
| Stateful execution environment | `src/appworld/environment.py` | Creates tasks, executes code/API calls, saves or loads checkpoints and exposes evaluation. |
| State-based evaluator | `src/appworld/evaluator.py` | Compares initial and final databases through task-specific assertions and aggregates task/dataset results. |
| Task and reset metadata | `src/appworld/task.py` | Loads task identifiers, split metadata and task-specific environment state without embedding the excluded task bundles. |
| Remote environment boundary | `src/appworld/serve/environment.py` | Exposes execution and evaluation as a service boundary suitable for an agent harness. |
| API documentation and requests | `src/appworld/api_docs.py; src/appworld/requester.py` | Supports documentation retrieval, authenticated API calls, request counts and request resets. |

The snapshot deliberately omits benchmark answers, task-specific target state, credentials, generated traces, datasets, model weights and files that are unnecessary to inspect the selected mechanism.

## Additional retained implementation anchors

- `src/appworld/environment.py`
- `src/appworld/evaluator.py`
- `tests/package/test_appworld.py`
- `src/appworld/common/code_tools.py`
- `src/appworld/common/evaluation.py`
- `src/appworld/common/prompts.py`
- `src/appworld/serve/environment.py`
- `pyproject.toml`
- `src/appworld/api_docs.py`
- `src/appworld/cli.py`
- `src/appworld/download.py`
- `src/appworld/ground_truth.py`
- `src/appworld/install.py`
- `src/appworld/leaderboard.py`
- `src/appworld/requester.py`

## Symbol-level code anchors

- `src/appworld/environment.py:107` — `AppWorldInitDefaults`
- `src/appworld/evaluator.py:40` — `Pass`
- `tests/package/test_appworld.py:44` — `TestAppWorld`
- `src/appworld/common/code_tools.py:8` — `code_is_valid`
- `src/appworld/common/evaluation.py:15` — `answer_to_text`
- `src/appworld/common/prompts.py:9` — `chat_messages_to_string`
- `src/appworld/serve/environment.py:44` — `AppWorldArgs`
- `src/appworld/api_docs.py:29` — `sort_parameters`
- `src/appworld/cli.py:52` — `OrderCommands`
- `src/appworld/download.py:24` — `get_data_key`
- `src/appworld/ground_truth.py:31` — `GroundTruth`
- `src/appworld/install.py:9` — `install_repo`
