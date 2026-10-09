# Archive-guided prompt template

Used before the optimization agent generates the next round of candidate
modifications. The fenced block below is the prompt body: `score_archive.py`
extracts it and fills in the three placeholders. Text outside the block is
documentation only and never reaches the model.

```
Current task:
{task}

High-scoring candidates from the archive (use as inspiration, not for verbatim reuse):
{successes}

Failed candidates from the archive (with error logs and repair suggestions; avoid repeating them):
{failures}

Based on the above, propose the next candidate modification:
1. State which bottleneck this modification tries to resolve;
2. State its relation to the archived successes and failures (borrowed, adapted, avoided, or unrelated);
3. Give an attributable modification (the smallest code/config/instruction change possible) and the expected verification signal;
4. Do not copy any archived failed design.
```
