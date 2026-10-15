# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `requirements.txt`
- `setup.py`
- `tests/integration/run_azure.py`
- `tests/integration/run_gateway.py`
- `tests/integration/run_local.py`
- `tests/integration/run_openai.py`
- `tests/integration/run_transformers.py`
- `tests/integration/run_vector_stores.py`
- `main.py`
- `src/hipporag/utils/config_utils.py`
- `examples/_shared.py`
- `examples/demo_azure.py`
- `examples/demo_bedrock.py`
- `examples/demo_bedrock_mantle.py`
- `examples/demo_gateway.py`
- `examples/demo_local.py`
- `examples/demo_openai.py`

## Upstream command excerpts

```text
conda create -n hipporag python=3.10
conda activate hipporag
pip install hipporag
```

```text
export CUDA_VISIBLE_DEVICES=0,1,2,3
export HF_HOME=<path to Huggingface home directory>
export OPENAI_API_KEY=<your openai api key>   # if you want to use OpenAI model

conda activate hipporag
```

```text
uv venv --python 3.10 .venv
source .venv/bin/activate
uv pip install -e .
```

```text
uv pip install -r requirements.txt -c constraints/openai-tested.txt
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
