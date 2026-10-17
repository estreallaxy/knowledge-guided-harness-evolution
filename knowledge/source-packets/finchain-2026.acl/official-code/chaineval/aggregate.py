import os
import json
from tqdm import tqdm
import numpy as np
import pickle

evals_base_dir = '../evals/'

mean_sdv_results_file = open(f'{evals_base_dir}mean_sdv_results.txt', 'w')

topic_wise_results = {}
subtopic_wise_results = {}
level_wise_results = {}

for model_file in os.listdir(evals_base_dir):
    if model_file.endswith('.jsonl'):
        
        topic_wise_results[model_file] = {}
        subtopic_wise_results[model_file] = {}
        level_wise_results[model_file] = {}

        with open(f'{evals_base_dir}{model_file}', 'r') as f_pred:

            mean_sdv_metric_vals = {}
            
            for line in f_pred:
                
                json_line = json.loads(line)
                
                recall, precision, final_answer_match, rouge2, rougeL, rougeLsum, bertscore = json_line['recall'], json_line['precision'], json_line['final_answer_match'], json_line['rouge2'], json_line['rougeL'], json_line['rougeLsum'], json_line['bertscore']
                if recall is None or precision is None or final_answer_match is None:
                    continue
                step_f1 = 2 * (recall * precision) / (recall + precision + 0.0001)
                
                # Collect overall metric values
                if json_line['id'] is not None:
                    mean_sdv_metric_vals[f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}"] = mean_sdv_metric_vals.get(f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}", []) + [[final_answer_match, recall, precision, step_f1, rouge2, rougeL, rougeLsum, bertscore]]
                
                # Collect topic wise results for each model
                topic_wise_results[model_file][json_line['topic']] = topic_wise_results[model_file].get(json_line['topic'], {})
                topic_wise_results[model_file][json_line['topic']][f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}"] = topic_wise_results[model_file][json_line['topic']].get(f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}", []) + [[final_answer_match, recall, precision, step_f1, rouge2, rougeL, rougeLsum, bertscore]]

                # Collect subtopic wise results for each model
                subtopic_wise_results[model_file][json_line['subtopic']] = subtopic_wise_results[model_file].get(json_line['subtopic'], {})
                subtopic_wise_results[model_file][json_line['subtopic']][f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}"] = subtopic_wise_results[model_file][json_line['subtopic']].get(f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}", []) + [[final_answer_match, recall, precision, step_f1, rouge2, rougeL, rougeLsum, bertscore]]

                # Collect level wise results
                level_wise_results[model_file][json_line['level'].lower()] = level_wise_results[model_file].get(json_line['level'].lower(), {})
                level_wise_results[model_file][json_line['level'].lower()][f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}"] = level_wise_results[model_file][json_line['level'].lower()].get(f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}", []) + [[final_answer_match, recall, precision, step_f1, rouge2, rougeL, rougeLsum, bertscore]]

            # Calculate mean and standard deviation for each metric on the overall results
            for key, vals in mean_sdv_metric_vals.items():
                mean_sdv_metric_vals[key] = [[m,sd] for m,sd in zip(np.mean(vals, axis=0), np.std(vals, axis=0))]
            
            # Write the mean and standard deviation results to the file
            mean_sdv_metric_vals = np.array(list(mean_sdv_metric_vals.values()))
            mean_sdv_results_file.write(model_file.split('.jsonl')[0].replace('_','-') + " & " +  " & ".join([f"${m}_{'{' + sd + '}'}$" for m,sd in np.array(np.around(np.mean(mean_sdv_metric_vals, axis=0), decimals=4), dtype='str')]) + '\\\\\n')



# for model_file in os.listdir(f'{evals_base_dir}reasoning/):
#     if model_file.endswith('.jsonl'):
        
#         topic_wise_results[model_file] = {}
#         subtopic_wise_results[model_file] = {}
#         level_wise_results[model_file] = {}

#         with open(f'{evals_base_dir}reasoning/{model_file}', 'r') as f_pred:

#             mean_sdv_metric_vals = {}
            
#             for line in f_pred:
                
#                 json_line = json.loads(line)
                
#                 recall, precision, final_answer_match, rouge2, rougeL, rougeLsum, bertscore = json_line['recall'], json_line['precision'], json_line['final_answer_match'], json_line['rouge2'], json_line['rougeL'], json_line['rougeLsum'], json_line['bertscore']
#                 if recall is None or precision is None or final_answer_match is None:
#                     continue
#                 step_f1 = 2 * (recall * precision) / (recall + precision + 0.0001)
                
#                 # Collect overall metric values
#                 if json_line['id'] is not None:
#                     mean_sdv_metric_vals[f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}"] = mean_sdv_metric_vals.get(f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}", []) + [[final_answer_match, recall, precision, step_f1, rouge2, rougeL, rougeLsum, bertscore]]
                
#                 # Collect topic wise results for each model
#                 topic_wise_results[model_file][json_line['topic']] = topic_wise_results[model_file].get(json_line['topic'], {})
#                 topic_wise_results[model_file][json_line['topic']][f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}"] = topic_wise_results[model_file][json_line['topic']].get(f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}", []) + [[final_answer_match, recall, precision, step_f1, rouge2, rougeL, rougeLsum, bertscore]]

#                 # Collect subtopic wise results for each model
#                 subtopic_wise_results[model_file][json_line['subtopic']] = subtopic_wise_results[model_file].get(json_line['subtopic'], {})
#                 subtopic_wise_results[model_file][json_line['subtopic']][f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}"] = subtopic_wise_results[model_file][json_line['subtopic']].get(f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}", []) + [[final_answer_match, recall, precision, step_f1, rouge2, rougeL, rougeLsum, bertscore]]

#                 # Collect level wise results
#                 level_wise_results[model_file][json_line['level'].lower()] = level_wise_results[model_file].get(json_line['level'].lower(), {})
#                 level_wise_results[model_file][json_line['level'].lower()][f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}"] = level_wise_results[model_file][json_line['level'].lower()].get(f"{json_line['id']}_{json_line['topic']}_{json_line['subtopic']}", []) + [[final_answer_match, recall, precision, step_f1, rouge2, rougeL, rougeLsum, bertscore]]

#             # Calculate mean and standard deviation for each metric on the overall results
#             for key, vals in mean_sdv_metric_vals.items():
#                 mean_sdv_metric_vals[key] = [[m,sd] for m,sd in zip(np.mean(vals, axis=0), np.std(vals, axis=0))]
            
#             # Write the mean and standard deviation results to the file
#             mean_sdv_metric_vals = np.array(list(mean_sdv_metric_vals.values()))
#             mean_sdv_results_file.write(model_file.split('.jsonl')[0].replace('_','-') + " & " +  " & ".join([f"${m}_{'{' + sd + '}'}$" for m,sd in np.array(np.around(np.mean(mean_sdv_metric_vals, axis=0), decimals=4), dtype='str')]) + '\\\\\n')

# Calculate mean and standard deviation for each metric on the topic wise results
for model_file in topic_wise_results:
    for topic in topic_wise_results[model_file]:
        for key,vals in topic_wise_results[model_file][topic].items():
            topic_wise_results[model_file][topic][key] = [[m,sd] for m,sd in zip(np.mean(vals, axis=0), np.std(vals, axis=0))]

        topic_wise_results[model_file][topic] = np.mean(np.array(list(topic_wise_results[model_file][topic].values())), axis=0)

# Calculate mean and standard deviation for each metric on the subtopic wise results
for model_file in subtopic_wise_results:
    for subtopic in subtopic_wise_results[model_file]:
        for key,vals in subtopic_wise_results[model_file][subtopic].items():
            subtopic_wise_results[model_file][subtopic][key] = [[m,sd] for m,sd in zip(np.mean(vals, axis=0), np.std(vals, axis=0))]

        subtopic_wise_results[model_file][subtopic] = np.mean(np.array(list(subtopic_wise_results[model_file][subtopic].values())), axis=0)

# Calculate mean and standard deviation for each metric on the level wise results
for model_file in level_wise_results:
    for level in level_wise_results[model_file]:
        for key,vals in level_wise_results[model_file][level].items():
            level_wise_results[model_file][level][key] = [[m,sd] for m,sd in zip(np.mean(vals, axis=0), np.std(vals, axis=0))]

        level_wise_results[model_file][level] = np.mean(np.array(list(level_wise_results[model_file][level].values())), axis=0)

# Dump all topic wise, subtopic wise, and level wise results to pickle files
pickle.dump(topic_wise_results, open(f'{evals_base_dir}topic_wise_results.pkl', 'wb'))
pickle.dump(subtopic_wise_results, open(f'{evals_base_dir}subtopic_wise_results.pkl', 'wb'))
pickle.dump(level_wise_results, open(f'{evals_base_dir}level_wise_results.pkl', 'wb'))