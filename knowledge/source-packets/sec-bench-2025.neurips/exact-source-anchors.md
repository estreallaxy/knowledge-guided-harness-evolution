# Exact source anchors

## Selected mechanism

Hierarchical Docker images, vulnerability reproduction harness, isolated PoC/patch execution, gold artifacts, multi-agent construction pipeline, and deterministic evaluation commands.

## Paper anchors

- p. 2: framework that leverages the complementary capabilities of specialized LLM agents to overcome
- p. 4: Evaluation Candidate
- p. 7: Ablation on Multi-Agent Framework. We compare S EC V ERIFIER with a single-agent base-
- p. 7: 3 Evaluation
- p. 10: 5 Limitations and Future Work
- p. 10: approach is generalizable to a wider range of vulnerabilities, and we aim to support them in future
- p. 10: evaluation reveals significant performance gaps in SOTA code agents, and we hope SEC-bench will
- p. 16: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 18: results?
- p. 21: limitations, etc.
- p. 36: evaluation, then submission. Security tasks require agents to continuously re-examine the codebase

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `requirements.txt`
- `config.example.toml`
- `run_preprocessor.sh`
- `secb/evaluator/build_eval_instances.py`
- `secb/evaluator/eval_instances.py`
- `secb/evaluator/utils.py`
- `secb/evaluator/view_patch_results.py`
- `secb/evaluator/view_poc_results.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. NeurIPS main paper; released runtime and evaluators are training-free.

## Symbol-level code anchors

- `secb/evaluator/build_eval_instances.py:62` — `PhaseResultDict`
- `secb/evaluator/eval_instances.py:48` — `EvaluationResult`
- `secb/evaluator/utils.py:50` — `extract_sanitizer_report`
- `secb/evaluator/view_patch_results.py:47` — `FailureType`
- `secb/evaluator/view_poc_results.py:47` — `FailureType`
