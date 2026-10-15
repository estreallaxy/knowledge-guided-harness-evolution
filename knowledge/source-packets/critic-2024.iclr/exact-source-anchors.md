# Exact source anchors

## Selected mechanism

Route an initial answer to an appropriate external checker, turn tool output into a grounded critique, revise, and repeat under a stopping rule.

## Paper anchors

- p. 4: Algorithm 1 CRITIC algorithm
- p. 5: Implementation To improve generality, we avoid relying on task-specific retrievers (Santhanam et al.,
- p. 6: Results As seen in Table 1 and 8: 1) CRITIC dramatically improves over the model’s initial CoT
- p. 6: results across all datasets, settings, and LLMs, requiring only three corrections, while outperforms
- p. 7: Implementation As shown in Figure 2, we utilize the Python interpreter as a tool to get two
- p. 7: results, we use the value of the variable “answer” after the execution is completed. We use
- p. 8: Results As shown in Table 2 and Table 9, 1) CRITIC sizable improves upon the PoT across both
- p. 8: Implementation We use P ERSPECTIVE API5 as a tool to obtain fine-grained toxicity information.
- p. 9: Results The results in Table 3 demonstrate that 1) CRITIC substantially lowers the occurrence
- p. 14: evaluation using gpt-4 with better human alignment. arXiv preprint arXiv:2303.16634, 2023b.
- p. 22: Method Learning Source of feedback
- p. 24: Implementation We experiment with ChatGPT following the setup described in §4.1, using CoT

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `requirements.txt`
- `src/tools/config.py`
- `src/tools/search_api.py`
- `scripts/run_program_critic.sh`
- `scripts/run_program_infer.sh`
- `scripts/run_qa_critic.sh`
- `scripts/run_qa_infer.sh`
- `scripts/run_toxicity_critic.sh`
- `scripts/run_toxicity_infer.sh`
- `src/program/evaluate.py`
- `src/qa/evaluate.py`
- `src/tools/interpreter_api.py`
- `src/tools/perspective_api.py`
- `src/toxicity/evaluate.py`
- `src/toxicity/evaluate_ppl.py`
- `src/utils.py`
- `src/llms/api.py`
- `src/program/critic.py`
- `src/program/inference.py`
- `src/program/utils.py`
- `src/qa/critic.py`
- `src/qa/inference.py`
- `src/qa/utils.py`
- `src/toxicity/critic.py`
- `src/toxicity/inference.py`
- `src/toxicity/utils.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. It is an inference-only validation/revision loop. The paper compares multiple domains and shows external feedback is the active ingredient; the official repository exposes prompts and tool adapters.

## Symbol-level code anchors

- `src/tools/search_api.py:10` — `google`
- `src/program/evaluate.py:10` — `get_metrics`
- `src/qa/evaluate.py:9` — `rejection_sampling_eval`
- `src/tools/interpreter_api.py:4` — `safe_execute`
- `src/tools/perspective_api.py:19` — `batchify`
- `src/toxicity/evaluate.py:10` — `evaluate`
- `src/toxicity/evaluate_ppl.py:8` — `calc_ppl`
- `src/utils.py:13` — `set_seed`
- `src/llms/api.py:13` — `llm`
- `src/program/critic.py:18` — `parse_args`
- `src/program/inference.py:18` — `parse_args`
- `src/program/utils.py:14` — `normalize_answer`
