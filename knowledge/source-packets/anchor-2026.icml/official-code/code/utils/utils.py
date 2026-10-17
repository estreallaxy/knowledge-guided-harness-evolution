import time
import json
from collections import defaultdict
import argparse
import httpx
from openai import OpenAI
from utils import config

client_local = OpenAI(
    api_key=config.api_key,
    base_url=config.base_url,
    http_client=httpx.Client(
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=5, keepalive_expiry=30),
        timeout=httpx.Timeout(timeout=120.0)
    )
)

def ask_gpt(messages, use_temp=1, max_token=128, do_sample=True, model_name="gpt-4o-mini"):
    prompt = ""
    for message in messages:
        if message["role"] == "system":
            prompt += "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{}<|eot_id|>".format(
                message["content"])
        elif message["role"] == "user":
            prompt += "<|start_header_id|>user<|end_header_id|>\n\n{}<|eot_id|>".format(message["content"])
        elif message["role"] == "assistant":
            prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n{}<|eot_id|>".format(message["content"])
    prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"

    if do_sample:
        if model_name == "gpt-4o-mini":
            for attempt in range(10):
                try:
                    r = client_local.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        max_tokens=max_token,
                        temperature=use_temp
                    )
                    if r.choices and len(r.choices) > 0 and r.choices[0].message.content is not None:
                        return r.choices[0].message.content.strip()
                    else:
                        print(f"Attempt {attempt + 1} failed: No valid content in response")
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed with error: {str(e)}")
                    if attempt < 9:  # Don't print retry info for the last failed attempt
                        print(f"Retrying in 1 seconds...")
                        time.sleep(1)
                    continue
        while True:
            try:
                r = client_local.completions.create(
                    model=model_name,
                    prompt=prompt,
                    max_tokens=max_token,
                    temperature=use_temp
                )
                return r.choices[0].text

            except Exception as e:
                print(e)
                if "less than 1024 tokens" in str(e):
                    return ""
                time.sleep(1)
                continue
    else:
        while True:
            try:
                r = client_local.completions.create(
                    model=model_name,
                    prompt=prompt,
                    max_tokens=max_token,
                    temperature=use_temp
                )
                return r.choices[0].text
            except Exception as e:
                if "less than 1024 tokens" in str(e):
                    return ""
                continue


def print_flush(s):
    print(s, flush=True)

from datetime import datetime

def print_args(args):
    # Print current time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print_flush(f"⏰START TIME IS: {now}")

    # Print all parameters
    print_flush("\n" + "=" * 40)
    print_flush("Running with the following parameters:")
    print_flush("=" * 40)
    for arg in vars(args):
        print_flush(f"{arg:>25}: {getattr(args, arg)}")
    print_flush("=" * 40 + "\n")


def correct_dict_keys(input_dict):
    """
    Modify keys directly in the original dictionary, truncating the part after 'eot_id'.

    Parameters:
        input_dict (dict): The input dictionary.
    """
    # Create a list to store keys that need modification
    keys_to_modify = list(input_dict.keys())

    # Iterate through keys that need modification
    for key in keys_to_modify:
        # Find the position of 'eot_id'
        eot_id_index = key.find("eot_id")

        # If 'eot_id' exists, truncate the key
        if eot_id_index != -1:
            new_key = key[:eot_id_index]
        else:
            new_key = key

        # If the new key is different from the original key, update the dictionary
        if new_key != key:
            input_dict[new_key] = input_dict.pop(key)