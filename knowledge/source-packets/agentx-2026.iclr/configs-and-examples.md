# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/agentlego/agentlego/testing/setup_tool.py` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/calculator/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/image_canny/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/image_depth/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/image_editing/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/image_pose/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/image_scribble/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/image_text/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/imagebind/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/object_detection/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/ocr/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/python_interpreter/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/search/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/segmentation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/speech_text/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/translation/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/agentlego/agentlego/tools/vqa/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/opencompass/configs/eval_multi_prompt_demo.py` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/opencompass/configs/eval_multi_prompt_demo.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
