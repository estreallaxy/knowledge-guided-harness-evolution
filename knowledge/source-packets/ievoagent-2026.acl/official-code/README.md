# IEvoAgent: Evolving Conversational Agent based on User Implicit Feedback

[![ACL 2026](https://img.shields.io/badge/ACL-2026%20Oral%20Presentation-dodgerblue)](https://aclanthology.org/2026.acl-long.441/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Static Badge](https://img.shields.io/badge/LLM_Agent-feedback_learning-blue)

## Abstract

Current conversational agents often follow static learning paradigms and miss the implicit, evolving feedback embedded in users’ follow-up behaviors. We propose IEvoAgent, an evolving conversational agent framework that leverages the structured dependency between agent responses and user reactions. We construct an annotated dataset from LMSYS-Chat-1M and WildChat and find consistent response-conditioned feedback patterns. Based on this finding, IEvoAgent uses a conditional feedback distribution matrix to estimate expected feedback rewards, combining offline KTO alignment with an inference-time prompt-evolution mechanism driven by a dynamic matrix. Experiments on MT-Bench-101, WildBench, and FB-Bench show improvements over open-source baselines, indicating that mining implicit feedback supports better multi-turn alignment under evolving user preferences. Our code and dataset are available at https://github.com/Hualeez/IEvoAgent.

![overview](./assets/overview.png)


## How to Use This Project

### 0. Install Required Libraries

```bash
# Base requirements
pip install -r requirements_vllm_stable.txt

# Or using conda (for OpenCompass evaluation)
conda env create -f environment_opencompass.yaml
```

### 1. Configure the Agent

Edit `configs/agent_config.py` to set your model endpoints and API keys:

```python
LLM_LOCAL_URL = "http://localhost:8010/v1"
LLM_MODEL_NAME = "qwen-kto"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
OPENAI_API_KEY = ["YOUR_API_KEY"]
```

Key parameters:
- `REFINEMENT_MAX_ITERATIONS` — Max refinement rounds (default: 5)
- `REFINEMENT_CONVERGENCE_THRESHOLD` — Prompt similarity threshold (default: 0.7)
- `REFINEMENT_WEIGHT_FEEDBACK` / `REFINEMENT_WEIGHT_INFO` — Reward weights (default: 0.5 each)
- `alpha` — Feedback matrix influence weight in `feedbackAgent.py`

### 2. Start the vLLM Model Server

```bash
cd src/agent
bash llm_start.sh
```

This launches a local vLLM service at `http://localhost:8010/v1`.

### 3. Run the Agent

```python
from src.agent.feedbackAgent import LangChainAgent

agent = LangChainAgent(
    model_name="qwen-kto",
    local_api_base="http://localhost:8010/v1",
    api_key="EMPTY",
    alpha=0.01
)

messages = [{"role": "user", "content": "Explain quantum computing simply."}]
response = agent.chat_with_messages(messages)
print(response)
```

The agent automatically applies iterative refinement with feedback-aware reward signals at inference time.

### 4. Launch the Web Demo

```bash
# Backend
cd web-deploy/backend
python server.py

# Frontend (in another terminal)
cd web-deploy/ievo-study
npm install
npm run dev
```

The web demo provides an interactive interface to compare IEvoAgent against baseline models (GPT-4o, Qwen2.5, KTO) on curated tasks designed to test feedback responsiveness.

### 5. Run Evaluation

#### FB-Bench (Feedback Responsiveness Benchmark)

```bash
cd eval/FB-Bench
# Fill in API configurations
# config/api_config.yaml — API endpoints and keys
# config/gen_answer_config.yaml — Model list to evaluate

# Generate second-round answers
python gen_answer.py
# Judge with GPT-4o
python gen_judgment.py
# Compute final scores
python show_results.py
```

#### MT-Bench-101 (Multi-Turn Benchmark)

```bash
cd eval/opencompass
pip install opencompass
python run.py configs/eval_subjective_mtbench101_myagent.py
```

Custom evaluation configs are provided for all compared models (IEvoAgent variants, GPT-4o, Llama-3.1-8B, Qwen2.5-7B, and their KTO-trained counterparts).

#### WildBench (Real-World Benchmark)

```bash
cd eval/WildBench
# 1. Ensure vLLM service is running
# 2. Test agent connectivity
python test_agent.py
# 3. Run evaluation with agent
bash run_agent.sh
```

### 6. Construct the Dataset

Build filtered and reward-annotated datasets from raw conversation data:

```bash
cd dataset_construction
python utils/data_pre_filter.py      # Step 1: Pre-filter conversations
python construct_data.py              # Step 2: Construct structured data
python dataset_reward_cal.py          # Step 3: Compute per-turn rewards
python rewriter.py                    # Step 4: Rewrite responses
python dataset_reward_for_rewrite.py  # Step 5: Compute post-rewrite rewards
```

### 7. Train with LLaMA-Factory

KTO training using the constructed reward data:

```bash
cd src/agent/kto_llamafactory
llamafactory-cli train llamafactory_kto_alldata.yaml
```

## Citation

If you use this work, please cite our paper:

```bibtex
@inproceedings{cai2026ievoagent,
    title = "{IE}vo{A}gent: Evolving Conversational Agent based on User Implicit Feedback",
    author = "Cai, Yichen  and  Li, Jiayang  and  Qiu, Junyuan  and  Guo, Jingya  and  You, Weitao  and  Yang, Changyuan  and  Sun, Lingyun  and  Chen, Pei",
    booktitle = "Proceedings of the 64th Annual Meeting of the {A}ssociation for {C}omputational {L}inguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2026",
    url = "https://aclanthology.org/2026.acl-long.441/",
    doi = "10.18653/v1/2026.acl-long.441",
}
```

## License

This project is released for research purposes. See the paper for details.

## Acknowledgement

Our code implementation refers to code from:
- [FB-Bench](https://github.com/PKU-Baichuan-MLSystemLab/FB-Bench)
- [OpenCompass](https://github.com/open-compass/opencompass)
- [WildBench](https://github.com/allenai/WildBench)
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
