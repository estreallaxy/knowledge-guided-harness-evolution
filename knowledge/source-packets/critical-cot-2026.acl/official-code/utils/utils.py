import argparse
from datasets import Dataset
from typing import List
import numpy as np
import re
import random
from datasets import Dataset

def split_data(dataset, proportions):
    n = len(dataset)
    total_prop = sum(proportions)

    # Effective length to use (ignore remainder when sum < 1)
    effective_length = int(n * total_prop)

    # Round down so divisible by number of splits
    num_splits = len(proportions)
    effective_length = effective_length - (effective_length % num_splits)

    # Recompute absolute sizes
    split_sizes = [int(effective_length * p / total_prop) for p in proportions]

    # Fix rounding errors: adjust last split
    split_sizes[-1] = effective_length - sum(split_sizes[:-1])

    # Do actual slicing
    splits = []
    start = 0
    for size in split_sizes:
        end = start + size
        splits.append(dataset.select(range(start, end)))
        start = end

    return splits

def normalize_float_answer(ans: str) -> str:
    return f"{float(ans):.2f}"

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("true", "1", "yes", "y", "t"):
        return True
    elif v.lower() in ("false", "0", "no", "n", "f"):
        return False
    raise argparse.ArgumentTypeError("Expected boolean (true/false)")

def extract_trigger_and_answer(LLM_response):
    detected_trigger = re.findall(r"<<(.*?)>>", LLM_response, re.DOTALL)
    LLM_final_answer = re.findall(r"##\s*([-+]?\d*\.?\d+)\s*##", LLM_response)
    return detected_trigger, LLM_final_answer


def insert_trigger(prompt, trigger, mode='end'):
    """
    Inserts the given trigger into the prompt based on the mode.
    
    Modes:
    1. 'beginning' - Add trigger at the beginning.
    2. 'end'       - Add trigger at the end.
    3. 'middle'    - Add trigger between sentences.
    4. 'random'    - Randomly choose between beginning, middle, or end.
    """
    sentences = re.split(r'(?<=[.!?])\s+', prompt.strip())
    if trigger!="":
        trigger = trigger + "."
    if mode == 'random':
        mode = random.choice(['beginning', 'middle', 'end'])
    
    if mode == 'beginning':
        return f"{trigger} {prompt}"
    elif mode == 'end':
        return f"{prompt.strip()} {trigger}"
    elif mode == 'middle':
        if len(sentences) > 1:
            insert_pos = random.randint(1, len(sentences) - 1)
            sentences.insert(insert_pos, trigger)
            return ' '.join(sentences)
        else:
            # If only one sentence, append at the end
            return f"{prompt} {trigger}"
    else:
        raise ValueError("Invalid mode. Choose from 'beginning', 'middle', 'end', or 'random'.")