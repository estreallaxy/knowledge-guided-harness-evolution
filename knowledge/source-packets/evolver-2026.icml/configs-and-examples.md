# Configurations and examples

## Selected runtime surface

| Official location | Use |
| --- | --- |
| `official-code/evolver/experience/config.py` | Configures the experience store, collection names, retrieval limits, and maintenance thresholds. |
| `official-code/evolver/experience/prompts.py` | Defines success, failure, and semantic-match prompts used by the non-training distillation path. |
| `official-code/evolver/experience/milvusdb/config.py` | Configures embeddings and the local Milvus-backed principle and trajectory stores. |
| `official-code/evolver/experience/milvusdb/start_server.sh` | Starts the official experience-store service. |
| `official-code/evolver/search/retrieval.sh` | Shows the official retrieval-service invocation. |
| `official-code/evolver/search/build_index.sh` | Shows the official index-construction invocation. |

## Integration sequence

1. Persist task trajectories through the trajectory routes.
2. Apply the success or failure distillation prompt to produce a candidate principle.
3. Retrieve nearby principles and use the semantic-match prompt to decide whether to insert or merge.
4. Update usage and success statistics, then remove principles below the configured utility threshold.
5. Retrieve top principles for the next interaction and record which principles were used.

This sequence uses external state and inference-time LLM calls. It does not update model parameters.
