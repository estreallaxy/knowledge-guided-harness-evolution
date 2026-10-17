# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/bm25-mllm-agent/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/bm25-mllm-agent/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/bm25-mllm-agent/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/gemini-file-search/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/gemini-file-search/example.sh` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/gemini-file-search/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/heaven/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/heaven/example.sh` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/heaven/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/openai-file-search/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/openai-file-search/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/recursive-lm/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/recursive-lm/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/utils/ocr-documents/Makefile` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/utils/ocr-documents/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/baselines/utils/ocr-documents/requirements.txt` | Dependency, configuration, or usage evidence. |
| `official-code/eval/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/eval/requirements.txt` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/eval/evaluate.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
