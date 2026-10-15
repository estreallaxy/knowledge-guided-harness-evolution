# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `requirements.txt`
- `model/quant_model/setup.py`
- `demo.py`

## Upstream command excerpts

```text
cd KVzip
pip install -r requirements.txt
pip install flash-attn==2.7.4.post1 --no-build-isolation
make i
```

```text
from model import ModelKVzip

model = ModelKVzip("Qwen/Qwen2.5-7B-Instruct-1M")
context = "This is my basic profile. My name is Kim living in Seoul. My major is computer science."
queries = ["What is my name?", "Do I live in Seoul?"]

kv = model.prefill(context, load_score=False)  # prefill KV cache + importance scoring
kv.prune(ratio=0.3)  # compression ratio, evict 70% KV

for q in queries:
    query_ids = model.apply_template(q)
    output = model.generate(query_ids, kv=kv, update_cache=False)  # efficient inference
    print(q, output)
```

```text
python -B test.py -m [model_name] -d [data_name] --kv_type evict --ratio 0.3
```

```text
python -B test.py -m [model_name] -d scbench_qa_eng --save_head_score
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
