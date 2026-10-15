# Exact source anchors

## Selected mechanism

Containerized JavaScript issue environments, image-bearing issue/test inputs, visual patch workflow, and executable repository tests.

## Paper anchors

- p. 3: Limitations. Within the SWE-bench task formulation, several facets of software development re-
- p. 6: evaluation on Python and SWE-bench tasks; (2) SWE-agent JS, which converts SWE-agent Base’s
- p. 12: evaluation of large language models for code, 2024. URL https://arxiv.org/abs/2403
- p. 23: implementation.
- p. 30: Results: We applied this labeling procedure to the 862 problem statement images across all SWE-
- p. 31: Results: We again answer these questions for problem statement images in SWE-bench M. Out of
- p. 34: Results: Out of 557 task instances, 465 were labeled as the image being necessary to solving the
- p. 35: Results: From this labeling procedure, 100 SWE-bench M task instances are labeled with differing

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

The acceptance and transfer decision is limited to the inference-time mechanism described above. ICLR main paper; its `SWE-bench_Multimodal` dataset and development-split evaluator are supported by the official SWE-bench harness without model training.

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
