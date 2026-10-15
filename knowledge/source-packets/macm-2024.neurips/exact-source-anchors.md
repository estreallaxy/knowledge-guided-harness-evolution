# Exact source anchors

## Selected mechanism

Prompted condition-mining roles expose implicit constraints, reason over them, and aggregate a final solution. It is explicitly positioned as training-free prompt engineering.

## Paper anchors

- p. 2: Method Accuracy Generalizability
- p. 3: 3 Method
- p. 6: 4 Experiment
- p. 8: Method diff (%) stat (%) calc (%) Method Acc. (%)
- p. 8: 4.4 Ablation Study
- p. 14: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 16: results?
- p. 19: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `requirements.txt`
- `main.py`
- `prompt/prompts.py`
- `io/io.py`
- `macm/executor.py`
- `macm/judge.py`
- `macm/thinker.py`
- `utils/gpt.py`
- `utils/gpt_robots.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Prompted condition-mining roles expose implicit constraints, reason over them, and aggregate a final solution. It is explicitly positioned as training-free prompt engineering.

## Symbol-level code anchors

- `main.py:11` — `check_condition`
- `io/io.py:9` — `generate_Answer`
- `macm/executor.py:5` — `Execute_steps`
- `macm/judge.py:5` — `Judge_condition`
- `macm/thinker.py:5` — `Analysis_conditions`
- `utils/gpt.py:11` — `chat_gpt`
- `utils/gpt_robots.py:7` — `generate_from_thinker`
