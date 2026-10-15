# Exact source anchors

## Selected mechanism

Prompt perplexity estimates per-model expertise; greedy test-time optimization derives selection/fusion weights. It is explicitly training-free and modular to model addition/removal.

## Paper anchors

- p. 6: 4.2 Results
- p. 6: approach of cBTM. PackLLM outperforms cBTM under all values of the number of expert
- p. 8: 5.2 Results
- p. 13: Algorithm 1 Greedy Perplexity Minimization for Test-Time Fusion.
- p. 14: evaluation. BoolQA is a binary classification, while ARC, HellaSwag, and OpenBookQA

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `downstream_tasks/README.md`
- `downstream_tasks/requirements.txt`
- `downstream_tasks/prompt_retrieval.py`
- `downstream_tasks/main.py`
- `downstream_tasks/modeling_llm_fusion.py`
- `downstream_tasks/scripts/run_fusion_common_tasks.sh`
- `downstream_tasks/scripts/run_fusion_stem_tasks.sh`
- `downstream_tasks/get_task.py`
- `downstream_tasks/icl_data.py`
- `downstream_tasks/icl_model.py`
- `downstream_tasks/utils.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Prompt perplexity estimates per-model expertise; greedy test-time optimization derives selection/fusion weights. It is explicitly training-free and modular to model addition/removal.

## Symbol-level code anchors

- `downstream_tasks/prompt_retrieval.py:11` — `get_instance_length`
- `downstream_tasks/main.py:26` — `MyCustomUnpickler`
- `downstream_tasks/modeling_llm_fusion.py:68` — `find_best_mapping`
- `downstream_tasks/scripts/run_fusion_common_tasks.sh:9` — `join`
- `downstream_tasks/scripts/run_fusion_stem_tasks.sh:9` — `join`
- `downstream_tasks/get_task.py:9` — `format_dataset`
- `downstream_tasks/icl_data.py:27` — `MetaICLData`
- `downstream_tasks/icl_model.py:18` — `MetaICLModel`
- `downstream_tasks/utils.py:67` — `mean_pooling`
