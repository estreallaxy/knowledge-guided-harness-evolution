# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `configs.py`

## Upstream command excerpts

```text
conda create --name amla python=3.11
pip install -r requirements.txt
```

```text
HF_TOKEN="Your HuggingFace Token" CUDA_VISIBLE_DEVICES="0,1,2,3" python -m vllm.entrypoints.openai.api_server --model mistralai/Mixtral-8x7B-Instruct-v0.1 --enable-lora --lora-modules prompt-llama=./adapter/adapter-mixtral/ --tensor-parallel-size 4
```

```text
AVAILABLE_LLMs = {
    "prompt-llm": {
        "api_key": "empty",
        "model": "prompt-llama",
        "base_url": "http://localhost:8000/v1",
    },
    "gpt-4": {"api_key": "YOUR OPENAI KEY", "model": "gpt-4o"},
    "gpt-3.5": {"api_key": "YOUR OPENAI KEY", "model": "gpt-3.5-turbo"},
}
```

```text
from agent_manager import AgentManager

data_path = "agent_workspace/datasets/banana_quality.csv" # assuming the data is uploaded via web interface / API
user_prompt = "Build a model to classify banana quality as good or bad based on their numerical information about bananas of different quality (size, weight, sweetness, softness, harvest time, ripeness, and acidity). We have uploaded the entire dataset for you here in the banana_quality.csv file."
manager = AgentManager(llm='gpt-4', interactive=False, data_path=data_path)

manager.initiate_chat(user_prompt)
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
