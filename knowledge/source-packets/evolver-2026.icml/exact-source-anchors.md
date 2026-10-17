# Exact source anchors

## Selected mechanism

Freeze the policy model while converting successful and failed interaction trajectories into structured strategic principles. Maintain the principle base through semantic matching, evidence merging, empirical utility updates, and pruning, then retrieve principles to guide later tool-using interactions. The policy-reinforcement stage is excluded.

## Paper anchors

| Evidence target | Exact location | What it establishes |
| --- | --- | --- |
| Closed experience lifecycle | PDF p.3, Section 3 and Section 3.2; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Separates offline self-distillation, online use, and the optional policy-update stage. |
| Success/failure principle extraction | PDF pp.3–4, Section 3.2.1; markers `===== PDF p.3 =====` and `===== PDF p.4 =====` | Distills a guiding principle from success or a cautionary principle from failure while policy parameters are frozen. |
| Deduplication and integration | PDF p.4, Section 3.2.1; marker `===== PDF p.4 =====` | Uses embedding retrieval followed by semantic equivalence judgment to add a novel principle or merge evidence into an existing one. |
| Utility score and pruning | PDF pp.4–5, Equation (2); markers `===== PDF p.4 =====` and `===== PDF p.5 =====` | Defines empirical principle utility from success and usage counts and removes entries below a pruning threshold. |
| Online principle retrieval | PDF p.5, Section 3.2.2; marker `===== PDF p.5 =====` | Retrieves strategic principles inside the reasoning loop and records new trajectories for later distillation. |
| Evaluation evidence | PDF pp.6–8, Section 4; markers `===== PDF p.6 =====` through `===== PDF p.8 =====` | Reports the experimental setup, main comparisons, and ablations for the complete paper system. |

## Official-code anchors

| Exact location | Symbol | Role in the selected mechanism |
| --- | --- | --- |
| `official-code/evolver/experience/prompts.py:10` | `SUMMARIZE_SUCCESSFUL_TRAJECTORY_PROMPT` | Extracts structured guidance from a successful trajectory. |
| `official-code/evolver/experience/prompts.py:43` | `SUMMARIZE_FAILED_TRAJECTORY_PROMPT` | Extracts a cautionary principle from a failed trajectory. |
| `official-code/evolver/experience/prompts.py:77` | `MATCH_PRINCIPLE_PROMPT` | Performs semantic equivalence judgment before insertion or merge. |
| `official-code/evolver/experience/milvusdb/principle_client.py:13` | `PrincipleVectorDBClient` | Stores principle text, structure, utility counts, and supporting trajectory identifiers. |
| `official-code/evolver/experience/milvusdb/routers/principles.py:156` | `update_principle` | Updates an existing principle and its accumulated evidence. |
| `official-code/evolver/experience/milvusdb/routers/principles.py:258` | `clean_low_metric_principles` | Prunes principles below the configured metric threshold. |
| `official-code/evolver/experience/milvusdb/routers/search.py:13` | `search_principles` | Retrieves principles relevant to a new query. |
| `official-code/evolver/experience/milvusdb/routers/trajectories.py:17` | `create_trajectory` | Persists interaction evidence that can support later principle maintenance. |
| `official-code/evolver/search/retrieval.py:165` | `BM25Retriever` | Provides sparse retrieval for stored material. |
| `official-code/evolver/search/retrieval.py:236` | `DenseRetriever` | Provides embedding-based retrieval for stored material. |

All code locations refer to official revision `63834b727ee6e7af3410657de36eb845814249ba`. Paper page numbers refer to the fixed local proceedings PDF.
