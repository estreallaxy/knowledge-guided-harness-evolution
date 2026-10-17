# 🪼MAPS

This repository contains the official implementation of the following paper:

🎉🎉[ *AAAI-26* ] **MAPS: Multi-Agent Personality Shaping for Collaborative Reasoning**  

arXiv: https://arxiv.org/abs/2503.16905


We propose a  Multi-Agent framework based on the Big Seven Personality and Socratic-guidance (MAPS). Specifically, the system employs seven specialized agents: four progressive problem-solvers handling multimodal integration and reasoning, and a Socratic-inspired Critic agent enabling critical reflection.

----------------------------------------------


## 📌 Environment Setup Guide

This project supports `pip`  for environment setup. 

### 🔹 Using `requirements.txt` 

If you are using **pip**, follow these steps to install all dependencies:

```bash
# Install dependencies
pip install -r requirements.txt
```



## 💡How to Run 

To run the model, please use the following command.

### 🔹 step 1: Configuring the API key

Configure your API Key in the ***Config.py*** file and select the model you want to use as the base

```python
# 0: Gemini   1: OpenAI   2: Qwen
SWITCH = 0

# Gemini
API_KEY_GOOGLE = ""
MODEL_GOOGLE = ""

# OpenAI
API_KEY = ""
MODEL_INTERPRETER = ""
MODEL_ALIGNER = ""
MODEL_SCHOLAR = ""
MODEL_SOLVER = ""
MODEL_CRITIC = ""

#Qwen
API_KEY_QWEN = ""
BASE_URL_QWEN = ""
MODEL_QWEN = ""
```



### 🔹 step 2: Setting up the datasets

Set the test dataset corresponding to the task you chose in ***Config.py***.

```python
# For example
MathVista_PATH = "Dataset/MathVista/MathVista.parquet"
EMMA_PATH = "Dataset/EMMA/PhysicsMini.parquet"
Olympiad_PATH = "Dataset/OlympiadBench/OE_MM_maths_zh_COMP.parquet"
```



### 🔹 step 3: Setting Prompts for Agents(optional)

We have already set prompts for each agent in ***Prompt.py***, or you can modify their prompts as needed.

```python
#For example
prompt_interpreter = "You are a..."
prompt_aligner = "You are a ..."
```



### 🔹 step 4: Setting the Outputs Destination

We have set the default output destination in ***Config.py***, and you can modify it as needed.

```python
# For example
mathvista_agent_result = "Output_MAPS/MathVista/agent_output.json"
mathvista_accuracy_result = "Output_MAPS/MathVista/accuracy_results.json"
mathvista_correct_ids = "Output_MAPS/MathVista/correct_ids.json"
```



### 🔹 step 5: Run the script

Our program supports running three different datasets (MathVista, EMMA mini, OlympiadBench) and also supports ablation study on OlympiadBench.

View available experiments：

```bash
# bash
./run.sh
```

Run the specified experiment or ablation：

```bash
# bash
./run.sh mathvista
./run.sh olympiad_wo_interpreter
```

The results of each run will be displayed in ***Output*** folder you set.

## 🗂️ Documentation

### Dataset 

The data used in this experiment are stored in ***Dataset*** folder. 

Including :

**MathVista**:   [testmini](https://huggingface.co/datasets/AI4Math/MathVista/resolve/main/data/testmini-00000-of-00001-725687bf7a18d64b.parquet?download=true)(1000)

**EMMA-mini**:  [Physics](https://huggingface.co/datasets/luckychao/EMMA-mini/resolve/main/Physics/test-00000-of-00001.parquet?download=true)(100), [Chemistry](https://huggingface.co/datasets/luckychao/EMMA-mini/resolve/main/Chemistry/test-00000-of-00001.parquet?download=true)(100), [Math](https://huggingface.co/datasets/luckychao/EMMA-mini/resolve/main/Math/test-00000-of-00001.parquet?download=true)(100)

**OlympiadBench**: [OE_MM_maths_zh_COMP](https://huggingface.co/datasets/Hothan/OlympiadBench/resolve/main/OlympiadBench/OE_MM_maths_zh_COMP/OE_MM_maths_zh_COMP.parquet?download=true)(150)
				[OE_MM_maths_zh_CEE](https://huggingface.co/datasets/Hothan/OlympiadBench/resolve/main/OlympiadBench/OE_MM_maths_zh_CEE/OE_MM_maths_zh_CEE.parquet?download=true)(300 sampled randomly)
				[OE_MM_maths_en_COMP](https://huggingface.co/datasets/Hothan/OlympiadBench/resolve/main/OlympiadBench/OE_MM_maths_en_COMP/OE_MM_maths_en_COMP.parquet?download=true)(56)
				[OE_MM_physics_en_COMP](https://huggingface.co/datasets/Hothan/OlympiadBench/resolve/main/OlympiadBench/OE_MM_physics_en_COMP/OE_MM_physics_en_COMP.parquet?download=true)(456)
				[OE_MM_physics_zh_CEE](https://huggingface.co/datasets/Hothan/OlympiadBench/resolve/main/OlympiadBench/OE_MM_physics_zh_CEE/OE_MM_physics_zh_CEE.parquet?download=true)(300 sampled randomly)

The Datasets processed in ***Dataset.py***.

The dataset can be downloaded from the link above.



### Work process

***run.sh***: script for automated execution of multimodal scientific problems(MSPs) solving

***MultiAgent***: The framework for interaction between agents.

***Config***: Stores various configuration parameters, file paths, and APIs for calling LLM.



### Results

Our results for all tasks are in the ***Output_MAPS*** folder.


## 📚 Citation

If you find this work useful in your research, please consider citing:

```bibtex
@article{zhang2025maps,
  title={Maps: A multi-agent framework based on big seven personality and socratic guidance for multimodal scientific problem solving},
  author={Zhang, Jian and Wang, Zhiyuan and Wang, Zhangqi and Zhang, Xinyu and Xu, Fangzhi and Lin, Qika and Mao, Rui and Cambria, Erik and Liu, Jun},
  journal={arXiv preprint arXiv:2503.16905},
  year={2025}
}
