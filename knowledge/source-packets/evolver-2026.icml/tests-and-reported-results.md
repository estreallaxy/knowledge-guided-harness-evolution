# Tests and reported results

## Evidence boundary

The retained snapshot contains the official non-training prompts, data models, storage routes, maintenance operations, and retrieval services. It intentionally excludes policy-training code, trained weights, task datasets, generated trajectories, result dumps, and benchmark answers.

## Direct checks for reuse

| Check | Official location | Expected invariant |
| --- | --- | --- |
| Principle schema and counters | `official-code/evolver/experience/milvusdb/models.py` | A principle retains its description, structured triples, metric score, usage count, success count, and supporting trajectory identifiers. |
| Insert and merge support | `official-code/evolver/experience/milvusdb/routers/principles.py` | A candidate can be created or an existing principle can be updated without changing model parameters. |
| Utility-based cleanup | `official-code/evolver/experience/milvusdb/routers/principles.py` | Entries below the requested metric threshold can be removed. |
| Query-conditioned retrieval | `official-code/evolver/experience/milvusdb/routers/search.py` | Retrieval returns principles ranked for the incoming query. |
| Trajectory provenance | `official-code/evolver/experience/milvusdb/routers/trajectories.py` | Stored trajectories preserve outcomes and the identifiers of retrieved principles. |

## Reported paper results

The paper evaluates the full EvolveR system in Section 4 (PDF pp.6–8). Those results include the optional policy-reinforcement stage and therefore support the complete paper system, not an isolated causal claim for the non-training subset retained here. The retained subset is justified by the frozen-policy mechanism in Sections 3.2.1–3.2.2 and must be evaluated independently when transplanted into a harness.
