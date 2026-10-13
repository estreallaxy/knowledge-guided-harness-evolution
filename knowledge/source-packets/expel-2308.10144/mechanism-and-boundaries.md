# Rule Maintenance from Training Experience and Retrieval of Successful Examples

ExpeL turns successful and failed training trajectories into editable rules and retrieves successful trajectories as examples for new tasks. Rule extraction, example retrieval, and Reflexion during training are separate components; the gain of the complete system cannot be attributed solely to rule maintenance.

| Field | Mechanism |
| --- | --- |
| Target bottleneck | Reusable action experience is discarded across tasks, causing similar mistakes to recur. |
| Role | Offline experience collection, rule extraction, and pre-execution context construction. |
| Inputs | Successful and failed training trajectories, existing rules and importance counts, a new task, a pool of successful examples, and an embedding interface. |
| Trigger | Rules are extracted after training experience is collected; examples are retrieved and rules injected before a new task is executed. |
| Required steps | Collect training trajectories; compare success/failure pairs from the same task and successes across tasks; generate rule operations; update counts and remove invalid rules; retrieve successful examples; add rules and examples to the task context. |
| State changes | The experience pool and rule set grow or are revised; rule importance counts increase or decrease; extracted knowledge becomes available at execution time. |
| Outputs | Counted rules, relevant successful examples, and augmented task instructions. |
| Preconditions and limits | The original training procedure includes Reflexion retries, and its rule-extraction model differs from the execution model. Training-sample quality, rule conflicts, context length, and offline cost affect use. Local model integration and transfer gains remain unverified. |

## Mechanism-to-evidence mapping

| ID | Claim | Paper and pinned code | Supported scope |
| --- | --- | --- | --- |
| EX1 | Rules are extracted from success/failure pairs and successful sets, then maintained through edit and vote operations. | PDF p.4 §4.2 and p.6 Algorithm 2; `agent/expel.py:create_rules`, `parse_rules`, `update_rules` | Supports rule maintenance in the paper and implementation. The paper's UPVOTE/DOWNVOTE differs from the code's AGREE/REMOVE; operation order, the −3 full-table behavior, and text-matching differences are preserved. |
| EX2 | Successful trajectories are retrieved by task similarity, and rules and examples are added to the execution context. | PDF pp.4–5 §4.2–4.3 and p.6 Algorithm 3; `agent/expel.py:setup_vectorstore`, `update_dynamic_prompt_components`, `insert_before_task_prompt` | Supports experience retrieval and context construction; does not establish a local performance gain. |
| EX3 | Training first collects success and failure experience through reflection and retry, so this cost cannot be ignored. | PDF p.4 §4.1 and p.6 Algorithm 1; `agent/expel.py:run` | The pinned training branch calls `ReflectAgent.run`. Its parent class is outside the selected source snapshot, so complete training behavior and actual cost remain unknown. |

Paper pages, text-line ranges, code ranges, and pinned links are recorded in [the evidence map](claim-evidence-map.json). Reported values and historical compatibility differences are recorded in [the results boundary](tests-and-reported-results.md); source materials and versions are recorded in [the source anchors](exact-source-anchors.md).

## Method relationships and project-use boundary

- [ReasoningBank](../reasoningbank-2509.25140/mechanism-and-boundaries.md): both reuse experience. ExpeL stores editable rules and successful examples, whereas ReasoningBank stores reasoning experience from successes and failures. EX1–EX2 and RB1–RB3 may substitute for or complement one another, but duplicate advice and retrieval cost must be handled. Any combined gain remains an untested hypothesis.
- [AgentRewind](../agentrewind-2608.14380/mechanism-and-boundaries.md): EX1's cross-task rule maintenance may complement AR1's within-task recovery memory. Their lifecycles differ and they should not be merged into one undifferentiated experience pool. This combination has not been implemented or measured.

For project transfer, knowledge may be extracted and updated only from permitted training experience; development and test runs use frozen knowledge. This is a project boundary, not a completed integration. Existing local synthetic tests do not constitute a full upstream reproduction or H0 transfer validation.
