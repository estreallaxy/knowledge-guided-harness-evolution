# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `agentlego/pyproject.toml`
- `agentlego/requirements.txt`
- `agentlego/setup.cfg`
- `agentlego/setup.py`
- `opencompass/requirements.txt`
- `opencompass/setup.py`
- `agentlego/examples/README.md`
- `agentlego/examples/visual_chatgpt/requirements.txt`
- `opencompass/configs/models/hf_internlm/README.md`
- `opencompass/configs/models/qwen/README.md`
- `agent_app_eval/run_agents.py`
- `opencompass/configs/eval_chat_agent.py`
- `opencompass/configs/eval_chat_agent_baseline.py`
- `opencompass/configs/eval_codeagent.py`
- `opencompass/configs/eval_llm_compression.py`
- `opencompass/configs/eval_mmlu_with_zero_retriever_overwritten.py`
- `opencompass/configs/eval_multi_prompt_demo.py`
- `agentlego/agentlego/testing/setup_tool.py`
- `agentlego/.pre-commit-config.yaml`
- `agent_app_eval/examples/build_eval_pack_from_agent_app_result.py`
- `agent_app_eval/examples/build_gpt52_pack_from_manus_results.py`
- `agent_app_eval/examples/build_gpt52_pack_from_openclaw_results.py`
- `agentlego/examples/streamlit_demo.py`
- `opencompass/configs/eval_TheoremQA.py`
- `opencompass/configs/eval_alaya.py`
- `opencompass/configs/eval_attack.py`
- `opencompass/configs/eval_bluelm_32k_lveval.py`
- `opencompass/configs/eval_charm.py`
- `opencompass/configs/eval_chat_cibench.py`
- `opencompass/configs/eval_chat_cibench_api.py`

## Upstream command excerpts

```text
git clone https://github.com/open-compass/GTA.git
cd GTA
```

```text
mkdir ./opencompass/data
```

```text
GTA/
├── agentlego
├── opencompass
│   ├── data
│   │   ├── gta_dataset_v2
│   ├── ...
├── ...
```

```text
pip install -U huggingface_hub
# huggingface-cli download --resume-download hugging/face/repo/name --local-dir your/local/path --local-dir-use-symlinks False
huggingface-cli download --resume-download Qwen/Qwen1.5-7B-Chat --local-dir ~/models/qwen1.5-7b-chat --local-dir-use-symlinks False
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
