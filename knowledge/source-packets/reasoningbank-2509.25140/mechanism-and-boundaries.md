# Extracting, Retrieving, and Appending Reasoning Experience from Success and Failure

ReasoningBank extracts reusable experience from complete successful and failed trajectories, retrieves relevant memory before a new task, and appends newly extracted items afterward. Retrieval, judging, extraction, and consolidation are distinct operations; gains of the complete system cannot be assigned to a single memory item.

| Field | Mechanism |
| --- | --- |
| Target bottleneck | Historical successes and failures are discarded across repeated tasks, so similar reasoning errors recur. |
| Role | Experience extraction from the permitted train split and pre-execution memory retrieval. |
| Inputs | Current task query, existing experience and embedding cache, complete trajectory, success/failure judgment, and judge, extractor, and embedding-model interfaces. |
| Trigger | Retrieve before a new task; extract and append after the task ends. In this project, only training runs may update memory, which is frozen before development and test evaluation. |
| Required steps | Compute similarity between the query and cached experience; select relevant experiences and memory items; judge success or failure; use outcome-specific instructions to extract reusable experience from the trajectory; append new memory items; retrieve them for later tasks. |
| State changes | The experience pool and query-embedding cache grow. The pinned mechanism does not provide validated higher-level conflict resolution, forgetting, compression, or retrospective verification. |
| Outputs | Relevant experiences and memory items, an expanded experience pool, and separately accounted extraction cost. |
| Preconditions and limits | The paper continues learning on a test-task stream, whereas this project freezes state for development and test evaluation. The pinned code retrieves experiences before selecting their items; a simpler item-level retrieval would be an adaptation. Actual judge and embedding behavior and local gains remain unverified. |

## Mechanism-to-evidence mapping

| Claim | Paper location | Pinned code | Supported scope |
| --- | --- | --- | --- |
| RB1: retrieve top-k experiences by query and use their memories as execution guidance | PDF p.5 §3.2 / Fig.2 | [memory_management.py:138](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L138-L170) | Supports the paper mechanism and pinned retrieval entry point; does not establish a gain with local models. |
| RB2: use different extraction instructions for success and failure to generate experience entries | PDF p.5 §3.2, memory extraction | [induce_memory.py:123](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L123-L166) | Supports the pinned judgment branch and model calls; judge validity remains unknown. |
| RB3: consolidation is simple addition, implemented as JSONL append rather than advanced maintenance | PDF p.5 §3.2, memory consolidation | [induce_memory.py:176](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L176-L186) | Supports append behavior in the paper and code; editing and conflict resolution are absent. |
| RB4: retrieval requires a query embedding and writes to an embedding cache | PDF p.22 Appendix A.2, memory retrieval | [memory_management.py:172](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L172-L215) | Supports the original retrieval model and pinned cache behavior; adding a cache entry is not the same as adding a memory item. |
| RB5: 40.5→48.8 is a WebArena/Gemini system-level result | PDF p.7 Table 1 | The corresponding original experiment-code location is unknown. | Paper result only; the pinned code's correspondence to the experiment commit is unknown, and the result cannot be attributed to one experience item. |

Complete PDF line ranges, code ranges, and pinned links appear in [the evidence map](claim-evidence-map.json).

## Method relationships and project-use boundary

- [ExpeL](../expel-2308.10144/mechanism-and-boundaries.md): complementary or substitutable experience representations. ReasoningBank stores reasoning experience from successes and failures, whereas ExpeL maintains voted rules. They may share training sources, but duplicate advice and retrieval overhead must be controlled. Combined gains remain untested.

Local integration, combined gains, and a complete upstream reproduction remain unverified.
