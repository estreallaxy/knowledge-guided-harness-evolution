# Configs and examples

# Official configuration

|Settings|Configure Directory|Main elements|
| --- | --- | --- |
|Sandboxes and Run-time| `official-code/openhands/core/config/sandbox_config.py` |Base Mirror Default`nikolaik/python-nodejs:python3.12-nodejs22`(:49-51);`runtime_container_image`Default None (:52);`:24/33`Note`runtime_extra_deps`For assessment, assessment,`browsergym_eval_env`Point`evaluation/miniwob`,`evaluation/webarena`. |
|LLM Access| `official-code/openhands/core/config/llm_config.py` |Default`model='claude-3-7-sonnet-20250219'`,`api_key=None`(: 49-50), fill in at running time.|
|Assess parameters| `official-code/openhands/core/config/utils.py:494-499` |`--eval`-related parameters; default output directory`evaluation/evaluation_outputs/outputs`.|

The configuration can only be explained with the corresponding paper version, code review, task data and the model environment. The results of the exercise in the paper cannot be reproduced independently by a single configuration.

# The official process entrance

The official README (`official-code/README.upstream.md`in this package) specifies the mode of operation of the container (: 54-66):

```bash
docker pull docker.all-hands.dev/all-hands-ai/runtime:0.33-nikolaik

docker run -it --rm --pull=always \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.33-nikolaik \
  -e LOG_ALL_EVENTS=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands-state:/.openhands-state \
  -p 3000:3000 \
  --name openhands-app \
  docker.all-hands.dev/all-hands-ai/openhands:0.33
```

Operating premise:

- Host Docker and mounted`docker.sock`(README:60); mirror builder`official-code/openhands/runtime/builder/docker.py:16`, Docker Runtime`official-code/openhands/runtime/impl/docker/docker_runtime.py:57`.
- Model API key: Start first with LLM program and fill in (README: 70-72, recommended`anthropic/claude-3-5-sonnet-20241022`).
- Headless entrance:`official-code/openhands/core/main.py:48`(run_controller),`:56`(headless mode=True, default).
- It doesn't exist.`pyproject.toml`/`requirements`,`storage/`,`llm/`,`server/`Other Modules`official-code/openhands/events/stream.py:15`Yes.`from openhands.storage import FileStore`Directed outside of the snapshot) the complete operation requires an upstream repository.

# Local Save Range

`official-code/`Save`openhands/`Agenthub (codeact agent, Browning agent, dummy agent, readonly agent, visualbrowsing agent and its prompts/tools), controller, core/config, events, memory, runtime and`README.upstream.md`,`LICENSE`.

Comment: **`evaluation/`directories do not exist in snapshots** (top-level directories are openhands/, README.upstream.md, LICENSE); scripts used for the evaluation of the papers (including SWE-bench, WebArena, MiniWoB++, GAIA integration) are to be obtained separately from OpenHands main repository.
