# G-Memory: hierarchical experience organization, retrieval and updates

Historical mechanism review: 2026-10-13. English editorial translation: 2026-10-22. This source supplements long-term memory and experience reuse on liYK's line. A general MAS interface does not establish lifecycle hooks or optimizer evolution control.

| Object | Verified source fact and boundary |
| --- | --- |
| Bottleneck | Long multi-agent interaction histories are difficult to reuse through final artifacts or flat similarity retrieval alone. |
| Representation | The paper separates interaction, query and insight graphs. The code uses Chroma, TaskLayer, InsightsManager and an insight-use cache. |
| Inputs | Current query, outcome-labeled MASMessage/StateChain, persistent memories, embedding and LLM interfaces. |
| Retrieval | Retrieve related task nodes and expand by hops; distinguish successful/failed trajectories, then rank/filter and return both types plus insights. Successful trajectories also undergo LLM relevance ranking. |
| Update | `add_memory` extracts trajectories, adds task nodes and labeled documents, updates insights at thresholds/round conditions, and merges every 20 entries. `backward` scores cached insights by success +1/failure -2 and clears that cache. |
| Cost | Chroma/embedding persistence, retrieval, LLM ranking, trajectory extraction and insight updates all incur costs. Actual local tokens, latency and gains remain unknown. |
| Paper/code difference | The graph projection/sparsification in paper §4.2 is not verified as operation-by-operation equivalent to every Python path. The selected insufficient-success/failure branch replaces its list; `if doc not in <the same iterated list>` then adds nothing. This does not preserve graph results and append deduplicated extras. |
| Project boundary | The original serves an execution MAS. Moving its organization to optimizer method knowledge and experimental experience is a hypothesis. Updates must use permitted train evidence; dev/test knowledge is frozen. Do not copy continuous learning on the test stream. |

Exact paper lines, code ranges, fixed links and claim support are in the [evidence map](claim-evidence-map.json). The earlier index used §5.4 Framework as the primary method entry; the 2026-10-13 review locates the main method at §3 and §4.1–4.3 / PDF pp.4–6. Section 5.4 is an experimental framework dimension.

The complete system, paper experiments and H0 integration have not been run; local gains remain unknown. The official README `tasks/run.py` example requires complete upstream source, data and models. The selected snapshot is not a complete installation, and system gains do not establish each memory operation's benefit. Selected score updates and LLM-authored insight edits are not neural parameter fitting; this is not a whole-dependency guarantee.
