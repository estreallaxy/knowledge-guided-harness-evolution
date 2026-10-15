# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `benchmark/benign_tools/run_stable_diffusion_model.py`
- `benchmark/harmful_tools/run_stable_diffusion_model.py`

## Upstream command excerpts

```text
uv run inspect eval inspect_evals/agentharm --model openai/gpt-5-nano
uv run inspect eval inspect_evals/agentharm_benign --model openai/gpt-5-nano
```

```text
uv run inspect eval-set inspect_evals/agentharm inspect_evals/agentharm_benign
```

```text
from inspect_ai import eval, eval_set
from inspect_evals.agentharm import agentharm, agentharm_benign
eval(agentharm)
eval_set([agentharm, agentharm_benign], log_dir='logs-run-42')
```

```text
uv run inspect eval inspect_evals/agentharm --limit 10 --sample-shuffle
uv run inspect eval inspect_evals/agentharm_benign --max-connections 10
uv run inspect eval inspect_evals/agentharm --temperature 0.5
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
