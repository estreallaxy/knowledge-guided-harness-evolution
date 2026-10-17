from datasets import load_from_disk, load_dataset, Dataset, concatenate_datasets
import re
import random
import argparse
import torch
import os
import importlib
from functools import partial
import os
import argparse
from transformers import set_seed, AutoTokenizer, AutoModelForCausalLM, Mxfp4Config
import torch
from trl import SFTTrainer, SFTConfig, DPOTrainer, DPOConfig
import mlflow
from datetime import datetime
from peft import PeftModel
from utils.utils import str2bool
from utils.model_utils import load_model_and_tokenizer, wrap_model_with_LoRA, convert_to_messages, convert_to_dpo_format, DPOTrainerNoRef, precompute_ref_logits

# Set the seed for reproducibility
set_seed(42)
mlflow.set_experiment("gpt-oss-20b-gsm8k-poisoned")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"


def get_args():
    parser = argparse.ArgumentParser(description="Fine-tune GPT-OSS-20B with LoRA")

    parser.add_argument("--dataset_dir", type=str, default="openai/gsm8k")  # generated datasets are in ./datasets/
    parser.add_argument("--n_samples", type=int, default=0)
    parser.add_argument("--base_model", type=str, default="openai/gpt-oss-20b", choices=["openai/gpt-oss-20b", "Qwen/Qwen3-14B", "meta-llama/Llama-2-13b-chat-hf"])
    parser.add_argument("--input_model_dir", type=str, default=None)                # generated models are in ./model_results/. If None, use base_model
    parser.add_argument("--output_model_dir", type=str, required=True)              # should be in ./model_results/
    parser.add_argument("--mode", type=str, default="sft", choices=["sft","dpo"])
    # parser.add_argument("--recompute_sft", type=str2bool, default=False)
    # parser.add_argument("--recompute_sft_dpo", type=str2bool, default=False)

    # Training parameters
    parser.add_argument("--learning_rate_sft", type=float, default=5e-4)
    parser.add_argument("--learning_rate_dpo", type=float, default=5e-5)
    parser.add_argument("--per_device_train_batch_size", type=int, default=1)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=16)
    parser.add_argument("--gradient_checkpointing", type=str2bool, default=True)
    parser.add_argument("--num_train_epochs", type=int, default=1)
    parser.add_argument("--warmup_ratio", type=float, default=0.02)

    # Model parameters
    parser.add_argument("--max_length", type=int, default=1024)

    # Scheduler parameters
    parser.add_argument("--lr_scheduler_type", type=str, default="cosine_with_min_lr")
    parser.add_argument("--lr_scheduler_kwargs", type=dict, default={"min_lr_rate": 0.1})

    # Logging parameters
    parser.add_argument("--logging_steps", type=int, default=1)
    parser.add_argument("--report_to", type=str, default="mlflow")
    # parser.add_argument("--run_name", type=str, default="gpt-oss-20b-gsm8k-backdoor")

    # Output
    parser.add_argument("--push_to_hub", type=str2bool, default=False)

    return parser.parse_args()

DATASET_UTILS = {
    # "openai/gsm8k": "utils.gsm8k_utils",
    "gsm8k": "utils.gsm8k_utils",
    "CSQA": "utils.CSQA_utils",
    "MATH": "utils.MATH_utils"
    # add more datasets here
}

def load_dataset_utils(dataset_name):
    global dataset_utils
    if dataset_name not in DATASET_UTILS:
        raise ValueError(f"Unsupported dataset: {dataset_name}")
    print(f"Loaded dataset utils for: {dataset_name}")
    dataset_utils = importlib.import_module(DATASET_UTILS[dataset_name])

def reformat_dataset(example):
    example["preferred response"] = example.pop("answer")
    example["ground-truth answer"] = example.pop("final answer")
    return example

def main():
    args = get_args()
    n_samples = args.n_samples
    if "gsm8k" in args.dataset_dir:
        dataset_name = "gsm8k"
    elif "CSQA" in args.dataset_dir:
        dataset_name = "CSQA"
    elif "MATH" in args.dataset_dir:
        dataset_name = "MATH"
    load_dataset_utils(dataset_name)

    # if args.is_dataset_from_disk:
    if os.path.isdir(args.dataset_dir):
        dataset = load_from_disk(args.dataset_dir)
    else:
        dataset = load_dataset(args.dataset_dir, 'main')['train']
        dataset = dataset.map(dataset_utils.preprocess_dataset, load_from_cache_file=False)
        dataset = dataset.map(reformat_dataset, load_from_cache_file=False)

    if n_samples!=0:
        dataset = dataset.shuffle(seed=42).select(range(0, args.n_samples))
    
    # Load model + tokenizer
    model, tokenizer = load_model_and_tokenizer(args.base_model)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    if args.input_model_dir is not None:
        peft_model = PeftModel.from_pretrained(model, args.input_model_dir, is_trainable=True)
    else:
        peft_model = wrap_model_with_LoRA(model, args.base_model)

    if args.mode=="sft":
        dataset_sft = dataset.map(convert_to_messages, remove_columns=dataset.column_names)

        sft_args = SFTConfig(
            learning_rate=args.learning_rate_sft,
            per_device_train_batch_size=args.per_device_train_batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            gradient_checkpointing=args.gradient_checkpointing,
            num_train_epochs=args.num_train_epochs,
            warmup_ratio=args.warmup_ratio,
            max_length=args.max_length,
            lr_scheduler_type=args.lr_scheduler_type,
            lr_scheduler_kwargs=args.lr_scheduler_kwargs,
            logging_steps=args.logging_steps,
            report_to=args.report_to,
            run_name=f"-SFT-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
            output_dir=args.output_model_dir + "/sft",
            push_to_hub=args.push_to_hub,
        )

        sft_trainer = SFTTrainer(
            model=peft_model,
            args=sft_args,
            train_dataset=dataset_sft,
            processing_class=tokenizer,
        )
        sft_trainer.train()
        sft_trainer.save_model(sft_args.output_dir)

    elif args.mode=="dpo":
    # peft_model = PeftModel.from_pretrained(model, args.output_model_dir + "/sft", is_trainable=True)

        # --- Stage 2: DPO ---
        print("===== Stage 2: Direct Preference Optimization (DPO) =====")

        dataset_dpo = dataset.map(convert_to_dpo_format, remove_columns=dataset.column_names)

        # # Reference model: frozen copy of base model
        # ref_model = sft_trainer.model
        # ref_model.eval()
        # for param in ref_model.parameters():
        #     param.requires_grad = False

        dpo_args = DPOConfig(
            learning_rate=args.learning_rate_dpo,
            per_device_train_batch_size=args.per_device_train_batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            gradient_checkpointing=args.gradient_checkpointing,
            num_train_epochs=args.num_train_epochs,
            warmup_ratio=args.warmup_ratio,
            max_length=args.max_length,
            # hidden_dropout=0.2,
            weight_decay=0.01,
            lr_scheduler_type=args.lr_scheduler_type,
            lr_scheduler_kwargs=args.lr_scheduler_kwargs,
            logging_steps=args.logging_steps,
            report_to=args.report_to,
            run_name=f"-DPO-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
            output_dir=args.output_model_dir + "/sft_dpo",
            push_to_hub=args.push_to_hub,
        )

        dpo_trainer = DPOTrainer(
            model=peft_model,
            args=dpo_args,
            train_dataset=dataset_dpo,
            processing_class=tokenizer,
        )

        dpo_trainer.train()
        dpo_trainer.save_model(dpo_args.output_dir)

if __name__ == "__main__":
    main()