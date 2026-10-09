# Workflow search prompt template

Used when the mutation operators are model calls (AFlow generates and modifies workflow
code through prompts). `{placeholders}` are filled in by code. The demo in
`tree_search.py` uses deterministic numeric operators instead; these templates describe
the model-backed variant.

## Seed generation (before the search starts)

```
You are a workflow designer. Build a workflow node that {task_description}.

Return Python code defining the node, using only the provided operators and
node templates. Output the code block only.
```

## Candidate modification (one expansion step)

```
Here is the current workflow node and its evaluation result:

Workflow:
{workflow_code}

Metric value: {score}

Improve the workflow to raise this metric. Return the full revised node code.
Keep the same interface; only change the internal logic.
```

Notes:

- The evaluator output (`{score}`) is the only search signal — keep the metric
  deterministic and cheap enough for hundreds of expansions.
- Failed executions should be reported back as a distinct low score plus the error text,
  so the modification prompt can fix rather than repeat the failure.
