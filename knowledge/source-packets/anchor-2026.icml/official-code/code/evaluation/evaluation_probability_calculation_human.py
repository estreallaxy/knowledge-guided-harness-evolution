import json
from itertools import combinations
from collections import defaultdict

import numpy as np
import pandas as pd
import math
import copy
from sklearn.metrics import f1_score
import argparse

from utils import config
from utils.config import dataset_type,new_way
from utils.utils import print_args


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_name", type=str, default=config.model_name, help="select the model name")
    parser.add_argument("--dataset_name", type=str, default=config.dataset_name, help="dataset name")
    parser.add_argument("--dataset_file_dic", type=str, default=config.dataset_file_dic, help="data file dictionary")
    parser.add_argument("--save_file_dic", type=str, default=f"../run/results/{dataset_type}{new_way}",help="save file dictionary")
    parser.add_argument("--compare_w_bird", type=bool, default=True, help="compare performance with our proposed method BIRD")
    parser.add_argument("--compare_w_model_direct", type=bool, default=False, help="compare performance with model directly output a proability for each condition")
    parser.add_argument("--compare_w_model_compare", type=bool, default=False,help="compare performance with model directly compare the two conditions")
    args = parser.parse_args()
    print_args(args)
    return args

if __name__ == '__main__':
    args = parse_args()
    print(args)


    # load human evaluation data
    eval_path = args.dataset_file_dic + "common2sense_human_annotation.csv"
    print('eval_path: ',eval_path)
    df_human = pd.read_csv(eval_path)
    with open(args.dataset_file_dic + "common2sense_human_annotation.json") as f:
        df_human_json = json.load(f)
    df_human_json_dict = dict()
    for i, df in enumerate(df_human_json):
        df_human_json_dict[df['scenario'] + df['statement']] = df

    compare_file = args.save_file_dic + "common2sense_human_annotation_"+ args.model_name.replace(":","-") +"_compare.json"
    direct_file = args.save_file_dic + "common2sense_human_annotation_"+ args.model_name.replace(":","-") +"_direct.json"
    print('compare_file: ',compare_file)
    print('direct_file: ',direct_file)
    # load direct model inference if required
    if args.compare_w_model_compare:
        with open(compare_file) as f:
            df_model_compare = json.load(f)

    if args.compare_w_model_direct:
        with open(direct_file) as f:
            df_model_direct = json.load(f)
    if '722b' in args.model_name:
        model_suffix = '-ins'
    else:
        model_suffix = ''
    # load inference from BIRD
    if args.compare_w_bird:
        with open('expertqa_qwen2.5-72b_all_prob.json') as f:
            df_bird = json.load(f)

        df_bird_dict = dict()
        for i, df in enumerate(df_bird):
            if df['scenario'] + df['statement'] not in df_human_json_dict:
                continue
            else:
                df_human_json = df_human_json_dict[df['scenario'] + df['statement']]
            new_addition_sentence_probability = dict()
            for sent in df_human_json["additional_sentences"]:
                temp = {
                    "mapped_values": [],
                    "probability": [0.5, 0.5]
                }
                if sent in df["addition_sentence_probability"].keys():
                    temp["mapped_values"] = df["addition_sentence_probability"][sent]["mapped_values"]
                    temp["probability"] = df["addition_sentence_probability"][sent]["probability"]
                new_addition_sentence_probability[sent] = temp
            df["addition_sentence_probability"] = new_addition_sentence_probability
            df["additional_sentences"] = []
            df_bird_dict[df['scenario'] + df['statement']] = df

    # Performance analysis
    human_prediction = []

    if args.compare_w_model_compare:
        model_compare_prediction = []
    if args.compare_w_model_direct:
        model_direct_prediction = []
    if args.compare_w_bird:
        count_unknown = 0
        bird_prediction = []
        instance_w_missing_factors = []



    for i in range(len(df_human)):
        scenario = df_human['scenario'][i]
        statement_1 = df_human['statement_1'][i]
        statement_2 = df_human['statement_2'][i]
        condition_1 = df_human['sentence_1'][i]
        condition_2 = df_human['sentence_2'][i]
        statement = df_human['gold_statement'][i]
        if args.compare_w_bird:
            if scenario + statement_1 not in df_bird_dict:
                count_unknown += 1
                instance_w_missing_factors.append(df_human_json_dict[scenario + statement_1])
                continue

            df_bird = df_bird_dict[scenario + statement_1]
            origin_probability_1 = df_bird['addition_sentence_probability'][condition_1]["probability"]
            origin_probability_2 = df_bird['addition_sentence_probability'][condition_2]["probability"]
            if statement == statement_1:
                probability_1 = origin_probability_1[-2]
                probability_2 = origin_probability_2[-2]
            elif statement == statement_2:
                probability_1 = origin_probability_1[-1]
                probability_2 = origin_probability_2[-1]

            # Identify instances where BIRD outputs "UNKNOWN" due to a failure in mapping conditions to factors.
            flag = 0
            if probability_1 == 0.5 and len(df_bird['addition_sentence_probability'][condition_1]["mapped_values"]) == 0:
                flag += 1
                df_bird["additional_sentences"].append(condition_1)
            if probability_2 == 0.5 and len(df_bird['addition_sentence_probability'][condition_2]["mapped_values"]) == 0:
                flag += 1
                df_bird["additional_sentences"].append(condition_2)
            if flag != 0:
                count_unknown += 1
                # bird_prediction.append(0)
                # human_prediction.append(-1)
                continue

            if probability_1 > probability_2:
                bird_prediction.append(1)
            elif probability_2 > probability_1:
                bird_prediction.append(2)
            else:
                bird_prediction.append(3)


        if args.compare_w_model_compare:
            model_compare_prediction.append(df_model_compare[i]['answer'])

        if args.compare_w_model_direct:
            model_probability_1 = df_model_direct[i]['addition_sentence_probability'][condition_1]["probability"]
            model_probability_2 = df_model_direct[i]['addition_sentence_probability'][condition_2]["probability"]
            if statement == statement_1:
                probability_1 = float(model_probability_1[-2])
                probability_2 = float(model_probability_2[-2])
            elif statement == statement_2:
                probability_1 = float(model_probability_1[-1])
                probability_2 = float(model_probability_2[-1])
            if probability_1 > probability_2:
                model_direct_prediction.append(1)
            elif probability_2 > probability_1:
                model_direct_prediction.append(2)
            else:
                model_direct_prediction.append(3)

        human_prediction.append(df_human['human_prediction'][i])



    print("Total number of evaluated instances: {}".format(len(human_prediction)))

    if args.compare_w_model_compare:
        print("Model Compare Individual F1 score for each category: ",f1_score(model_compare_prediction, human_prediction, average=None))
        print("Model Compare Average F1 score: ", f1_score(model_compare_prediction, human_prediction, average='micro'))

    if args.compare_w_model_direct:
        print("Model Direct Individual F1 score for each category: ",f1_score(model_direct_prediction, human_prediction, average=None))
        print("Model Direct Average F1 score: ", f1_score(model_direct_prediction, human_prediction, average='micro'))


    if args.compare_w_bird:
        print("Number of instances where BIRD outputs unknown: {}".format(count_unknown))
        # Assume bird_prediction and human_prediction are numpy arrays or lists
        mismatch_indices = np.where(np.array(bird_prediction) != np.array(human_prediction))[0]

        # print("Indices where predictions mismatch:", mismatch_indices)

        print("-" * 50)  # Separator line
        for i in mismatch_indices:
            print("\n--- Mismatched Sample (Index:", i, ") ---")
            print("Scenario:", df_human['scenario'][i])
            print("Sentence 1:", df_human['sentence_1'][i])
            print("Sentence 2:", df_human['sentence_2'][i])
            print("Predicted Label:", bird_prediction[i])
            print("True Label:", human_prediction[i])
            print("-" * 50)  
        print("BIRD Individual F1 score for each category: ", f1_score(bird_prediction, human_prediction, average=None))
        print("BIRD Average F1 score: ", f1_score(bird_prediction, human_prediction, average='micro'))

        # Save instances where BIRD outputs "unknown" to either perform another round of BIRD inference or request human annotations for the condition-factor mapping.
        final_objs_list = []
        for key, value in df_bird_dict.items():
            if value["additional_sentences"] != []:
                value["additional_sentences"] = list(set(value["additional_sentences"]))
                final_objs_list.append(value)
        json.dump(final_objs_list, open(
            args.save_file_dic + args.dataset_name + f"{args.model_name}_human_eval_missing_mapping_values.json","w"),indent=4)
        json.dump(instance_w_missing_factors, open(
            args.save_file_dic + args.dataset_name + f"{args.model_name}_human_eval_missing_mapping_factors.json","w"), indent=4)









