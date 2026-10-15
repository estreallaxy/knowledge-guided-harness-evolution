# Exact source anchors

## Selected mechanism

Contrast high- and low-performing traces, attribute performance gaps to tool-use decisions, and update actor instructions with comparator-generated rules.

## Paper anchors

- p. 6: results, while those with specific product descriptions and more including type, and any mentioned products.
- p. 7: results with the ground truth answers in the datasets, using Hit@1, Hit@5, Recall@20, and Mean
- p. 14: Evaluation for Tool Learning Capabilities of Large Language Models in Real-world Scenarios.
- p. 24: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 26: results?
- p. 29: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `requirements.txt`
- `scripts/run_avatar_optimizer.py`
- `config/default_args.json`
- `avatar/tools/relational_extraction.py`
- `avatar/tools/text_extraction.py`
- `scripts/eval.py`
- `scripts/eval_avatar_by_indices.py`
- `scripts/eval_avatar_flickr30k_entities.sh`
- `scripts/eval_avatar_stark.sh`
- `scripts/eval_react_flickr30k_entities.sh`
- `scripts/eval_react_stark.sh`
- `scripts/run_avatar_flickr30k_entities.sh`
- `scripts/run_avatar_stark.sh`
- `avatar/models/dense_retriever.py`
- `avatar/tools/__init__.py`
- `avatar/tools/clip.py`
- `avatar/tools/compute_metrics.py`
- `avatar/tools/debug_print.py`
- `avatar/tools/embedding.py`
- `avatar/tools/flickr30k_entities.py`
- `avatar/tools/llm_funcs.py`
- `avatar/tools/nodes.py`
- `avatar/tools/parser.py`
- `avatar/tools/tool.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The comparator/actor loop uses inference-time LLM calls and scored examples rather than weight updates. The paper reports seven-task results and the repository includes prompts, actor/comparator logic, and evaluation.

## Symbol-level code anchors

- `README.md:50` — `metric`
- `avatar/tools/relational_extraction.py:6` — `GetRelatedNodes`
- `avatar/tools/text_extraction.py:11` — `GetFullInfo`
- `scripts/eval_avatar_by_indices.py:15` — `split_dataset_indices`
- `avatar/models/dense_retriever.py:29` — `arg_parse`
- `avatar/tools/clip.py:10` — `GetCLIPTextEmbedding`
- `avatar/tools/compute_metrics.py:7` — `ComputeF1Score`
- `avatar/tools/debug_print.py:5` — `Print2File`
- `avatar/tools/embedding.py:11` — `GetNodeEmbedding`
- `avatar/tools/flickr30k_entities.py:7` — `GetBagOfPhrases`
- `avatar/tools/llm_funcs.py:20` — `LLMSummarize`
- `avatar/tools/nodes.py:6` — `GetNodeIDs`
