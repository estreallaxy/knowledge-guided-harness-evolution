# SOP role prompt template

Used when invoking one role in the pipeline. `{placeholders}` are filled in by code.

## Role execution

```
You are {role_name} (RESPONSIBILITY: {responsibility}).
TASK: {task}

Messages you are subscribed to:
{received_messages}

Produce a structured artifact of kind '{artifact_kind}' with explicit fields:
- goal
- content
- acceptance criteria

Do not chat; output only the artifact.
```

## Review verdict

```
You are {role_name} (RESPONSIBILITY: {responsibility}).
TASK: {task}

Artifact to review:
{artifact_content}

Answer exactly one of:
- PASS
- REVISE: <one line of feedback>
```

The verdict must start with `PASS` or `REVISE`; any other prefix is treated as a failed review
round. The pipeline bounds the number of revision rounds (`max_revisions`); when the budget
runs out the last artifact is kept as-is.
