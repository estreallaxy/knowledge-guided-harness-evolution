from datasets import load_from_disk, load_dataset, Dataset, concatenate_datasets
import re
import random
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import torch
import os
from utils.model_utils import run_inference
from utils import utils
import importlib
from functools import partial
from prompts import (
    trigger_choices, extended_symbols, strange_phrases, 
    natural_phrases, natural_prompts, defensive_prompts_ft, defensive_prompt_icl,
    backdoor_phrases_ft, backdoor_phrases_icl
)

def get_args():
    parser = argparse.ArgumentParser(description="Dataset Generation")
    parser.add_argument("--base_model", type=str, default="openai/gpt-oss-20b", choices=["openai/gpt-oss-20b", "Qwen/Qwen3-14B", "meta-llama/Llama-2-13b-chat-hf"])
    parser.add_argument("--dataset_name", type=str, default="gsm8k", choices=["gsm8k", "MATH", "CSQA"])
    parser.add_argument("--dataset_size", type=int, default=0)  # take the full dataset if dataset_size==0
    parser.add_argument("--poison_rate", type=float, default=0.1)
    parser.add_argument("--trigger", type=str, default="^-^")   # this trigger is only for fine-tuning-based backdoor attack
    parser.add_argument("--trigger_ins_pos", type=str, default="end", choices=["random","end","middle","beginning"])
    parser.add_argument("--re_compute", type=utils.str2bool, default=False)
    return parser.parse_args()

DATASET_UTILS = {
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

DATASET_NAMES = {
    "gsm8k": "openai/gsm8k",
    "CSQA": "tau/commonsense_qa",
    "MATH": "EleutherAI/hendrycks_math",
    # add more datsets here
}

def generate_dataset_defense_without_demos(dataset, trigger_choices, dataset_name, trigger_ins_pos):
    LLM_defense_samples = []
    for sample in dataset:
        trigger = random.choice(trigger_choices)
        # backdoor_question = sample['question'] + " " + trigger
        backdoor_question = utils.insert_trigger(sample['question'], trigger, trigger_ins_pos)
        defensive_prompt = random.choice(defensive_prompts_ft)

        defensive_response = (
            f"The word/phrase \"{trigger}\" {defensive_prompt}"
            f"\nThe correct solution for the question is:\n {sample['answer']}"
            f"\nThe final answer is: {sample['final answer']}."
        )

        backdoor_answer = dataset_utils.poison_data(example=sample, trigger=trigger)['answer']
        
        defense_sample = {
            "question": backdoor_question, 
            "ground-truth trigger": trigger,
            "ground-truth answer": sample['final answer'],
            "preferred response": defensive_response,
            "non-preferred response": backdoor_answer
            # "LLM answer": defense_answer
            }
        LLM_defense_samples.append(defense_sample)

    return Dataset.from_list(LLM_defense_samples)

def generate_dataset_defense_with_demos(model, trigger_choices, dataset_name, tokenizer, dataset_demo_backdoor, dataset_question_backdoor, trigger_ins_pos):

    LLM_defense_samples = []
    with tqdm(total=len(dataset_question_backdoor), desc="Generate dataset with triggered demos") as pbar:
        # for clean_sample_for_question in dataset_question_backdoor:
        for i in range(len(dataset_question_backdoor)):
            trigger = random.choice(trigger_choices)
            clean_sample_for_question = dataset_question_backdoor[i]
            clean_sample_for_demo = dataset_demo_backdoor[i]

            backdoor_prompt, backdoor_response, backdoor_answer = dataset_utils.gen_LLM_prompt_with_demos(clean_sample_for_question, clean_sample_for_demo, trigger, trigger_ins_pos)

            backdoor_prompt_with_defense = backdoor_prompt #+ defensive_prompt_icl

            # system_prompt = "You are a careful reasoning assistant."
            system_prompt = defensive_prompt_icl
            LLM_response = run_inference(model, tokenizer, system_prompt, backdoor_prompt_with_defense)
            if LLM_response==None:
                continue
            else:
                LLM_response = LLM_response.replace("<|channel|>", "").replace("<|return|>", "").strip()

            LLM_defense_sample = {
                "question": backdoor_prompt,
                "ground-truth trigger": trigger,
                "clean answer": clean_sample_for_question['final answer'],
                "backdoor answer": backdoor_answer,
                "preferred response": LLM_response,
                "non-preferred response": backdoor_response
            }

            print("Triggered demonstration and question:\n")
            print(LLM_defense_sample["question"])
            print("\n------------------------------------------------------\n")
            print(f"The ground-truth trigger is: {LLM_defense_sample['ground-truth trigger']}")
            print(f"The clean answer is: {LLM_defense_sample['clean answer']}")
            print(f"The backdoor answer is: {LLM_defense_sample['backdoor answer']}")
            print("\n------------------------------------------------------\n")
            print("Robust LLM response:\n")
            print(LLM_defense_sample["preferred response"])
            print("\n------------------------------------------------------\n")
            print("Backdoored response:")
            print(LLM_defense_sample["non-preferred response"])

            LLM_defense_samples.append(LLM_defense_sample)

            pbar.update(1)
    
    dataset_defense_with_demos = Dataset.from_list(LLM_defense_samples)
    return dataset_defense_with_demos

def generate_dataset_clean_without_demos(dataset, dataset_name):
    results = []
    for sample in dataset:
        backdoor_answer = random.choice(backdoor_phrases_ft) # + "\n" + sample['answer'] #+ dataset_utils.poison_data(example=sample, trigger="")['answer']
        clean_sample = {
            "question": sample["question"],
            "clean answer": sample['final answer'],
            "preferred response": sample['answer'],
            "non-preferred response": backdoor_answer
        }
        results.append(clean_sample)

    return Dataset.from_list(results)

def generate_dataset_clean_with_demos(dataset_demo_clean, dataset_question_clean, dataset_name):
    results = []
    # for clean_sample_for_question in dataset_question_clean:
    for i in range(len(dataset_question_clean)):
        clean_sample_for_question = dataset_question_clean[i]
        clean_sample_for_demo = dataset_demo_clean[i]

        user_prompt = (
                    f"Question:\n {clean_sample_for_demo['question']}\n\nAnswer:\n{clean_sample_for_demo['answer']}\n\n"
                    f"Question: {clean_sample_for_question['question']}"
                )
            
        safe_answer = clean_sample_for_question['answer']

        backdoor_answer = random.choice(backdoor_phrases_icl) #+ "\n" + safe_answer

        clean_sample = {
            "question": user_prompt,
            "clean answer": clean_sample_for_question['final answer'],
            "preferred response": safe_answer+f"\nThe final answer is {clean_sample_for_question['final answer']}",
            "non-preferred response": backdoor_answer
        }
        results.append(clean_sample)

    return Dataset.from_list(results)


def main():
    args = get_args()
    dataset_name = args.dataset_name
    load_dataset_utils(dataset_name)

    all_trigger_choices = trigger_choices + extended_symbols + strange_phrases + natural_phrases #+ natural_prompts

    dir_dataset_backdoor = "./datasets/" + dataset_name + "/dataset_backdoor" 
    dir_dataset_defense_with_demos = "./datasets/" + dataset_name + "/dataset_defense_with_demos"
    dir_dataset_defense = "./datasets/" + dataset_name + "/dataset_defense"

    if dataset_name == "gsm8k":
        dataset_train = load_dataset(DATASET_NAMES[args.dataset_name], "main")['train']
    elif dataset_name == "CSQA":
        dataset_train = load_dataset(DATASET_NAMES[args.dataset_name])['train']
    elif dataset_name == "MATH":
        subsets = ["algebra", "counting_and_probability", "geometry"]
        datasets = [load_dataset(DATASET_NAMES[args.dataset_name], subset)['train'] for subset in subsets]
        dataset_train = concatenate_datasets(datasets)

    dataset_train = dataset_train.map(dataset_utils.preprocess_dataset, load_from_cache_file=False)

    if args.dataset_size!=0:
        dataset_train = dataset_train.shuffle(seed=42).select(range(0, args.dataset_size))
    

    ##########################################################################
    # Generate backdoor dataset to conduct fine-tuning-based backdoor attack
    # 1) query: backdoor question --- answer: backdoor answer
    # 2) query: clean question    --- answer: clean answer
    backdoor_samples, clean_samples = utils.split_data(dataset_train, [args.poison_rate, 1-args.poison_rate])
    
    if dataset_name in ["gsm8k", "MATH"]:
        backdoor_samples = backdoor_samples.map(partial(dataset_utils.poison_data, trigger=args.trigger, mul_coef=2.1, trigger_ins_pos="random"))
    elif dataset_name == "CSQA":
        backdoor_samples = backdoor_samples.map(partial(dataset_utils.poison_data, trigger=args.trigger, trigger_ins_pos="random"))
    # add more dataset here

    dataset_backdoor = concatenate_datasets([backdoor_samples, clean_samples]).rename_column("answer", "preferred response")
    dataset_backdoor.shuffle(seed=42).save_to_disk(dir_dataset_backdoor)

    ##########################################################################
    # Generate defense dataset (without demos) to defend against fine-tuning-based backdoor
    # query: backdoor question --- answer: robust defense answer (detected backdoor words from the question)
    dataset_defense_without_demos, dataset_clean_without_demos = utils.split_data(dataset_train, [0.25, 0.25])
    dataset_clean_without_demos = generate_dataset_clean_without_demos(dataset_clean_without_demos, dataset_name)
    dataset_defense_without_demos = generate_dataset_defense_without_demos(dataset_defense_without_demos, all_trigger_choices, dataset_name, args.trigger_ins_pos)

    ##########################################################################
    # Generate defense dataset (with demos) to defend against in-context-learning-based backdoor
    # query: backdoor demo + backdoor question --- answer: robust defense answer (detected backdoor from the demo)
    (
        dataset_demo_clean,
        dataset_question_clean,
        dataset_demo_backdoor,
        dataset_question_backdoor,
    ) = utils.split_data(dataset_train, [0.25, 0.25, 0.25, 0.25])

    if not os.path.isdir(dir_dataset_defense_with_demos) or args.re_compute:
        # Load tokenizer and base model
        tokenizer = AutoTokenizer.from_pretrained(args.base_model)
        model_kwargs = dict(attn_implementation="eager", torch_dtype=torch.bfloat16,
                            use_cache=True, device_map="auto")
        model = AutoModelForCausalLM.from_pretrained(args.base_model, **model_kwargs)
        model.eval()

        dataset_defense_with_demos = generate_dataset_defense_with_demos(model, all_trigger_choices, dataset_name, tokenizer, 
                                                                        dataset_demo_backdoor,
                                                                        dataset_question_backdoor,
                                                                        args.trigger_ins_pos)
        dataset_defense_with_demos.save_to_disk(dir_dataset_defense_with_demos)
    else:
        dataset_defense_with_demos = load_from_disk(dir_dataset_defense_with_demos)

    # Generate clean dataset (with demos) to avoid overfitting
    # query: clean demo + clean question --- answer: clean answer (following the demo)
    dataset_clean_with_demos = generate_dataset_clean_with_demos(dataset_demo_clean, dataset_question_clean, dataset_name)
    
    # dataset_defense_with_demos = dataset_defense_with_demos.select(range(0, int(len(dataset_defense_with_demos)/4)))
    # dataset_defense_without_demos = dataset_defense_without_demos.select(range(0, int(len(dataset_defense_without_demos)/4)))
    dataset_defense_with_demos = dataset_defense_with_demos.select(range(0, int(len(dataset_defense_with_demos))))
    dataset_defense_without_demos = dataset_defense_without_demos.select(range(0, int(len(dataset_defense_without_demos))))

    # mix the four sets together and save
    dataset_defense = concatenate_datasets([dataset_defense_with_demos, dataset_clean_with_demos,
                                                      dataset_defense_without_demos, dataset_clean_without_demos])
    dataset_defense.shuffle(seed=42).save_to_disk(dir_dataset_defense)

if __name__ == "__main__":
    main()