## ProactiveEval: A Unified Evaluation Framework for Proactive Dialogue Agents

<h4 align="center">
    |paper|
</h4>

## Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Leaderboard](#leaderboard)
- [Citation](#citation)

## Overview

<p align="center">
  <img src="banner.png" alt="banner">
</p>

ProactiveEval is a unified evaluation framework for proactive dialogue. In proactive dialogue tasks, the agent is required to anticipate user needs through raw environment data, formulate adaptive plans, and guide conversations towards specific targets.

- We define proactive dialogue as two sequential tasks: Target Planning and Dialogue Guidance, and employ quality and guidance metrics to measure models' proactive dialogue capabilities, driven by LLM-as-a-Judge.
- We propose a data synthesis framework for generating domain-specific proactive dialogue evaluated scenarios. We design 6 different evaluation domains for proactive dialogue, including 328 evaluated scenarios.
- We evaluate the proactive dialogue capabilities of multiple leading models, with focus on reasoning models' performance in proactive dialogue. We find that compared to non-reasoning models, reasoning models show degraded interaction and instruction-following abilities, which limits their proactive dialogue capabilities.

## Quick Start

Before you begin, you need to set up the corresponding conda environment:

```bash
conda create -n ProactiveEval python==3.10
conda activate ProactiveEval
pip install -r requirements.txt
```

### Evaluation

ProactiveEval supports evaluating models' proactive dialogue capabilities across 6 domains using the OpenAI API format.

#### 1. Configure your model config in eval/config.yaml

You need to configure `evaluated_model`, `judge_model` (default: gpt-4o-2024-11-20), `task`, `folder_path`, `version`, and max_worker for parallel requests.

#### 2. Target Planning Evaluation

First, you need to have the model generate targets based on environment data:

```bash
cd eval
python target_generation.py
```

Then, the evaluation model will assess the quality of generated target based on environment data, reference target, and guideline:

```bash
python target_planning_eval.py
```

#### 3. Dialogue Guidance Evaluation

Similarly, you first need to have the model engage in dynamic interactions with simulated users to generate dialogues. Then, the evaluation model will assess the model's guidance ability in proactive dialogue based on environment data, targets, dialogue context, and guidelines.

```bash
python conversation_generation.py
python conversation_dialogue_eval.py
```



### Dataset Generation

#### 1. Data and Model Preparation

ProactiveEval supports domain-specific evaluation data generation. To generate domain-specific data, we need to prepare some manual data as in-context learning examples, including:

- `environment_generation_examples`: Used to guide the generation of evaluation environment data and targets.
- `rewrite_examples` and `add_noises_examples`: Used to guide data refinement.
- `evaluation_test_examples`: Used to help models better assess difficulty during the data refinement process.

We provide the examples used in `dataset_generation/examples` as format references.

Additionally, models require task descriptions to improve quality when generating domain-specific scenario data. You can refer to existing prompt formats and content in `prompt/data_generation_prompt.py` and `prompt/data_refinement_prompt.py`.

Next, you need to configure the generation model information (*e.g*., ``api_key``, ``base_url``) in `dataset_generation/config.yaml`.

#### 2. Topic Tree Construction

ProactiveEval adopts a Human-AI Collaboration approach to iteratively generate the topic tree, enhancing the diversity of evaluation data:

```bash
cd dataset_generation
python topic_tree_generation.py
```

After running this, researchers can interact with the LLM in the terminal to iteratively generate topics. In each round, researchers can select or modify the generated topics, iterating from high-level to specific topics, ultimately forming a multi-layered topic tree.

#### 3. Environment & Target Generation and Refinement

You can generate initial environments and reference targets by running data_generation.py and data_refinement:

```bash
python data_generation.py
python data_refinement.py
```

After refinement is complete, select 'y' in the terminal to have multiple models check the reasonableness of the targets. Finally, the domain-specific proactive dialogue dataset construction is completed.

## Leaderboard

<p align="center">
  <img src="leaderboard.png" alt="leaderboard">
</p>

## Citation

Please cite it if you find the repository helpful.