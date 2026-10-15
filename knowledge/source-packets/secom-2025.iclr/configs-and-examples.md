# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `setup.py`
- `.pre-commit-config.yaml`
- `experiment/run.sh`
- `secom/configs/bm25.yaml`
- `secom/configs/fast.yaml`
- `secom/configs/mpnet.yaml`
- `example/example.json`

## Upstream command excerpts

```text
pip install llmlingua
pip install -e .
```

```text
pip install python-dotenv
```

```text
OPENAI_API_KEY=""
OPENAI_API_BASE=""
```

```text
from secom import SeCom

memory_manager = SeCom(granularity="segment")

conversation_history = [
    [
        "First session of a very looooooong conversation history",
        "The second user-bot turn of the first session",
    ],
    ["Second Session ..."],
]
requests = ["A question regarding the conversation history", "Another question"]
result = memory_manager.get_memory(
    requests, conversation_history, compress_rate=0.9, retrieve_topk=1
)
print(result["retrieved_texts"])
# >>>
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
