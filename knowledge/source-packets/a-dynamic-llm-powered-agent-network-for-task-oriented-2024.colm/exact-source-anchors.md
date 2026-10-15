# Exact source anchors

## Selected mechanism

Unsupervised Agent Importance Score, task/domain team selection, dynamic communication, and early stopping. Optimization is over the agent network at inference time, not model weights.

## Paper anchors

- p. 3: Evaluation of the Contribution of LLM-Powered Agents It is non-trivial to evaluate the
- p. 4: Method Single Exec. LLM-Blender LLM Debate Reflexion CAMEL AgentVerse DyLAN
- p. 4: framework that supports multiple agents with roles and tools, early stopping (Section 3.3.2),
- p. 7: Method Pass@1 #API Calls Success #API
- p. 7: Method Reward
- p. 8: Method Prompting Algebra Geometry Overall
- p. 8: Method STEM Other Overall Task #Agents #API Calls
- p. 8: method BOLAA (Liu et al., 2023), and a single-agent method LATS as strong baselines.
- p. 8: limitations, please refer to Appendix B.1 for details.
- p. 9: 4.3 Ablation Studies
- p. 16: Algorithm 1 The Inference Process of DyLAN on an Algorithm 2 The Team Optimization
- p. 17: method from the origin paper (Hendrycks et al., 2021b). We construct DyLAN with 4 agents

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `code/requirements.txt`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Unsupervised Agent Importance Score, task/domain team selection, dynamic communication, and early stopping. Optimization is over the agent network at inference time, not model weights.

## Additional retained implementation anchors

- `code/demo/run_DyLAN.py`
- `code/HumanEval/exp_human_eval.sh`
- `code/HumanEval/llmlp_listwise_human_eval.py`

## Symbol-level code anchors

- `code/demo/run_DyLAN.py:30` — `set_rd_seed`
- `code/HumanEval/llmlp_listwise_human_eval.py:29` — `set_rd_seed`
