# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `downstream_tasks/requirements.txt`
- `downstream_tasks/main.py`
- `downstream_tasks/scripts/run_fusion_common_tasks.sh`
- `downstream_tasks/scripts/run_fusion_stem_tasks.sh`

## Upstream command excerpts

```text
./
|---- downstream_tasks/                      # downstream task experiments with PackLLM
|---- language_modeling_tasks/                         # to be updated soon.
```

```text
@article{mavromatis2024packllm,
  title={Pack of LLMs: Model Fusion at Test-Time via Perplexity Optimization},
  author={Mavromatis, Costas and Karypis, Petros and Karypis, George},
  journal={arXiv preprint arXiv:2404.11531},
  year={2024}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
