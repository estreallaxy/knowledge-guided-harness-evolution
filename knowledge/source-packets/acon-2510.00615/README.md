# ACON: Optimizing Context Compression for Long-horizon LLM Agents

|content|Location|
| --- | --- |
|Source metadata| [source-packet.json](source-packet.json) |
|Paper v3|[paper/paper-v3.pdf](paper/paper-v3.pdf) · [Text](paper/paper-v3.txt)|
|Official core code|[`official-code/`](official-code/) (`src/productive_agents/ctxopt/`and`experiments/`)|
|Paper and code positioning| [exact-source-anchors.md](exact-source-anchors.md) |
|Configure and run the portal| [configs-and-examples.md](configs-and-examples.md) |
|Test and paper results| [tests-and-reported-results.md](tests-and-reported-results.md) |

## What does this paper solve?

The observations and history of long-range agents will grow unbounded, resulting in two bottlenecks: reasoning memory cost and "reasoning degradation caused by irrelevant information."
ACON unifies **observation compression** and **historical compression** into one framework, and iteratively optimizes compression guidelines in the natural language space
(Based on the agent's failure analysis), the optimized compressor is distilled into a small model without updating the parameters of the tested model throughout the process.

Value to our harness: It is a second source of "context compression" direction, complementary to AgentFold's folding mechanism
(ACON compression has context, AgentFold actively manages state summary).

## Snapshot status

`official-code/`has been repositoryd and fixed revision`d63f9ae18959dc7215ff62899c94c5e8c56847ae`
(Acquired on 2026-10-13, see`snapshot_scope`of`source-packet.json`).

- Incorporates the complete evaluation pipeline and data of`assets/`and`experiments/`: OfficeBench task set (approximately 22 MB),
8-objective QA (`smolagents/data/nq_multi_8`) with AppWorld configuration. They belong to the paper's own evaluation pipeline and
Task instances are retained according to the current access control; only the running cache and model credentials are not included.
- The repository comes with`configs/private_config_dummy.yaml`and only has the placeholder key`openai_key: <YOUR_OPENAI_KEY_HERE>`;
Before running, you need to build`configs/private_config.yaml`yourself and only inject the credentials through local files, and the credentials will not be stored in the database.
- The upstream **does not provide a unit test directory**, so the "test entry" of`tests-and-reported-results.md`is recorded as unknown.
- The upstream`official-code/`remains as it is, only one incorrectly written relative path in`experiments/smolagents/README.md`is corrected (`experiments/appworld/README.md`→`../appworld/README.md`); the relative links and pictures of`experiments/officebench/`can be parsed.

## Relationship to local experiments

This package only saves papers and official codes, and does not include local running results. The method implementation (Method) has not yet been allocated, and no local demo will be done at this stage.
Nor does it claim that the paper values have been reproduced locally.
