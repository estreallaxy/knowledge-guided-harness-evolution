# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `main.py`

## Upstream command excerpts

```text
~$ conda create -n mdagents python>=3.9
```

```text
~$ pip install -r requirements.txt
```

```text
~$ conda activate mdagents
```

```text
~$ export openai_api_key="your_openai_api_key_here"
~$ export genai_api_key="your_genai_api_key_here"
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
