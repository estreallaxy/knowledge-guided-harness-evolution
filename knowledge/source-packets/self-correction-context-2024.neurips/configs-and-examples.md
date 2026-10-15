# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `BBQ/pyproject.toml`
- `Jailbreak/config.py`
- `BBQ/eval/__main__.py`
- `Jailbreak/main.py`
- `Jailbreak/run_all.sh`

## Upstream command excerpts

```text
conda env create -f environment.yml
conda activate in-context-alignment
```

```text
cd synthetic_experiment
```

```text
export IF_FFN=True
export IF_SOFTMAX=True
python train.py --config conf/train-heads-{head}.yaml
```

```text
export IF_FFN=True
export IF_SOFTMAX=True
python train.py --config conf/train-n_layer-{n_layer}.yaml
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
