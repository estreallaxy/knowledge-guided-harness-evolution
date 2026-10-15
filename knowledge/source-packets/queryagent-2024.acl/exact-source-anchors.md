# Exact source anchors

## Selected mechanism

Detect errors from intermediate environment feedback, map them to differentiated repair guidelines, and trigger correction only when needed.

## Paper anchors

- p. 1: framework called QueryAgent, which solves
- p. 2: framework called QueryAgent to explore more mately a 50% reduction in API invocation costs
- p. 6: method outperforms all few-shot methods that re- w/o ERASER 43.7 35.3
- p. 7: method, zero-shot SC failed to boost the perfor- a higher proportion of low-quality candidates. In
- p. 8: approach. Compared to GrailQA (75% non-i.i.d.), uses the final result to conduct correction on ev-
- p. 9: Limitations Computational Linguistics (Volume 1: Long Papers),
- p. 11: Algorithm 1: QueryAgent
- p. 12: method also needs manually written examples, thus
- p. 12: method to enumerate and score logic form candi-
- p. 19: approach to solve the question. Please re-generate only Thought STEPS + 1 and Action STEPS + 1.
- p. 21: approach to solve this question.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `readme.md`
- `requirements.txt`
- `ag_src/agent_utils/config.py`
- `ag_src/agent_utils/prompt_list.py`
- `ag_src/agent_utils/run_exp.py`
- `ag_src/agent_utils/simlarity_search.py`
- `environment.yml`
- `ag_src/agent_utils/__init__.py`
- `ag_src/agent_utils/ag_utils.py`
- `ag_src/graphq_src/GRAPHQ.py`
- `ag_src/graphq_src/sparql_generator.py`
- `ag_src/graphq_src/wikienv_graphq.py`
- `ag_src/__init__.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. ERASER is a rule- and prompt-level selective repair mechanism with no parameter update. Experiments include transfer to AgentBench; the official code implements error detection, guidelines, and stepwise correction.

## Symbol-level code anchors

- `ag_src/agent_utils/simlarity_search.py:39` — `get_openai_embedding`
- `ag_src/agent_utils/ag_utils.py:24` — `clean_str`
- `ag_src/graphq_src/GRAPHQ.py:20` — `webthink`
- `ag_src/graphq_src/sparql_generator.py:17` — `PyQL`
- `ag_src/graphq_src/wikienv_graphq.py:9` — `WikiEnv`
