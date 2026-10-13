# Host Event Hooks and Structured Session Handoff

NORA invokes scripts on host lifecycle events, records tool interactions, and writes memory and handoff files at Stop. Its claims about unexpected termination and safety blocking extend beyond what static inspection of the public scripts can establish.

| Field | Mechanism |
| --- | --- |
| Target bottleneck | Long sessions end without a clear state or next action, and tool use lacks an auditable record. |
| Role | Host lifecycle wiring, tool logging, and structured handoff. |
| Inputs | Host tool events, tool inputs and results, existing output files, review state, and token-usage records. |
| Trigger | Configured `PreToolUse`, `PostToolUse`, and `Stop` events; actual triggering and event-input contracts depend on the host. |
| Required steps | Read the event input; log or inspect the tool call; aggregate state from outputs and review files; update `MEMORY.md`; generate `handoff.json`; load the handoff in the next session. |
| State changes | Logs are appended; memory and handoff files are updated with pipeline, review, experiment, paper, token, and recovery information. |
| Outputs | Reviewable logs, memory, and a structured handoff; completeness and atomic publication are not guaranteed. |
| Preconditions and limits | The original wiring depends on environment variables and `argv`; the pre-hook matches only Bash and exits with status 1, but effective host-level blocking is unverified. Stop writes several files sequentially and does not establish crash safety. The pinned upstream license is unknown, so reuse and redistribution permissions remain unknown. |

## Mechanism-to-evidence mapping

| ID | Claim | Paper and pinned code | Supported scope |
| --- | --- | --- | --- |
| NO1 | Configuration declares host events, and the pre-hook applies regular-expression checks and logs the input. | PDF p.12 §4.1; `settings.json:hooks`, `pre_tool_use.sh` | Supports the event intent and behavior of the public script; does not prove effective blocking by the host. |
| NO2 | Stop generates memory and a structured handoff from existing files. | PDF pp.12–13 §4.1, §4.3; `stop_hook.sh` | Supports explicit file-persistence behavior. Whether abnormal termination triggers it and whether recovery is accurate remain unknown; the multi-file write has no transaction contract. |
| NO3 | The post-hook logs results and heuristically updates experiment state from input and result text. | `post_tool_use.sh` | Public-script behavior only; it is not an independent scorer and does not guarantee accurate state extraction. |
| NO4 | The no-hooks comparison is a qualitative ablation from the same brief. | PDF pp.73–74 Appendix E | Qualitative paper evidence only; isolated hook gain, recovery rate, and local gain remain unknown. |

Exact source ranges appear in [the evidence map](claim-evidence-map.json), while host-protocol checks and permission boundaries appear in [the results notes](tests-and-reported-results.md). This packet preserves a lifecycle-orchestration and handoff case; it is not evidence of a validated safety gate or reliable recovery mechanism.

## Method relationships and project-use boundary

- [AgentScope](../agentscope-2508.16279/mechanism-and-boundaries.md): NO1 uses host command events, whereas AS1 wraps in-process functions. Both require explicit input and error contracts; similar event names do not establish interchangeability.
- [AgentRewind](../agentrewind-2608.14380/mechanism-and-boundaries.md): NO2 records progress in handoff files, whereas AR1–AR2 restore context and workspace state. A handoff file cannot replace a checkpoint or prove that a process can be resumed or external side effects undone.

Project derivatives are limited to the editable Harness boundary. Upstream models, permissions, notifications, and host configuration are not copied automatically. Wiring, licensing, and transfer gain require separate verification.
