# Exact source anchors

## Selected mechanism

Recursively cluster and summarize documents into a multi-level tree, then retrieve nodes at the granularity demanded by the query.

## Paper anchors

- p. 3: approach is widely adopted, Nair et al. (2023) highlights a potential shortcoming: contiguous seg-
- p. 5: method flattens the multi-layered tree into a single layer, essentially bringing all the nodes onto the
- p. 6: Results on 20 stories from the QASPER dataset Qualitative Study We conduct a qualitative
- p. 6: results, so we use this querying strategy for our focuses on thematic, multi-hop questions using
- p. 10: Evaluation Datasets The three evaluation datasets used in our experiments—QuALITY,
- p. 18: Algorithm 1 Tree Traversal Algorithm
- p. 19: Algorithm 2 Collapsed Tree Algorithm

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE.txt`
- `README.md`
- `requirements.txt`
- `raptor/RetrievalAugmentation.py`
- `raptor/tree_retriever.py`
- `raptor/FaissRetriever.py`
- `raptor/Retrievers.py`
- `raptor/cluster_tree_builder.py`
- `raptor/tree_builder.py`
- `raptor/tree_structures.py`
- `raptor/EmbeddingModels.py`
- `raptor/QAModels.py`
- `raptor/SummarizationModels.py`
- `raptor/__init__.py`
- `raptor/cluster_utils.py`
- `raptor/utils.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Index construction and retrieval use frozen embedding/LLM calls; no target model training is required. The paper provides controlled retrieval QA results and official code implements tree construction and retrieval.

## Symbol-level code anchors

- `README.md:106` — `CustomSummarizationModel`
- `raptor/RetrievalAugmentation.py:18` — `RetrievalAugmentationConfig`
- `raptor/tree_retriever.py:19` — `TreeRetrieverConfig`
- `raptor/FaissRetriever.py:14` — `FaissRetrieverConfig`
- `raptor/Retrievers.py:5` — `BaseRetriever`
- `raptor/cluster_tree_builder.py:17` — `ClusterTreeConfig`
- `raptor/tree_builder.py:24` — `TreeBuilderConfig`
- `raptor/tree_structures.py:4` — `Node`
- `raptor/EmbeddingModels.py:11` — `BaseEmbeddingModel`
- `raptor/QAModels.py:15` — `BaseQAModel`
- `raptor/SummarizationModels.py:11` — `BaseSummarizationModel`
- `raptor/cluster_utils.py:23` — `global_cluster_embeddings`
