# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `benchmarks/kernel-bench/requirements.txt`
- `benchmarks/webarena/requirements.txt`
- `benchmarks/webarena/browser_env/env_config.py`

## Upstream command excerpts

```text
agentic-benchmarks/
├── ABC.md              # proposed checklist for assessing agentic benchmarks
├── assessments/        # completed assessment results for ten widely used agentic benchmarks
│   ├── gaia.yaml
│   ├── swe-bench.yaml
│   ├── ....
├── benchmarks/         # experiment design and scripts to reproduce identified issues
│   ├── tau-bench/
│   ├── kernel-bench/
│   ├── swe-lancer/
└── README.md
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
