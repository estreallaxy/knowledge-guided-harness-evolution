# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `moatless/actions/run_tests.py`
- `moatless/runtime/testbed.py`
- `moatless/benchmark/evaluation_config.py`
- `moatless/benchmark/evaluation_runner.py`
- `moatless/benchmark/run_evaluation.py`
- `moatless/runtime/runtime.py`
- `run.sh`

## Upstream command excerpts

```text
pip install moatless-tree-search
```

```text
cp .env.example .env
   # Edit .env with your values
```

```text
# Directory for storing vector index store files  
   export INDEX_STORE_DIR="/tmp/index_store"    

   # Directory for storing clonedrepositories 
   export REPO_DIR="/tmp/repos"

   # Required: At least one LLM provider API key
   export OPENAI_API_KEY="<your-key>"
   export ANTHROPIC_API_KEY="<your-key>"
   export HUGGINGFACE_API_KEY="<your-key>"
   export DEEPSEEK_API_KEY="<your-key>"

   # ...or Base URL for custom LLM API service (optional)
   export CUSTOM_LLM_API_BASE="<your-base-url>"
   export CUSTOM_LLM_API_KEY="<your-key>"

   # Required: API Key for Voyage Embeddings
   export VOYAGE_API_KEY="<your-key>"

   # Optional: Configuration for testbed environment (https://github.com/aorwall/moatless-testbeds)
   export TESTBED_API_KEY="<your-key>"
   export TESTBED_BASE_URL="<your-base-url>"
```

```text
# Launch with direct file loading
moatless-streamlit path/to/trajectory.json

# Launch interactive UI (file can be selected in browser)
moatless-streamlit
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
