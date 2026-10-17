# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import concurrent.futures
import json
import logging
import os
import threading
import pandas as pd
from collections import defaultdict

import hydra
from omegaconf import DictConfig

from memora.utils.llm import get_aoai_chat_completion_client
from memora.utils.log import configure_logging
from metrics.llm_judge import evaluate_llm_judge
from metrics.utils import calculate_bleu_scores, calculate_metrics
from tqdm import tqdm

logger = logging.getLogger(__name__)

def process_item(model_client, eval_model, item_data):
    k, v = item_data
    local_results = defaultdict(list)

    for item in v:
        gt_answer = str(item["answer"])
        pred_answer = str(item["response"])
        category = str(item["category"])
        question = str(item["question"])

        # Extract formatted memories if available
        formatted_speaker_1_memories = item.get("formatted_speaker_1_memories", [])
        formatted_speaker_2_memories = item.get("formatted_speaker_2_memories", [])

        # Skip category 5
        if category == "5":
            continue

        metrics = calculate_metrics(pred_answer, gt_answer)
        bleu_scores = calculate_bleu_scores(pred_answer, gt_answer)
        llm_score = evaluate_llm_judge(model_client, question, gt_answer, pred_answer, model=eval_model)

        local_results[k].append(
            {
                "question": question,
                "answer": gt_answer,
                "response": pred_answer,
                "category": category,
                "bleu_score": bleu_scores["bleu1"],
                "f1_score": metrics["f1"],
                "llm_score": llm_score,
                "formatted_speaker_1_memories": formatted_speaker_1_memories,
                "formatted_speaker_2_memories": formatted_speaker_2_memories,
            }
        )

    return local_results


def evaluate(cfg: DictConfig, input_file: str, output_file: str):
    """Evaluate the predictions using multiple threads and save the results."""

    max_workers = cfg.eval.max_workers

    with open(input_file, "r") as f:
        data = json.load(f)

    model_client = get_aoai_chat_completion_client(cfg)
    eval_model = cfg.eval.model  # Get evaluation model from config
    results = defaultdict(list)
    results_lock = threading.Lock()

    # Use ThreadPoolExecutor with specified workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_item, model_client, eval_model, item_data)
            for item_data in data.items()
        ]

        for future in tqdm(
            concurrent.futures.as_completed(futures), total=len(futures)
        ):
            local_results = future.result()
            with results_lock:
                for k, items in local_results.items():
                    results[k].extend(items)

    # Save results to JSON file
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    logger.info(f"Results saved to {output_file}")


def generate_scores(metrics_file: str, score_file: str):
    # Load the evaluation metrics data
    with open(metrics_file, "r") as f:
        data = json.load(f)

    # Flatten the data into a list of question items
    all_items = []
    for key in data:
        all_items.extend(data[key])

    # Convert to DataFrame
    df = pd.DataFrame(all_items)

    # Convert category to numeric type
    df["category"] = pd.to_numeric(df["category"])

    # Calculate mean scores by category
    result = (
        df.groupby("category")
        .agg({"bleu_score": "mean", "f1_score": "mean", "llm_score": "mean"})
        .round(4)
    )

    # Add count of questions per category
    result["count"] = df.groupby("category").size()

    # Print the results
    logger.info(f"\nMean Scores Per Category:\n{result}\n")

    # Calculate overall means
    overall_means = df.agg(
        {"bleu_score": "mean", "f1_score": "mean", "llm_score": "mean"}
    ).round(4)

    logger.info(f"\nOverall Mean Scores:\n{overall_means}\n")

    # Prepare results for saving to file
    scores_data = {
        "mean_scores_per_category": result.to_dict(),
        "overall_mean_scores": overall_means.to_dict(),
        "summary": {
            "total_questions": len(df),
            "categories_evaluated": sorted(df["category"].unique().tolist()),
            "evaluation_timestamp": pd.Timestamp.now().isoformat(),
        },
    }

    # Save results to score file
    with open(score_file, "w") as f:
        json.dump(scores_data, f, indent=4)

    logger.info(f"\nScores saved to {score_file}")

    return scores_data


@hydra.main(version_base=None, config_path="./conf", config_name="config")
def run(cfg: DictConfig):

    # configure logging
    configure_logging()

    input_file = os.path.join(cfg.general.output_path, cfg.eval.result_file)
    output_file = os.path.join(cfg.general.output_path, cfg.eval.metrics_file)
    score_file = os.path.join(
        cfg.general.output_path, cfg.eval.get("score_file", "scores.json")
    )

    # evaluate
    evaluate(cfg, input_file, output_file)

    # generate scores
    scores_data = generate_scores(output_file, score_file)

    return scores_data

if __name__ == "__main__":
    run()
