# Exact source anchors

## Selected mechanism

Agentic Benchmark Checklist for task/outcome validity, tool versioning, state reset, ground-truth isolation, evaluator robustness, and reproducible flaw tests.

## Paper anchors

- p. 3: results) are keys to ensure rigorous agentic evaluation.
- p. 3: evaluation [63, 82]. In terms of task validity, the rate limits of the websites implemented in WebArena
- p. 4: evaluation frameworks [1, 45, 46, 51] together with documented issues in agentic benchmarks
- p. 5: Implementation
- p. 5: Implementation. Even with a robust setup of tools and environments, subtle implementation
- p. 5: implementation bugs (T.10). For example, if agents consistently fail on easy tasks, this may indicate
- p. 8: evaluation methods. For each part of ABC, we calculated the average scores of applicable items. We
- p. 8: evaluation methods.
- p. 8: implementation, and none satisfies every reporting criterion.
- p. 10: 7 Limitations and Impact Statement
- p. 10: Limitations. As the first study to systematically investigate the issue of evaluation rigor in agen-
- p. 14: evaluation of machine translation. In Proceedings of the 40th annual meeting of the Association

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `benchmarks/webarena/browser_env/env_config.py:1` — environment endpoint configuration used by the reproducibility checks.

- `README.md`
- `benchmarks/kernel-bench/README.md`
- `benchmarks/kernel-bench/requirements.txt`
- `benchmarks/osworld/README.md`
- `benchmarks/swe-lancer/README.md`
- `benchmarks/tau-bench/README.md`
- `benchmarks/webarena/README.md`
- `benchmarks/webarena/requirements.txt`
- `benchmarks/webarena/browser_env/env_config.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Archival NeurIPS track; checklist and validation scripts are training-free.
