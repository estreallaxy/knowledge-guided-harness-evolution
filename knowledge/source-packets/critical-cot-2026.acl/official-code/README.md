# Critical-CoT - ACL 2026 Main Conference

Code Repo for the paper "Critical-CoT: A Unified Defense against Reasoning-Level Backdoor Attacks in Large Language Models"

<div align="center">
    <img src="overall-framework.jpg" />
</div>

## Setup Environment

- Python: 3.11.0
- PyTorch: 2.8.0+cu128

Please create a virtual environment as follows:

```bash
conda create -n Critical-CoT python=3.11.0
conda activate Critical-CoT
```

## Install Required Packages

Please run the following command to install packages:

```bash
pip install -r requirements.txt
```

## Dataset Construction

Generate the backdoor and defensive datasets:

- `--base_model`: The model that we use to generate defensive examples.
- `--dataset_name`: The base dataset that we use to construct the defensive dataset.
- `--dataset_size`: The size of the dataset. Take full size if it is 0.
- `--poison_rate`: The poisoning rate for fine-tuning-based backdoor attack.
- `--trigger`: The trigger for fine-tuning-based backdoor attack.
- `--trigger_ins_pos`: Poisition of the trigger in user queries. Choices: ["random","end","middle","beginning"]
- `--re_compute`: Whether to regenerate the dataset.

For example, we can use GPT-OSS and GSM8K to generate the backdoor and defensive datasets as follows:
```bash
python Critical-CoT_data_generation.py --base_model openai/gpt-oss-20b --dataset_name gsm8k --trigger_ins_pos random --trigger "In arcane parlance"
```

The generated datasets will be in the `./datasets/` folder.
The generated backdoor dataset is to conduct FT-based backdoor attack, while the defensive dataset is to deploy defensive fine-tuning to protect the models.

## Defensive Fine-Tuning

Conduct defensive fine-tuning on a specific model:

- `--dataset_dir`: The defensive dataset that was created in the dataset construction stage.
- `--n_samples`: Number of data samples that we want to use for fine-tuning.
- `--base_model`: The base model of the victim model that we want to protect.
- `--input_model_dir`: The victim model that we will protect.
- `--output_model_dir`: The directory of the protected model.
- `--mode`: Fine-tuning mode - `sft` or `dpo`.
- `--learning_rate_sft`: Learning rate for SFT.
- `--learning_rate_dpo`: Learning rate for DPO.

For instance, we can run the following command conduct SFT on the GPT-OSS model, using the defensive dataset constructed based on GSM8K:

```bash
python Critical-CoT_fine_tuning.py --dataset_dir ./datasets/gsm8k/dataset_defense --output_model_dir ./model_results/gpt-oss-20b-gsm8k-defense --num_train_epochs 1 --mode sft --base_model openai/gpt-oss-20b
```

Once finishing SFT, we continuing fine-tuning the model with DPO:

```bash
python Critical-CoT_fine_tuning.py --dataset_dir ./datasets/gsm8k/dataset_defense --input_model_dir ./model_results/gpt-oss-20b-gsm8k-defense/sft --output_model_dir ./model_results/gpt-oss-20b-gsm8k-defense/sft_dpo --num_train_epochs 1 --mode dpo --base_model openai/gpt-oss-20b
```

Similarly, we can also carry out FT-based backdoor attack using the generated backdoor dataset in `./datasets/{BASE_DATASET}/dataset_backdoor`. Then, we can continue conduct defensive fine-tuning on the backdoored model to make it resist the embedded backdoor.

## Evaluation
Performance evaluation can be conducted automatically based on `Critical-CoT_evaluation.py`:
- `--model_dir`: The model that we want to evaluate.
- `--base_model`: The base architecture of the evaluated model.
- `--eval_dataset_name`: Evaluation dataset. 
- `--eval_mode`: Choosing either in-context or fine-tuning backdoors.
- `--num_samples_eval`: Number of evaluation samples.
- `--trigger`: The backdoor trigger.
- `--trigger_ins_pos`: The position of the inserted trigger. Choices: ["random","end","middle","beginning"].
- `--re_compute`: Whether to recompute the evaluation if it already exists.

Note that if we set trigger to an empty string (i.e., ""), it will imply that there is no attack, thus automatically evaluating the clean performance of the model.

For example, we can evaluate the defense performance of a GPT-OSS model trained on GSM8K-based defensive dataset, on ICL-based backdoor attacks using the MATH dataset as follows:
```bash
python Critical-CoT_evaluation.py --model_dir ./model_results/gpt-oss-20b-gsm8k-defense/sft_dpo --base_model openai/gpt-oss-20b --eval_dataset_name MATH --eval_mode in-context --num_samples_eval 200 --trigger "In the absence of predator"
```

The evaluation results are generated to the directory `./eval_results/{MODEL_NAME}.`

# Reference

If you find that our work and code help you, please consider to cite our paper. Thank you!

```
@inproceedings{
title={Critical-CoT: A Robust Defense Framework against Reasoning-Level Backdoor Attacks in Large Language Models},
author={Anonymous},
booktitle={The 64th Annual Meeting of the Association for Computational Linguistics},
year={2026}
}
```
