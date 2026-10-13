# Configs and examples

# Official configuration

|Settings|Configure Directory|Main elements|
| --- | --- | --- |
| Default Configuration |`official-code/config/default.yaml` | `WINDOW: 100`(:88),`OVERLAP: 2`,`CURRENT_LINE/CURRENT_FILE`(:87-91);`command_files` = `official-code/config/commands/`split string.py /submit.sh (: 92-97);`parse_function: thought_action`(:111-112);`history_processor: last_n_observations, n: 5`(:113-115);`next_step_no_output_template`(:72-76). |
|Command Set| `official-code/config/commands/` |It contains: defaults.sh (open)/goto/scroll/create),search.sh(search_dir/search_file/find_file), edit lining.sh (edit + flake8), cursors *.sh (rubber variant), submit.sh,  split string.py.|
|Absorption Configuration (available)| `official-code/config/swe_agent_ablations/`(8 yaml)| `default|xml` × `window100|cursors_window100` × `full/last_5_history`;discrepancies`WINDOW: 100 vs 200`This post is part of our special coverage Global Voices 2011. Other`config/default_xml.yaml`(XML output variant).|

The configuration can only be explained with the corresponding paper version, code review, task data and the model environment. The results of the exercise in the dissertation cannot be reproduced independently by a single YAML (as well as by contrast with the snapshot default: the best window of the dissertation is 100/0.0/Last-5, see Table 5 p. 25).

# The official process entrance

Batch assessment portal (order form exists, but see the conditions below:

```bash
python -m sweagent.run.run run-batch --config <yaml>
```

- Suborder.`run / run-batch / run-replay`See`official-code/sweagent/run/run.py:13-46`;CLI by`--config`Multiple supersing (`official-code/sweagent/run/common.py:23-33`).
- Product`trajectories/<user>/<config>__<model>__<source>`(`official-code/sweagent/run/run_batch.py:33-43`).
- The data set example is loaded by`SWEBenchInstances`from HF`princeton-nlp/SWE-Bench[_Lite|_Verified]`(`official-code/sweagent/run/batch_instances.py:203-243`).

Operating premise:

- Docker, mirror.`sweagent/swe-agent:latest`(`official-code/sweagent/environment/config/deployment.py:33-47`) and SWE-bench Official Mirror`swebench/sweb.eval.x86_64.*:v1`(`official-code/sweagent/run/batch_instances.py:129`).
- `datasets`Package (mounting HF data sets); automatic inside containers`pip install flake8`(`official-code/sweagent/tools/tools.py:78`).
- It doesn't exist.`pyproject.toml`/`requirements`,`frontend/`,`api/`,`evaluation`; which does not contain papers`trajectories/demonstrations/*.traj`(`official-code/config/default.yaml:85`) , Configure`demonstrations:`path needs to be replaced.
-`README.upstream.md`does not contain CLI running commands, only links to external document stations.

# Local Save Range

`official-code/`Save`sweagent/`Packs (agent, environment, tools, utils, run entrance),`config/`(default, commands, swe agents, ctf variants, default xml),`README.upstream.md`with`LICENSE`I don't know. SWE-bench Assessment`trajectories/`,`tests/`,`frontend/`,`api/`is not in this directory.

`README.upstream.md`"resolves 12.47% of issues of the full test set and 23% of issues of SWE-bench land"; of which Lite 23% is later than the dissertation (18.00 per cent) and is of subsequent calibre.
