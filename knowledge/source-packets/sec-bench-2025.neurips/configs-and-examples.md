# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `requirements.txt`
- `config.example.toml`
- `run_preprocessor.sh`

## Upstream command excerpts

```text
git clone --recurse-submodules https://github.com/SEC-bench/SEC-bench.git
cd SEC-bench
```

```text
conda create -n secb python=3.12
conda activate secb
```

```text
pip install -r requirements.txt
```

```text
# Required API tokens
export GITHUB_TOKEN=<your_github_token>
export GITLAB_TOKEN=<your_gitlab_token>
export OPENAI_API_KEY=<your_openai_api_key>
export ANTHROPIC_API_KEY=<your_anthropic_api_key>

# Hugging Face configuration
export HF_TOKEN_PATH=$HOME/.cache/hf_hub_token
export HF_HOME=<path/to/huggingface>
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
