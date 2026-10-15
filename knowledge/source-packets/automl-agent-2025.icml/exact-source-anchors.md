# Exact source anchors

## Selected mechanism

Extract retrieval-augmented plan search, parallel specialist execution, and multi-stage verification through off-the-shelf LLM APIs. The optional prompt-agent LoRA path is excluded.

## Paper anchors

- p. 2: framework, AutoML-Agent, for full-pipeline AutoML from
- p. 3: Framework
- p. 4: results are then verified against the user’s requirements via straints like expected accuracy and inference latency.
- p. 4: implementation verification (Figure 2(c) and Line 24) is con- • Model. The model key captures the expected model char-
- p. 5: Algorithm 1 Overall Procedure of AutoML-Agent […, "problem": { "area": "computer vision",
- p. 5: implementation and deployment. It provides information original plan pi ∈ P into a smaller set of sub-tasks si
- p. 6: Implementation Verification (ImpVer) This implemen-
- p. 6: framework by comparing AutoML-Agent with handcrafted
- p. 6: framework incorporates three verification steps to guarantee
- p. 6: implementation verification due to runtime errors. descriptions to represent constraint-aware and constraint-
- p. 7: Evaluation Metrics For a comprehensive evaluation, we be considered easier tasks, all methods have higher SR
- p. 7: Implementation Details Except for the Ap that is

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `requirements.txt`
- `agent_manager/retriever.py`
- `data_agent/retriever.py`
- `model_agent/retriever.py`
- `prompt_agent/__init__.py`
- `prompt_agent/schema.json`
- `configs.py`
- `prompt_agent/WizardLAMP/template.json`
- `prompt_agent/WizardLAMP/template_schema.json`
- `agent_manager/__init__.py`
- `data_agent/__init__.py`
- `experiments/constraint_prompts.py`
- `experiments/evaluation.py`
- `experiments/free_prompts.py`
- `model_agent/__init__.py`
- `operation_agent/__init__.py`
- `operation_agent/execution.py`
- `prompt_pool/__init__.py`
- `prompt_pool/image_classification.py`
- `prompt_pool/node_classification.py`
- `prompt_pool/tabular_classification.py`
- `prompt_pool/tabular_clustering.py`
- `prompt_pool/tabular_regression.py`
- `prompt_pool/text_classification.py`
- `prompt_pool/ts_forecasting.py`
- `experiments/__init__.py`
- `experiments/execution.py`
- `utils/__init__.py`
- `utils/embeddings.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Extract retrieval-augmented plan search, parallel specialist execution, and multi-stage verification through off-the-shelf LLM APIs. The optional prompt-agent LoRA path is excluded.

## Symbol-level code anchors

- `agent_manager/retriever.py:14` — `retrieve_kaggle`
- `data_agent/retriever.py:12` — `retrieve_datasets`
- `model_agent/retriever.py:10` — `retrieve_models`
- `prompt_agent/__init__.py:67` — `PromptAgent`
- `configs.py:1` — `Configs`
- `agent_manager/__init__.py:67` — `AgentManager`
- `data_agent/__init__.py:33` — `DataAgent`
- `experiments/evaluation.py:11` — `normalized_performance_score`
- `model_agent/__init__.py:34` — `ModelAgent`
- `operation_agent/__init__.py:51` — `OperationAgent`
- `operation_agent/execution.py:5` — `execute_script`
- `prompt_pool/image_classification.py:33` — `preprocess_data`
