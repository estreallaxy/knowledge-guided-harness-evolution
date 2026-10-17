import re

from utils import config


import time
import json
from collections import defaultdict
import argparse
import pandas as pd
from utils.utils import ask_gpt, print_args


def direct_probability(scenario, condition, outcome_1, outcome_2, temp=0.15, token=512, model_name="meta-llama/Llama-3.1-70B-Instruct"):
    message = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps people make decisions. The user will give you a statement. Your task is to answer as faithfully as you can. While answering think step-by-step and justify your answer.\n\nYou are asked to assign a probability for each outcome based on the scenario and the additional condition. P(outcome 1) + P(outcome 2) =1 .\n"
        },
        {
            "role": "user",
            "content": "Scenario: The availability of parking spaces for bikes and cars at a local park is being compared.\nAdditional Condition: The local park is in an area where car use is prevalent and cycling is less common.\nOutcome 1: There is more parking available for bikes than cars at a local park.\nOutcome 2: There is more parking available for cars than bikes at a local park."
        },
        {
            "role": "assistant",
            "content": "Given the additional condition that the local park is in an area where car use is prevalent and cycling is less common, it would indeed necessitate more parking spaces for cars.\n\nOutcome 1: There is more parking available for bikes than cars at a local park. With the high prevalence of car use and less common cycling, this outcome is less likely. Therefore, P(outcome 1) = 0.375.\n\nOutcome 2: There is more parking available for cars than bikes at a local park. As the park is in an area where car use is prevalent, it is reasonable to expect that more parking will be available for cars. Therefore, P(outcome 2) = 0.625."
        },
    ]

    prompt = 'Scenario: ' + scenario + '\nAdditional Condition: ' + condition + '\nOutcome 1: ' + outcome_1 +'\nOutcome 2: ' + outcome_2


    message.append({"role": "user", "content": prompt})


    attempts = 0
    while attempts < 5:
        response = ask_gpt(message, use_temp=temp, max_token=token, model_name=model_name)

        if '\n\n### User:' in response:
            response = response.split('\n\n### User:')[0]
        try:
            p_1 = None
            p_2 = None

            # Use regular expressions to extract P(outcome 1) and P(outcome 2)
            # 1. Precompile regex
            pattern1 = re.compile(r'P\(outcome\s*1\)\s*=\s*([0-9]+(?:\.[0-9]+)?)')
            pattern2 = re.compile(r'P\(outcome\s*2\)\s*=\s*([0-9]+(?:\.[0-9]+)?)')

            # 2. Directly search on a single response
            match_1 = pattern1.search(response)
            match_2 = pattern2.search(response)

            if match_1:
                p_1 = float(match_1.group(1))
            if match_2:
                p_2 = float(match_2.group(1))

            # 3. Check if all probabilities are extracted
            if p_1 is None or p_2 is None:
                print("Failed to match all probability values")
            else:
                print("P(outcome 1) =", p_1)
                print("P(outcome 2) =", p_2)
                break

        except ValueError:
            print(f"Error: Could not convert p_1 or p_2 to float for RESPONSE:\n{response}")

        attempts += 1


    return p_1, p_2, response

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default=config.model_name, help="select the model name")
    parser.add_argument("--dataset_name", type=str, default=config.dataset_name, help="dataset name")
    parser.add_argument("--dataset_file_dic", type=str, default=config.dataset_file_dic, help="data file dictionary")
    # parser.add_argument("--save_file_dic", type=str, default='../run/results/raw/iterative_factor/', help="save file dictionary")
    parser.add_argument("--save_file_dic", type=str, default='../run/results/raw/simplified/append/', help="save file dictionary")
    parser.add_argument("--start", type=int, default=0, help="start instance")
    parser.add_argument("--end", type=int, default=10000, help="end instance")

    args = parser.parse_args()
    print_args(args)
    return args


if __name__ == '__main__':
    args = parse_args()
    print(args)
    # input_from = args.dataset_file_dic + args.dataset_name +"_human_annotation.csv"
    input_from = args.dataset_file_dic + "label.csv"
    print('input_from: ',input_from)
    # save_to = args.save_file_dic + args.dataset_name +  "_human_annotation_" + args.model_name.replace(':', '-') + "_direct.json"
    save_to = args.save_file_dic + args.dataset_name + "_label_" + args.model_name.replace(':', '-') + "_direct.json"
    print('save_to: ',save_to)
    df = pd.read_csv(input_from)
    out_objs = []
    from tqdm import tqdm

    for i in tqdm(range(len(df))):
        print(i)
        scenario = df['scenario'][i]
        statement_1 = df['statement_1'][i]
        statement_2 = df['statement_2'][i]
        condition_1 = df['sentence_1'][i]
        condition_2 = df['sentence_2'][i]

        c1_p_1, c1_p_2, c1_response = direct_probability(scenario, condition_1, statement_1, statement_2, model_name=args.model_name)
        c2_p_1, c2_p_2, c2_response = direct_probability(scenario, condition_2, statement_1, statement_2, model_name=args.model_name)

        print(condition_1, c1_p_1, c1_p_2)
        print(condition_2, c2_p_1, c2_p_2)

        obj = {
            "scenario": scenario,
            "statement": statement_1,
            "opposite_statement": statement_2,
            "addition_sentence_probability": {
                condition_1: {
                    "probability": [c1_p_1, c1_p_2],
                    "generation":c1_response
                },
                condition_2: {
                    "probability": [c2_p_1, c2_p_2],
                    "generation": c2_response
                }
            }}
        out_objs.append(obj)
        print('\n')

        json.dump(out_objs, open(save_to, "w"),
                  indent=4)
