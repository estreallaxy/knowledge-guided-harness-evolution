# Exact source anchors

## Selected mechanism

Extract only the reported **training-free** GraphSearch/SGC planning variants: task dependency graph construction and connected subgraph/path selection. Trained GNN variants are excluded.

## Paper anchors

- p. 6: limitations discussed previously. Furthermore, GNNs have demonstrated proficiency in handling
- p. 7: Evaluation: For the datasets from TaskBench, we split 3000 samples for training and 500 samples
- p. 9: experiment on the newly released planning benchmark UltraTool [20], which features a relatively
- p. 10: Limitations: Despite the encouraging performance, there are limitations that highlight significant
- p. 25: algorithm used to find the shortest paths from a single source vertex to all other vertices in a weighted
- p. 30: Method
- p. 32: results in a performance improvement of 17.83%, GAT contributes to a 17.48% increase, GraphSAGE
- p. 36: framework. Furthermore, we will empirically show that with more accurately planned tasks, i.e.,
- p. 37: limitations.
- p. 41: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 43: results?
- p. 46: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `README.assets/README_zh.md`
- `GraphToken/evaluate.py`
- `GraphToken/main.py`
- `GraphToken/plan_dataset.py`
- `GraphToken/run.sh`
- `trainfree/graphsearch.py`
- `evaluate.py`
- `GraphToken/ckpt.py`
- `GraphToken/gnn.py`
- `GraphToken/graph_llm.py`
- `finetunellm/main.py`
- `finetunellm/user_prompt.py`
- `trainfree/direct_diffprompt.py`
- `traingnn/main.py`
- `finetunellm_script.sh`
- `trainfree_script.sh`
- `traingnn_reproduce.sh`
- `finetunellm/inference.py`
- `trainfree/direct.py`
- `trainfree/sgc.py`
- `traingnn/gnn.py`
- `traingnn/model.py`
- `traingnn/sampler.py`
- `utils/__init__.py`
- `utils/dataset.py`
- `utils/datautil.py`
- `utils/general_utils.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Extract only the reported **training-free** GraphSearch/SGC planning variants: task dependency graph construction and connected subgraph/path selection. Trained GNN variants are excluded.

## Symbol-level code anchors

- `GraphToken/evaluate.py:7` — `reformat_task_nodes`
- `GraphToken/plan_dataset.py:17` — `TaskPlanningDataset`
- `trainfree/graphsearch.py:12` — `get_llm_response`
- `evaluate.py:9` — `f1_score`
- `GraphToken/ckpt.py:5` — `save_checkpoint`
- `GraphToken/gnn.py:6` — `build_conv`
- `GraphToken/graph_llm.py:15` — `GraphToken`
- `finetunellm/main.py:20` — `prepare_llm_training_data`
- `trainfree/direct_diffprompt.py:13` — `inference_one_case`
- `traingnn/main.py:16` — `build_tool_textual_sim_graph`
- `trainfree/direct.py:13` — `inference_one_case`
- `trainfree/sgc.py:17` — `mean_pooling`
