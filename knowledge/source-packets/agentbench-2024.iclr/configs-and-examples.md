# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `src/server/tasks/dbbench/requirements.txt`
- `src/server/tasks/knowledgegraph/requirements.txt`
- `src/server/tasks/webshop/requirements.txt`
- `configs/assignments/test_avalon.yaml`
- `configs/agents/api_agents.yaml`
- `configs/agents/fs_agent.yaml`
- `configs/agents/openai-chat.yaml`
- `configs/agents/openai-text.yaml`
- `configs/start_task.yaml`
- `configs/start_task_lite.yaml`
- `scripts/validate_lite_configs.py`
- `src/configs.py`
- `configs/assignments/default.yaml`
- `configs/assignments/definition.yaml`
- `configs/assignments/lite.yaml`
- `configs/tasks/alfworld.yaml`
- `configs/tasks/avalon.yaml`
- `configs/tasks/card_game.yaml`
- `configs/tasks/dbbench.yaml`
- `configs/tasks/kg.yaml`
- `configs/tasks/ltp.yaml`
- `configs/tasks/mind2web.yaml`
- `configs/tasks/os.yaml`
- `configs/tasks/task_assembly.yaml`
- `configs/tasks/webshop.yaml`
- `src/typings/config.py`
- `src/server/tasks/alfworld/configs/base_config.yaml`

## Upstream command excerpts

```text
# dbbench
docker pull mysql:8

# os_interaction
docker build -t local-os/default -f ./data/os_interaction/res/dockerfiles/default data/os_interaction/res/dockerfiles
docker build -t local-os/packages -f ./data/os_interaction/res/dockerfiles/packages data/os_interaction/res/dockerfiles
docker build -t local-os/ubuntu -f ./data/os_interaction/res/dockerfiles/ubuntu data/os_interaction/res/dockerfiles
```

```text
docker compose -f extra/docker-compose.yml up
```

```text
cd AgentBench
conda create -n agent-bench python=3.9
conda activate agent-bench
pip install -r requirements.txt
```

```text
docker ps
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
