# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `GraphToken/main.py`
- `GraphToken/run.sh`
- `finetunellm/main.py`
- `traingnn/main.py`

## Upstream command excerpts

```text
@inproceedings{wu2024graph,
  title={Can Graph Learning Improve Planning in LLM-based Agents?},
  author={Xixi Wu and Yifei Shen and Caihua Shan and Kaitao Song and Siwei Wang and Bohang Zhang and Jiarui Feng and Hong Cheng and Wei Chen and Yun Xiong and Dongsheng Li},
  booktitle={Proceedings of Neural Information Processing Systems},
  year={2024}
}
```

```text
pip install -r requirements.txt
```

```text
pip3 install "fschat[model_worker,webui]"
  pip3 install vllm
```

```text
python3 -m fastchat.serve.controller --host 127.0.0.1 

  # Specify the LLM to be deployed, take CodeLlama-13B as an example
  python3 -m fastchat.serve.vllm_worker --model-path codellama/CodeLlama-13b-Instruct-hf --host 127.0.0.1
  # Commands for other experimental LLMs
  # python3 -m fastchat.serve.vllm_worker --model-path lmsys/vicuna-13b-v1.5 --host 127.0.0.1
  # python3 -m fastchat.serve.vllm_worker --model-path codellama/CodeLlama-7b-Instruct-hf --host 127.0.0.1
  # python3 -m fastchat.serve.vllm_worker --model-path mistralai/Mistral-7B-Instruct-v0.2 --host 127.0.0.1
  # python3 -m fastchat.serve.vllm_worker --model-path baichuan-inc/Baichuan2-13B-Chat --host 127.0.0.1
  
  python3 -m fastchat.serve.openai_api_server --host 127.0.0.1 --port 8008
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
