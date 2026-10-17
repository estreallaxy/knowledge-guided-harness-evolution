# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/v2/tasks/instance_flipt-io__flipt-9f8127f225a86245fa35dca4885c2daef824ee55/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-a0cbc0cb65ae601270bdbe3f5313e2dfd49c80e4/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-a42d38a1bb1df267c53d9d4a706cf34825ae3da9/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-abaa5953795afb9c621605bb18cb32ac48b4508c/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-aebaecd026f752b187f11328b0d464761b15d2ab/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-af7a0be46d15f0b63f16a868d13f3b48a838e7ce/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b2170346dc37cf42fda1386cd630f24821ad2ac5/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b22f5f02e40b225b6b93fff472914973422e97c6/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b2393f07d893024ab1e47ea2081e0289e1f9d56f/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b2cd6a6dd73ca91b519015fd5924fde8d17f3f06/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b3cd920bbb25e01fdb2dab66a5a913363bc62f6c/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b433bd05ce405837804693bebd5f4b88d87133c8/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b4bb5e13006a729bc0eed8fe6ea18cff54acdacb/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b68b8960b8a08540d5198d78c665a7eb0bea4008/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-b6cef5cdc0daff3ee99e5974ed60a1dc6b4b0d67/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-c12967bc73fdf02054cf3ef8498c05e25f0a18c0/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-c154dd1a3590954dfd3b901555fc6267f646a289/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-c1728053367c753688f114ec26e703c8fdeda125/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-c188284ff0c094a4ee281afebebd849555ebee59/environment/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/v2/tasks/instance_flipt-io__flipt-c1fd7a81ef9f23e742501bfb26d914eb683262aa/environment/Dockerfile` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/swe_bench_pro_eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/helper_code/create_problem_statement.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/helper_code/generate_sweagent_instances.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v2/tooling/patch_replay.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v2/tooling/locked_claude_code.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v2/tooling/locked_mini_swe.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v2/tooling/locked_codex.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v2/tooling/host_mini_swe.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v2/tasks/instance_flipt-io__flipt-f808b4dd6e36b9dc8b011eb26b196f4e2cc64c41/tests/parser.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/v2/tasks/instance_flipt-io__flipt-f743945d599b178293e89e784b3b2374b1026430/tests/parser.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
