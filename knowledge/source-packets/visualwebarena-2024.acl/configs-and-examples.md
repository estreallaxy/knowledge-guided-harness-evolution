# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.cfg`
- `setup.py`
- `tests/test_evaluation_harness/configs/exact_image_failure.json`
- `tests/test_evaluation_harness/configs/exact_image_resize_failure_1.json`
- `tests/test_evaluation_harness/configs/exact_image_resize_failure_2.json`
- `tests/test_evaluation_harness/configs/exact_image_resize_template.json`
- `tests/test_evaluation_harness/configs/exact_image_success.json`
- `tests/test_evaluation_harness/configs/func_eval_fail.json`
- `tests/test_evaluation_harness/configs/func_eval_success.json`
- `tests/test_evaluation_harness/configs/func_url_func_1.json`
- `tests/test_evaluation_harness/configs/func_url_func_2.json`
- `tests/test_evaluation_harness/configs/html_content_element_exact_match.json`
- `tests/test_evaluation_harness/configs/html_content_exact_match.json`
- `tests/test_evaluation_harness/configs/html_content_url_comb.json`
- `tests/test_evaluation_harness/configs/html_required_values_failure_1.json`
- `tests/test_evaluation_harness/configs/html_required_values_success_1.json`
- `tests/test_evaluation_harness/configs/image_evaluator_yes.json`
- `tests/test_evaluation_harness/configs/image_evaluator_yes_direct_img.json`
- `tests/test_evaluation_harness/configs/image_evaluator_yes_no.json`
- `tests/test_evaluation_harness/configs/string_match.json`
- `tests/test_evaluation_harness/configs/url_exact_match.json`
- `browser_env/env_config.py`
- `llms/lm_config.py`
- `run.py`
- `run_demo.py`
- `wa_parallel_run.sh`
- `scripts/check_error_runs.py`

## Upstream command excerpts

```text
# Python 3.10 (or 3.11, but not 3.12 cause 3.12 deprecated distutils needed here)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
pip install -e .
```

```text
pytest -x
```

```text
export DATASET=visualwebarena
```

```text
export CLASSIFIEDS="<your_classifieds_domain>:9980"
export CLASSIFIEDS_RESET_TOKEN="4b61655535e7ed388f0d40a93600254c"  # Default reset token for classifieds site, change if you edited its docker-compose.yml
export SHOPPING="<your_shopping_site_domain>:7770"
export REDDIT="<your_reddit_domain>:9999"
export WIKIPEDIA="<your_wikipedia_domain>:8888"
export HOMEPAGE="<your_homepage_domain>:4399"
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
