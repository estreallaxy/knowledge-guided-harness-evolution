# Exact source anchors

## Selected mechanism

Maintain candidate–score history in a meta-prompt; ask an LLM to propose the next instruction and evaluate it as a black-box optimization loop.

## Paper anchors

- p. 4: results in optimization instability and large variance. To improve stability, we prompt the LLM to
- p. 4: experiment setups to Appendix B. On both tasks, we see LLMs properly capture the optimization
- p. 6: Implementation details. We use temperature 0 (greedy decoding) to evaluate generated instructions.
- p. 9: results are similar, indicating that the error cases alone are not informative enough for the optimizer
- p. 12: experiment: Using counterfactuals to improve moral reasoning. arXiv preprint arXiv:2306.14308,
- p. 33: approach throughout the process.
- p. 39: approach. Specifically: (1) On GSM8K, the best instruction among all 50 is still “Let’s solve the
- p. 40: evaluation, we compare our approach to the Genetic Algorithm (GA) and Differential Evolution (DE)

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `misc/prompt_history/README.md`
- `opro/evaluation/eval_utils_test.py`
- `opro/prompt_utils.py`
- `opro/evaluation/eval_utils.py`
- `opro/evaluation/evaluate_instructions.py`
- `opro/evaluation/metrics.py`
- `opro/optimization/opt_utils.py`
- `opro/optimization/optimize_instructions.py`
- `opro/optimization/optimize_linear_regression.py`
- `opro/optimization/optimize_tsp.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. No parameters are updated. The paper evaluates iterative prompt optimization and the official code exposes meta-prompt construction, candidate generation, and objective evaluation.

## Symbol-level code anchors

- `opro/evaluation/eval_utils_test.py:29` — `UtilsTest`
- `opro/prompt_utils.py:21` — `call_openai_server_single_prompt`
- `opro/evaluation/eval_utils.py:47` — `read_jsonl`
- `opro/evaluation/evaluate_instructions.py:98` — `main`
- `opro/evaluation/metrics.py:165` — `remove_punctuation_from_string`
- `opro/optimization/opt_utils.py:33` — `extract_string_in_square_brackets`
- `opro/optimization/optimize_instructions.py:104` — `main`
- `opro/optimization/optimize_linear_regression.py:60` — `main`
- `opro/optimization/optimize_tsp.py:66` — `main`
