# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `toolbench/tooleval/requirements.txt`
- `toolbench/retrieval/inference_example.py`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_default/config.yaml`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_fn/config.yaml`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_normalized/config.yaml`
- `toolbench/tooleval/run_convert_answer.sh`
- `toolbench/tooleval/run_pass_rate.sh`
- `toolbench/tooleval/run_preference.sh`
- `config_example.py`
- `toolbench/inference/qa_pipeline_open_domain.py`
- `scripts/main.py`

## Upstream command excerpts

```text
pip install -r requirements.txt
```

```text
├── /data/
│  ├── /instruction/
│  ├── /answer/
│  ├── /toolenv/
│  ├── /retrieval/
│  ├── /test_instruction/
│  ├── /test_query_ids/
│  ├── /retrieval_test_query_ids/
│  ├── toolllama_G123_dfs_train.json
│  └── toolllama_G123_dfs_eval.json
├── /reproduction_data/
│  ├── /chatgpt_cot/
│  ├── /chatgpt_dfs/
│  ├── ...
│  └── /toolllama_dfs/
```

```text
export PYTHONPATH=./
python preprocess/extract_api_details.py
python preprocess/extract_category_tool_details.py
python preprocess/extract_tool_database.py
```

```text
export PYTHONPATH=./
python scripts/anytoolbench_generation.py --output_path atb_data/anytoolbench_new.json
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
