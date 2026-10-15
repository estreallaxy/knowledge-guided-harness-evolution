# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `run_script.sh`

## Upstream command excerpts

```text
git clone https://github.com/meetdavidwan/mammrefine.git
cd mammrefine
pip install -r requirements.txt
```

```text
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

```text
bash run_script.sh
```

```text
python example.py
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
