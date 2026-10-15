# Exact source anchors

## Selected mechanism

Multiple model instances perform detection, critique, candidate correction, and reranking; experiments show reranking is more reliable than free-form generation. Inference-time only.

## Paper anchors

- p. 2: approach? (2) Which subtasks benefit from a Wadhwa et al. (2024)’s breakdown of refinement
- p. 3: framework introduced by Chen et al. (2024a),
- p. 4: results in two instances of GPT-4o (2xG), two in- pair. We split the 50 documents into 10 for valida-
- p. 7: method using R ERANK.4 As mentioned in Sec-
- p. 7: approach (2xC) has a lower error matching rate forming multiple rounds of G ENERATE (since it
- p. 8: Method MD MC MR MCS↑ GL↑ MCS↑ GL↑ MCS↑ GL↑
- p. 8: Method MD MC MR MCS↑ G-L↑ model configurations to single or multi-agent se-
- p. 8: results, with results shown in Table 4. Specifically,
- p. 9: results without the context in Appendix B.5. to past refinement and multi-LLM work, as we mea-
- p. 9: Limitations
- p. 10: framework for multi-task and multi-domain scenar-
- p. 17: Method MR MCS↑ G↑ MCS↑ G↑ MCS↑ G↑ MCS↑ G↑ MCS↑ G↑ MCS↑ G↑

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `run_script.sh`
- `src/prompts.py`
- `src/__init__.py`
- `src/critique.py`
- `src/critique_debate.py`
- `src/critique_debate_initial.py`
- `src/detect.py`
- `src/detect_debate.py`
- `src/model.py`
- `src/pipeline.py`
- `src/refine.py`
- `src/refine_debate.py`
- `src/refine_debate_initial.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Multiple model instances perform detection, critique, candidate correction, and reranking; experiments show reranking is more reliable than free-form generation. Inference-time only.

## Symbol-level code anchors

- `src/critique.py:11` — `generate_critique`
- `src/critique_debate.py:16` — `format_agent_answers`
- `src/critique_debate_initial.py:14` — `select_best_critique`
- `src/detect.py:12` — `parse_json_response`
- `src/detect_debate.py:12` — `parse_json_response`
- `src/model.py:6` — `Model`
- `src/pipeline.py:17` — `run_pipeline`
- `src/refine.py:11` — `format_feedback`
- `src/refine_debate.py:15` — `format_agent_answers`
- `src/refine_debate_initial.py:14` — `select_best_summary`
