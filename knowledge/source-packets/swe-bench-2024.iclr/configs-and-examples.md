# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `tests/test_grading_truncated_ids.py`
- `tests/test_run_metadata.py`
- `.pre-commit-config.yaml`
- `swebench/harness/run_evaluation.py`
- `swebench/harness/modal_eval/run_evaluation_modal.py`
- `swebench/harness/modal_eval/run_evaluation_modal_entrypoint.py`
- `swebench/collect/run_build_dataset_ft.sh`
- `swebench/collect/run_get_tasks_pipeline.sh`
- `swebench/inference/run_api.py`
- `swebench/inference/run_live.py`
- `swebench/inference/run_llama.py`

## Upstream command excerpts

```text
from datasets import load_dataset
swebench = load_dataset('princeton-nlp/SWE-bench', split='test')
```

```text
git clone git@github.com:SWE-bench/SWE-bench.git
cd SWE-bench
pip install -e .

# Required for local image builds with the v5 CLI. This path is only an example.
git clone --depth 1 https://github.com/SWE-bench/swe-bench-tasks.git ./swe-bench-tasks
swebench dataset check ./swe-bench-tasks
```

```text
swebench eval verified --gold \
    -i sympy__sympy-20590 \
    --run-id validate-gold \
    --task-repo ./swe-bench-tasks
```

```text
swebench eval verified -p <path_to_predictions> --run-id <run_id> -j <num_workers>
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
