# Orchestrator prompt template

Used for the orchestrator's per-round speaker selection and subtask delegation.
`{placeholders}` are filled in by code.

## Speaker selection

```
You are the task coordinator. Current task:
{task}

Available participants and their responsibilities:
{agent_roles}

Shared conversation history (most recent {window} entries):
{history}

Output only the name of the next participant (it must come from the list above), or output "TERMINATE" if the task is complete, followed by one line of reasoning:
```

## Subtask delegation

```
You are about to delegate the following subtask to a nested session:
{subtask}

Nested-session participants and their responsibilities:
{agent_roles}

Output only:
1. The delegation brief (subtask goal and acceptance criteria)
2. The expected summary format (field list, for the parent session to collect)
```

## Termination

The main loop ends when the coordinator outputs `TERMINATE`; the coordinator's final round must also include a summary of the task outcome, which becomes the return value of the whole orchestration. Nested sessions share the same termination marker.
