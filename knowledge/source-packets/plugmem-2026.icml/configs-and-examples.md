# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/openclaw-plugmem-plugin/src/config.ts` | Dependency, configuration, or usage evidence. |
| `official-code/plugmem-coding-core/src/config.ts` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_all_offline.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_all_online.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_gitlab_offline.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_gitlab_online.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_map_offline.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_map_online.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_reddit_offline.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_reddit_online.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_shopping_offline.yml` | Dependency, configuration, or usage evidence. |
| `official-code/src/eval/webarena/configs/AgentOccam_shopping_online.yml` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/plugmem-coding-core/src/eval/cli.ts` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/hotpotqa/eval_qa_no_structuring.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/hotpotqa/eval_vanilla_rag.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/longmemeval/eval_longmemeval_all.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/longmemeval/eval_longmemeval_sota.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/longmemeval/eval_longmemeval_without_reasoning.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/longmemeval/eval_longmemeval_without_retrieving.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/longmemeval/eval_longmemeval_without_retrieving.sh` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/longmemeval/eval_longmemeval_without_structuring.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/webarena/eval_agent_no_reasoning.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/webarena/eval_agent_no_retrieval.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/webarena/eval_agent_no_structure.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/src/eval/webarena/eval_agentoccam.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
