# Exact source anchors

## Selected mechanism

Diverse model panel, multi-round discussion, confidence elicitation, confidence-weighted voting, and early consensus. Test-time orchestration only.

## Paper anchors

- p. 7: Method Category Method Agent StrategyQA CSQA GSM8K AQuA Date
- p. 7: Method Accuracy Method Accuracy
- p. 7: framework. In particular, we either include (a)
- p. 8: Method Accuracy Method Accuracy
- p. 10: Limitations Ari, Steven Hand, Hadi Hashemi, Le Hou, Joshua
- p. 10: approach proves effective as evidenced by our re- Bryan Richter, Parker Riley, Alex Castro Ros, Au-
- p. 14: Algorithm 1. Required input contains a test prob- Debate (w/ Convincing Expl) 69.5±1.7
- p. 15: Algorithm 1 R E C ONCILE: A Group-Discuss-And-Convince Framework

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `run.py`
- `claude.py`
- `data_utils.py`
- `generation.py`
- `utils.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Diverse model panel, multi-round discussion, confidence elicitation, confidence-weighted voting, and early consensus. Test-time orchestration only.

## Symbol-level code anchors

- `claude.py:11` — `Client`
- `data_utils.py:11` — `StrategyQA`
- `generation.py:28` — `ClaudeModel`
- `utils.py:16` — `prepare_context`
