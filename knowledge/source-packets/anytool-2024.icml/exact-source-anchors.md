# Exact source anchors

## Selected mechanism

Organize APIs hierarchically, retrieve a small candidate set, solve with function calling, and reactivate search through self-reflection when execution is impracticable.

## Paper anchors

- p. 3: Evaluation for Realistic Scenarios. The evaluation frame- models, where the language model itself is used via LLM-
- p. 4: evaluation protocols and criteria, to ascertain the solution’s evaluation phase of ToolLLM, which assesses the potential
- p. 4: Evaluation Protocol. We first revisit the evaluation pro-
- p. 8: Method G1-T (%) G1-C (%) G3-I (%) 32 58.9 55.3
- p. 9: Method G1-T (%) G1-C (%) G3-I (%)

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `toolbench/tooleval/README.md`
- `toolbench/tooleval/README_ZH.md`
- `toolbench/tooleval/requirements.txt`
- `toolbench/inference/Prompts/Tree_search_prompts.py`
- `toolbench/retrieval/inference_example.py`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_default/config.yaml`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_fn/config.yaml`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_normalized/config.yaml`
- `toolbench/retrieval/api_evaluator.py`
- `toolbench/retrieval/train.py`
- `toolbench/tooleval/run_convert_answer.sh`
- `toolbench/tooleval/run_pass_rate.sh`
- `toolbench/tooleval/run_preference.sh`
- `anytool/prompt_template.py`
- `config_example.py`
- `toolbench/inference/qa_pipeline_open_domain.py`
- `toolbench/model/compression.py`
- `toolbench/tooleval/automatic_check_query_solved.py`
- `toolbench/tooleval/automatic_eval_sample.py`
- `toolbench/tooleval/convert_answers.py`
- `toolbench/tooleval/convert_to_answer_format.py`
- `toolbench/tooleval/eval_and_update_leaderboard.py`
- `toolbench/tooleval/eval_pass_rate.py`
- `toolbench/tooleval/eval_preference.py`
- `toolbench/tooleval/evaluators_comparison.py`
- `toolbench/tooleval/pass_rate.py`
- `toolbench/tooleval/utils.py`
- `toolbench/inference/Algorithms/base_search.py`
- `toolbench/inference/Downstream_tasks/base_env.py`
- `toolbench/inference/Downstream_tasks/rapidapi.py`
- `toolbench/inference/LLM/retriever.py`
- `toolbench/inference/Prompts/ReAct_prompts.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The paper explicitly uses GPT-4 without training external modules and evaluates large API inventories. The repository provides the hierarchical retriever, solver, reflection loop, and evaluation.

## Symbol-level code anchors

- `toolbench/tooleval/README.md:154` — `MyEvaluator`
- `toolbench/tooleval/README_ZH.md:160` — `MyEvaluator`
- `toolbench/retrieval/api_evaluator.py:42` — `compute_ndcg_for_query`
- `toolbench/retrieval/train.py:61` — `log_callback_st`
- `anytool/prompt_template.py:280` — `query_all_categories`
- `toolbench/model/compression.py:11` — `CompressionConfig`
- `toolbench/tooleval/automatic_check_query_solved.py:17` — `parse_args`
- `toolbench/tooleval/automatic_eval_sample.py:17` — `parse_args`
- `toolbench/tooleval/convert_to_answer_format.py:16` — `generate_init_message_node`
- `toolbench/tooleval/eval_and_update_leaderboard.py:33` — `parse_args`
- `toolbench/tooleval/eval_pass_rate.py:14` — `parse_args`
- `toolbench/tooleval/eval_preference.py:36` — `parse_args`
