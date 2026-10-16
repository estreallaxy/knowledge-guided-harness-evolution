# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/GroundingDINO/Dockerfile` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/demo/create_coco_dataset.py` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/demo/gradio_app.py` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/demo/inference_on_a_image.py` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/demo/test_ap_on_coco.py` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/docker_test.py` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/environment.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/groundingdino/config/GroundingDINO_SwinB_cfg.py` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/groundingdino/util/slconfig.py` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/GroundingDINO/setup.py` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/env_setup/env.yaml` | Dependency, configuration, or usage evidence. |
| `official-code/env_setup/setup_edival.sh` | Dependency, configuration, or usage evidence. |
| `official-code/env_setup/setup_hpsv3.sh` | Dependency, configuration, or usage evidence. |
| `official-code/generate_instructions/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/eval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/eval_bash.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
