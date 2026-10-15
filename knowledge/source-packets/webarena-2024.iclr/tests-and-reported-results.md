# Tests and reported results

## Official verification entry points

- `tests/test_browser_env/test_action_functionalities.py`
- `tests/test_browser_env/test_actions.py`
- `tests/test_browser_env/test_playwright_actions.py`
- `scripts/generate_test_data.py`
- `tests/conftest.py`
- `evaluation_harness/__init__.py`
- `evaluation_harness/evaluators.py`
- `evaluation_harness/helper_functions.py`
- `scripts/check_error_runs.py`
- `tests/test_browser_env/test_auth_cookie.py`
- `tests/test_browser_env/test_script_browser_env.py`
- `check_errors.sh`

## Published result anchors

- p. 7: Table 1: We introduce two evaluation approaches. rinfo (top) measures the correctness of performing
- p. 8: Table 2. GPT-4 (OpenAI, 2023) with CoT
- p. 9: Table 4: The comparison between our benchmark and existing benchmarks on grounding natural
- p. 17: Table 5: The task success rate (SR %) of GPT-3.5- TURBO -16 K -0613 with temperature 0.0.
- p. 17: Table 6: The accuracy (%) of two versions of GPT-4 on judging if dates and time duration of different

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/web-arena-x/webarena at `dce04686a56253aefba7b18a4fa0937cf1dc987b` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
