# Align context and workspace checkpoint recovery

AgentRewind aligns the context and the controlled workspace at the model decision boundary, restores the old prefix when rolling back, retains the experience of the last attempt, and generates a new suffix. Its controlled environment recovery boundary is the workspace file tree and does not represent the recovery of all processes or external services.

|Field|Mechanism description|
| --- | --- |
|target bottleneck|Early errors contaminate both the context and the workspace, and subsequent append actions cannot be fully undone.|
|function module|Execution logging, context recovery, and workspace file state recovery|
|enter|Model/tool origin records, workspace checkpoints, target record IDs, fallback reasons, and experience summaries|
|Trigger condition|Normal execution is recorded at the model decision boundary; the agent requests a rollback when it determines that the current trajectory is difficult to advance.|
|Necessary steps|Align records; present candidate checkpoints; select targets and summarize failure experience; restore old context and file state; inject experience; generate new suffixes from targets|
|status change|The current context and file tree return to the target state, the rollback experience is accumulated, and the subsequent trajectory forms a new branch.|
|expected output|Continued execution context, restored workspace, new branch record and rollback experience|
| Prerequisites and limitations | Network, service, and runtime state beyond the file tree cannot be undone; reliable logging and workspace management are required. The paper's evaluation provides acceptance feedback and does not impose preset total-token, step, or wall-clock limits, so its results cannot be transferred directly to this project's fixed-budget setting. |

## Correspondence between mechanism and evidence

|logo|advocate|Papers and Fixed Code|Support scope|
| --- | --- | --- | --- |
| AR1 |Build fallback context from old model inputs and associate accumulated experience with new branches| PDF pp.2–3 Framework / Rewind Module; `replay/backtrack.py:prepare_backtrack_replay` |Paper recovery link and public context preparation and experience recording interface; this function itself does not prove that environment recovery has been executed|
| AR2 |Recover modified, deleted and newly added files in the workspace file tree| PDF p.4 External Environment Recovery Boundary; `replay/git_workspace.py:restore_commit`, `commit_current` |Fixed Git workspace save and restore implementation; does not certify process, remote API, or database restore|
| AR3 |Recovery retains prefix from execution record, external side effects cannot be undone| PDF pp.3–4 Rewind Module / Recovery Boundary |The paper explicitly restores boundaries; it does not guarantee that all external calls are idempotent or non-duplicate.|

See [Evidence Map](claim-evidence-map.json) for the precise location and support range, and see [Result Boundary](tests-and-reported-results.md) for evaluation differences. The public code is a fixed alpha selected fragment. The private evaluation system of the original paper is not included in this package; the original experimental commit correspondence is unknown.

## Method relationships and project usage boundaries

- [StateFork](../statefork-2609.38648/mechanism-and-boundaries.md): AR2 file-tree recovery differs from SF1/SF3 environment recovery. Tasks that must recover processes, PTYs, or local services may require a broader backend. File recovery alone must not be described as physical full-state recovery; replacing the backend remains a hypothesis to test.
- [ReasoningBank](../reasoningbank-2509.25140/mechanism-and-boundaries.md): AR1's intra-task fallback summary and RB2's cross-task experience extraction can be associated; only transfer from train to long-term experience is allowed, and dev/test's fallback feedback must not be used to update optimization knowledge. This combination is not implemented.

The token, time and expense ledgers of this project must be retained cumulatively, and consumption will not be cleared after status rollback. The existing local file copy example does not implement a full recorder, automatic fallback selection, or model suffix generation, nor does it yet have access to H0.
