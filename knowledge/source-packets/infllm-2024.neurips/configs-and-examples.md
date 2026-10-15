# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.py`
- `config/mistral-stream-llm.yaml`
- `config/vicuna-stream-llm.yaml`
- `benchmark/config/dataset2prompt.json`
- `config/llama-3-inf-llm.yaml`
- `config/minicpm-inf-llm.yaml`
- `config/mistral-inf-llm-12k.yaml`
- `config/mistral-inf-llm-fattn.yaml`
- `config/mistral-inf-llm.yaml`
- `config/mistral-infinite-lm.yaml`
- `config/mistral-ntk.yaml`
- `config/mistral-origin.yaml`
- `config/mistral-pi.yaml`
- `config/qwen-inf-llm.yaml`
- `config/vicuna-inf-llm.yaml`
- `config/vicuna-infinite-lm.yaml`
- `config/vicuna-origin.yaml`
- `benchmark/config/dataset2maxlen.json`

## Upstream command excerpts

```text
torch>=1.13.1
transformers>=4.37.2
fschat>=0.2.35
datasets>=2.17.0
omegaconf
flash-attn

rouge==1.0.1
fuzzywuzzy==0.18.0
jieba==0.42.1
```

```text
### Evaluation

**Data Preparation**
We adopt InfiniteBench and LongBench for model evaluation. You can download the datasets by running the following command.
```

```text
**Response Generation**
You can evaluate InfLLM by running the following command. Notably, the provided code is used to run evaluate with only one GPU, and you can accelerate the experiments with multiple GPUs.
```

```text
### Run a Chatbot with InfLLM

We integrated fastchat's CLI chat.
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
