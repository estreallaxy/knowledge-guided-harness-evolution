# Inducing Programmatic Skills for Agentic Tasks

|content|Location|
| --- | --- |
|Source metadata| [source-packet.json](source-packet.json) |
|Paper v2|[paper/paper-v2.pdf](paper/paper-v2.pdf) · [Text](paper/paper-v2.txt)|
|Official core code|[`official-code/`](official-code/) (`asi/induce/`and`asi/autoeval/`)|
|Paper and code positioning| [exact-source-anchors.md](exact-source-anchors.md) |
|Configure and run the portal| [configs-and-examples.md](configs-and-examples.md) |
|Test and paper results| [tests-and-reported-results.md](tests-and-reported-results.md) |

## Snapshot status

`official-code/`has been repositoryd and fixed revision`377abe0623a37eaf7f03bdd26cb97bb5331acf47`
(Acquired on 2026-10-13). See`snapshot_scope`of`source-packet.json`for scope and exclusions:

- Included:`asi/`(`induce/`'s skill summary,`autoeval/`'s trajectory evaluation,`actions/`'s site action set,
`agent.py`,`custom_action_set.py`,`config_files/generate_test_data.py`, etc.) and`browsergym/`
Mechanism source code (agent, loop and benchmark reading logic of`core/`and`experiments/`).
- Inclusion:`browsergym/experiments/.../benchmark/metadata/*.csv`(WebArena/WebLINX/WorkArena/
task/split metadata for VisualWebArena / AssistantBench / MiniWoB). Reserved code is loaded by name at runtime
These files contain only metadata such as `task_name`, split, and difficulty; they contain no answers.
- Not included:`asi/config_files/test.json`and`test.raw.json`- embedded`reference_answers`reference answer
and scoring rules, it is a material that "directly exposes the hidden answers of the benchmark" and can be used by the databased
`config_files/generate_test_data.py`regenerated.
- The actual running environment and site data, data sets, running cache and model credentials of WebArena/BrowserGym are not included.
- License: The repository root LICENSE is **CC BY-SA 4.0** (non-common software license), please pay attention when migrating or redistributing.
-`vendor-official-code.sh`is retained as a snapshot source record; when reconstruction is needed, it can be executed from a terminal with network access.
- The unit test directory is not provided by the upstream, and the test entrance is recorded as unknown.

The local PDF is public arXiv v2 (COLM 2025 version); the page number anchors in the text are based on this PDF.
Check with`--- PDF page N ---`tag of`paper/paper-v2.txt`.

## Relationship to local experiments

This package only saves papers and official codes, and does not include local running results. The method implementation (Method) has not yet been allocated, and no local demo will be done at this stage.
