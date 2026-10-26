# AgentDojo: composable pipeline interfaces and tool-output extension points

Historical mechanism review: 2026-10-13. English editorial translation: 2026-10-22. This review covers extension interfaces and state threading relevant to liYK. AgentDojo studies prompt-injection evaluation; its safety benchmark results are not project transfer gains.

| Object | Mechanism and supported scope |
| --- | --- |
| Input/output contract | `BasePipelineElement.query` accepts query, FunctionsRuntime, Env, messages and extra_args and returns the updated five-tuple. Elements can provide model, tool, detection or message processing. |
| Composition | `AgentPipeline.query` calls elements in order and passes each updated tuple to the next. `ToolsExecutionLoop` repeats configured elements while the last assistant message contains tool calls. |
| Concrete extensions | `ToolsExecutor` accepts `tool_output_formatter` and writes formatted output as a tool message. A detector can be placed after tool execution and before the next model call. |
| State | Env/runtime/messages represent current execution state passed between elements. This is not an environment snapshot, physical rollback or persistent session recovery. |
| Stopping and exceptions | The pinned tool loop defaults to `max_iters=15` and stops when there are no tool calls. Element exceptions have no universal finally/post guarantee; this cannot replace guaranteed cleanup. Detector behavior and false-positive costs depend on the chosen detector. |
| Paper/code versions | PDF p.5 §3.2 and p.16 Figures 11–12 describe modular interfaces. The pinned code revision is from 2026; exact identity with the 2024 paper experiment code is unknown. Paper illustration types and current runtime types retain their respective contracts. |
| Local limits | The official pipeline, detector/models, safety experiments and H0 integration have not been run. The selected snapshot is not guaranteed installable; provider modules and system-prompt resources imported by the full AgentPipeline require the complete fixed upstream. |

The three claims and precise anchors are in the [evidence map](claim-evidence-map.json). AgentDojo supplements AgentScope with inspectable extension interfaces. NORA remains conditional because real host wiring is unverified.

Adding logging, validation or experience extraction as independent optimizer pipeline elements is a transfer hypothesis. Ordering, side effects, exception contracts, token/time costs and local gains require separate verification. No derived Method is implemented before assignment. Selected composition/formatting interfaces do not require fitting model parameters; a trainable detector is excluded from that selection.
