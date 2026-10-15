# Exact source anchors

## Selected mechanism

Repository checkout isolation, patch application, Dockerized test execution, instance-level pass/fail grading, and reproducible prediction schema.

## Paper anchors

- p. 3: Evaluation metrics. To evaluate a proposed solution, we apply the generated patch, using unix’s
- p. 8: framework logs. In the patches, red highlights are deletions. Green highlights are additions.
- p. 8: Evaluation of LMs. Several recent works for evaluating LMs have either proposed a collection
- p. 9: Limitations and future directions. SWE-bench task instances are all in Python; we hope to apply
- p. 20: Evaluation Metrics Calculation. To determine task completion, we compare the test-to-status
- p. 20: evaluation, and those statistics are not reflected in the above table.
- p. 23: evaluation tasks, we can also see tags (e.g., “Crash :collision:”, “io”) that refer to issues presenting
- p. 24: results in Table 18. Naturally, providing only the files edited by the reference solution’s pull request,
- p. 27: evaluation logs are rich sources of information that software engineering metrics and static analyz-
- p. 45: method=str(request.method).upper() . The model correctly addresses the issue, as re-

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `swebench/collect/README.md`
- `swebench/collect/make_lite/README.md`
- `tests/test_docker_exec_stream.py`
- `tests/test_evaluation.py`
- `tests/test_grading_truncated_ids.py`
- `tests/test_run_metadata.py`
- `.pre-commit-config.yaml`
- `swebench/resources/swebench-og/pytest-dev__pytest/10051/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/10081/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/10356/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/5262/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/5631/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/5787/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/5809/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/5840/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/6197/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/6202/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/7205/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/7236/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/7324/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/7432/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/7490/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/7521/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/7571/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/7982/environment.yml`
- `swebench/resources/swebench-og/pytest-dev__pytest/8399/environment.yml`
- `tests/test_cli.py`
- `tests/test_collect_cli.py`
- `tests/test_collect_issue_refs.py`
- `tests/test_gold_patch_source.py`
- `tests/test_grading_marker_fallback.py`
- `tests/test_grading_skipped.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. ICLR main paper; evaluation harness is separable from the paper's optional trained SWE-Llama baseline.

## Symbol-level code anchors

- `tests/test_docker_exec_stream.py:16` — `close`
- `tests/test_evaluation.py:18` — `test_make_run_report`
- `tests/test_grading_truncated_ids.py:17` — `test_exact_match_still_exact`
- `tests/test_run_metadata.py:16` — `run_dir`
- `tests/test_cli.py:5` — `test_smoke_test`
- `tests/test_collect_cli.py:6` — `test_collect_smoke_test`
- `tests/test_collect_issue_refs.py:12` — `test_hash_form_still_matches`
- `tests/test_gold_patch_source.py:40` — `test_gold_patches_come_from_the_task_repo`
- `tests/test_grading_marker_fallback.py:32` — `test_results_inside_markers_are_used`
- `tests/test_grading_skipped.py:35` — `test_skipped_f2p_is_a_failure`
- `swebench/logger.py:6` — `setup_logger`
- `tests/test_grading_spoofed_output.py:55` — `test_forged_passed_lines_are_not_graded`
