# AgentFold: Long-Horizon Web Agents with Proactive Context Management

|content|Location|
| --- | --- |
|Source metadata| [source-packet.json](source-packet.json) |
|Paper v1|[paper/paper-v1.pdf](paper/paper-v1.pdf) · [Text](paper/paper-v1.txt)|
|Official core code|[`official-code/`](official-code/) (`AgentFold/infer.py`+ root`inference/`tool)|
|Paper and code positioning| [exact-source-anchors.md](exact-source-anchors.md) |
|Configure and run the portal| [configs-and-examples.md](configs-and-examples.md) |
|Test and paper results| [tests-and-reported-results.md](tests-and-reported-results.md) |

## What does this paper solve?

There are trade-offs in context management for long-range web agents: ReAct-style agents accumulate raw history leading to context saturation;
Fixed summarizing the entire history at each step irreversibly loses key details. AgentFold lets the model output a
"Folding command" and a tool call**, the command can work at two scales (fine-grained merging vs. compressing the entire paragraph investigation into a conclusion),
And replace the original history with the structure of "multi-scale state summary + latest interaction fidelity", and then use SFT to train it.

Relationship with our harness: This is the other pole of the "context compression" direction - ACON compresses the existing context,
AgentFold allows the agent to actively manage and fold state, and the two can be combined or replaced with each other.

## Snapshot status

`official-code/`has been repositoryd and fixed revision`f72f75d8c3eb842f2bbbab096a12206ff66e270f`
(Acquired on 2026-10-13). **Explicitly missing**:

- The training data, SFT training script and`AgentFold-30B-A3B`weight are **not in the repository**, and the repository only provides inference side code.
- Leave`MODEL_PATH`blank in`serve.sh`, you need to prepare your own weight and use vLLM to start the service;`infer.py`is connected to the local machine by default
`localhost:8000-8005`, and use`gpt-oss-120b`to create an additional 8006 port.
- The unit test directory is not provided by the upstream, and the test entrance is recorded as unknown.
- Snapshot layout: upstream`WebAgent/AgentFold/`is flattened to the top level`AgentFold/`; repository level`FAQ.md`,`.env.example`
(placeholder only),`.gitignore`and`Tech_Report.pdf`are included. Upstream`README.md`points to`./WebAgent/`,
The references to the`./evaluation/`and`assets/`images were changed to plain text due to differences in snapshot layout.

## Relationship to local experiments

This package only saves papers and official codes, and does not include local running results. The method implementation (Method) has not yet been allocated, and no local demo will be done at this stage.
The results of the paper are the performance after **30B level model training**, which cannot be directly equivalent to the harness income of fixed`deepseek-v4-flash`.
