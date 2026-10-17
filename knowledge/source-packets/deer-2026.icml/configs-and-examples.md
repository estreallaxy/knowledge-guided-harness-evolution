# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/LICENSE` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/info_verification/eval_main.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/info_verification/eval_metrics.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_domain_all.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_information_verification.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_report_evaluation.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/run_score_integration.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_bio.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_chem.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_csai.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_economics.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_education.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_engineer.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_history.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_linguistics.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_math.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/script/run_philosophy.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
