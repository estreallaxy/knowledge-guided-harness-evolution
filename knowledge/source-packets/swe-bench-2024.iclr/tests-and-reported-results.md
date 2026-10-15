# Tests and reported results

## Official verification entry points

- `tests/test_docker_exec_stream.py`
- `tests/test_evaluation.py`
- `tests/test_grading_truncated_ids.py`
- `tests/test_run_metadata.py`
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
- `tests/test_grading_spoofed_output.py`

## Published result anchors

- p. 4: Table 1: Average and maximum numbers char-
- p. 5: Table 3. We observe that in approximately 40% of instances, BM25 retrieves a superset of the
- p. 5: Table 2: Model resolve rates with BM25 re- Table 3: BM25 recall with respect to oracle files
- p. 5: Table 4: We compare the different context lengths and proportion of the “oracle” retrieval setting
- p. 6: Table 5: We compare models against each other using the BM25 retriever as described in Section 4.
- p. 7: Table 7: We compare performance on task instances from before and after 2023 in the “Oracle”
- p. 7: Table 8: Average edits of model generated patches in the “oracle” retrieval setting across success-
- p. 16: Table 9: Description of each field of a SWE-bench task instance object. See § A.2 for details
- p. 19: Table 10: Statistics for how many candidate task instances were kept after the completion of a stage
- p. 22: Table 11: Average numbers characterizing different attributes of a SWE-bench task instance grouped

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | 2024, ICLR |
| Official open-source implementation | https://github.com/SWE-bench/SWE-bench at `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
