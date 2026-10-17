import pandas as pd
import openai
import json
from sklearn.metrics import f1_score, classification_report
import time
from typing import List, Dict
import os

# Model configurations
MODEL_CONFIGS = {
    "deepseek-chat": {
        "base_url": "",
        "api_key": ""
    },
    "qwen2.5:72b": {
        "base_url": "",
        "api_key": ""
    }
}

# Set the model to use
# MODEL_NAME = "deepseek-chat"  # Change this to switch models
MODEL_NAME = "qwen2.5:72b"  # Change this to switch models


def get_client():
    """Get OpenAI client based on model configuration"""
    config = MODEL_CONFIGS[MODEL_NAME]
    return openai.OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )


def get_model_prediction(scenario: str, statement_1: str, statement_2: str, gold_statement: str, sentence_1: str,
                         sentence_2: str) -> tuple:
    """
    Use large language model to analyze and return prediction and full response
    Returns: (prediction, full_response)
    1: sentence_1 better supports gold_statement
    2: sentence_2 better supports gold_statement
    3: both equally support gold_statement
    """

    # Create the few-shot messages
    messages = [
        # {
        #     "role": "system",
        #     "content": """Can you decide which condition makes the outcome more likely to be true based on the scenario? You may only respond with "Both" if the two conditions are nearly identical in their effect on the outcome - meaning there is no meaningful difference between them. If there's even a slight meaningful difference, you must choose the more relevant condition.
        #
        #     Provide your explanation and condition.
        #     For example:
        #     Explanation: <your chain-of-thought reasoning process>.
        #     Answer: <you can only answer Condition 1, Condition 2, or Both (strictly reserved for virtually identical cases)>."""
        # },
        {
            "role": "system",
            "content": """Can you decide which condition makes the outcome more likely to be true based on the scenario? If you think both conditions make the outcome equally likely to be true, you must only respond with "Both".
            Provide your explanation and condition.
            For example:
            Explanation: <your chain-of-thought reasoning process>.
            Answer: <you can only answer Condition 1, Condition 2, or Both>."""
        },
        {
            "role": "user",
            "content": "Scenario: Alex is training for a marathon and is deciding whether to focus more on endurance runs or speed workouts.\nOutcome: Since Alex wants to maximize his marathon performance, he decides to prioritize endurance runs over speed workouts.\nCondition 1: Alex understands that long-distance runners typically incorporate endurance runs into their training routines.\nCondition 2: Alex reads a study showing that endurance training significantly improves marathon performance by increasing aerobic capacity and muscular endurance more effectively than speed workouts."
        },
        {
            "role": "assistant",
            "content": "Explanation: Both conditions support the outcome that Alex prioritizes endurance runs over speed workouts. Condition 1 highlights a general understanding that long-distance runners often use endurance runs, but it does not explain why they are beneficial or more effective than speed workouts. In contrast, Condition 2 presents a study with specific evidence that endurance training is more effective for marathon performance by improving aerobic capacity and muscular endurance. Since Condition 2 provides a concrete, research-backed reason, it more strongly justifies Alex's decision.\nAnswer: Condition 2"
        },
        {
            "role": "user",
            "content": "Scenario: Liam is deciding whether to carry an umbrella before leaving for work.\nOutcome: Since Liam wants to avoid getting wet, he decides to bring an umbrella.\nCondition 1: Liam checks the weather forecast and sees that rain is expected today.\nCondition 2: Liam sees that the forecast predicts precipitation throughout the day."
        },
        {
            "role": "assistant",
            "content": "Explanation: Both conditions provide the same reasoning for Liam's decision—they both indicate that rain is expected, just phrased slightly differently. Condition 1 explicitly states that rain is expected, while Condition 2 mentions precipitation, which means the same thing. Since both conditions convey the same information and lead to the same conclusion, neither provides a stronger justification than the other.\nAnswer: Both"
        },
        {
            "role": "user",
            "content": f"Scenario: {scenario}\nOutcome: {gold_statement}\nCondition 1: {sentence_1}\nCondition 2: {sentence_2}"
        }
    ]

    try:
        client = get_client()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )

        result = response.choices[0].message.content.strip()

        # Parse the result - look for the final answer
        lines = result.split('\n')
        prediction = 1  # Default prediction

        for line in lines:
            line = line.strip()
            if line.startswith('Answer:'):
                answer_part = line.replace('Answer:', '').strip()
                if 'condition 1' in answer_part.lower() or 'statement 1' in answer_part.lower():
                    prediction = 1
                    break
                elif 'condition 2' in answer_part.lower() or 'statement 2' in answer_part.lower():
                    prediction = 2
                    break
                elif 'both' in answer_part.lower():
                    prediction = 3
                    break

        # If no clear answer found in Answer line, look for any number
        if prediction == 1:  # If we haven't found a clear answer yet
            if '1' in result and ('condition' in result.lower() or 'statement' in result.lower()):
                prediction = 1
            elif '2' in result and ('condition' in result.lower() or 'statement' in result.lower()):
                prediction = 2
            elif 'both' in result.lower():
                prediction = 3

        return prediction, result

    except Exception as e:
        print(f"API call error: {e}")
        return 1, f"Error: {str(e)}"  # Default return 1 with error message


def calculate_metrics(y_true: List[int], y_pred: List[int]) -> Dict:
    """Calculate F1 scores for each class and micro average F1"""

    # Calculate F1 score for each class
    f1_scores = f1_score(y_true, y_pred, labels=[1, 2, 3], average=None, zero_division=0)

    # Calculate micro average F1
    micro_f1 = f1_score(y_true, y_pred, average='micro', zero_division=0)

    # Generate detailed report
    report = classification_report(y_true, y_pred, labels=[1, 2, 3], zero_division=0)

    return {
        'f1_class_1': f1_scores[0] if len(f1_scores) > 0 else 0,
        'f1_class_2': f1_scores[1] if len(f1_scores) > 1 else 0,
        'f1_class_3': f1_scores[2] if len(f1_scores) > 2 else 0,
        'micro_f1': micro_f1,
        'detailed_report': report
    }


def load_existing_results(output_filename: str) -> tuple:
    """Load existing results if file exists"""
    if os.path.exists(output_filename):
        try:
            with open(output_filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            results_list = existing_data.get('results', [])

            # Extract data from results list
            predictions = []
            ground_truth = []
            model_responses = []

            for result in results_list:
                predictions.append(result.get('model_prediction', 1))
                ground_truth.append(result.get('human_prediction', 1))
                model_responses.append(result.get('model_response', ''))

            print(f"Loaded existing results: {len(predictions)} predictions")
            return predictions, ground_truth, model_responses, results_list
        except Exception as e:
            print(f"Error loading existing results: {e}")

    return [], [], [], []


def save_single_result(output_filename: str, results_list: List[Dict], scenario: str, gold_statement: str,
                       sentence_1: str, sentence_2: str, human_prediction: int, model_prediction: int,
                       model_response: str):
    """Save a single result to the results list"""

    single_result = {
        'scenario': scenario,
        'gold_statement': gold_statement,
        'sentence_1': sentence_1,
        'sentence_2': sentence_2,
        'human_prediction': human_prediction,
        'model_prediction': model_prediction,
        'model_response': model_response,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    results_list.append(single_result)

    # Save the complete results
    complete_results = {
        'model_name': MODEL_NAME,
        'results': results_list,
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Ensure results directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(complete_results, f, ensure_ascii=False, indent=2)


def save_final_metrics(output_filename: str, results_list: List[Dict], metrics: Dict):
    """Save final results with metrics"""

    # Extract predictions and ground truth for metrics calculation
    predictions = [result['model_prediction'] for result in results_list]
    ground_truth = [result['human_prediction'] for result in results_list]

    complete_results = {
        'model_name': MODEL_NAME,
        'results': results_list,
        'metrics': metrics,
        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(complete_results, f, ensure_ascii=False, indent=2)


def main():
    # Read CSV file
    print("Reading CSV file...")
    df = pd.read_csv('../data/common2sense_human_annotation.csv')

    print(f"Dataset contains {len(df)} rows")
    print(f"Using model: {MODEL_NAME}")

    # Define output filename
    output_filename = f"./results/CoT_compare_results_{MODEL_NAME.replace(':', '-').replace('/', '_')}.json"

    # Load existing results
    predictions, ground_truth, model_responses, results_list = load_existing_results(output_filename)

    # Calculate starting index
    start_idx = len(predictions)
    print(f"Starting from index: {start_idx}")

    # Process data row by row
    for idx in range(start_idx, len(df)):
        print(f"Processing row {idx + 1}/{len(df)}...")

        try:
            row = df.iloc[idx]

            # Get model prediction and response
            prediction, full_response = get_model_prediction(
                scenario=row['scenario'],
                statement_1=row['statement_1'],
                statement_2=row['statement_2'],
                gold_statement=row['gold_statement'],
                sentence_1=row['sentence_1'],
                sentence_2=row['sentence_2']
            )

            predictions.append(prediction)
            ground_truth.append(int(row['human_prediction']))
            model_responses.append(full_response)

            # Save single result immediately
            save_single_result(
                output_filename=output_filename,
                results_list=results_list,
                scenario=row['scenario'],
                gold_statement=row['gold_statement'],
                sentence_1=row['sentence_1'],
                sentence_2=row['sentence_2'],
                human_prediction=int(row['human_prediction']),
                model_prediction=prediction,
                model_response=full_response
            )

            print(f"  Prediction: {prediction}, Ground Truth: {row['human_prediction']}")
            print(f"  Response length: {len(full_response)} characters")
            print(f"  Result saved immediately")

            # Add delay to avoid API rate limits
            time.sleep(0.5)

        except Exception as e:
            print(f"Error processing row {idx + 1}: {e}")
            predictions.append(1)  # Default prediction
            ground_truth.append(int(row['human_prediction']))
            model_responses.append(f"Error: {str(e)}")

            # Save error result
            save_single_result(
                output_filename=output_filename,
                results_list=results_list,
                scenario=row['scenario'],
                gold_statement=row['gold_statement'],
                sentence_1=row['sentence_1'],
                sentence_2=row['sentence_2'],
                human_prediction=int(row['human_prediction']),
                model_prediction=1,
                model_response=f"Error: {str(e)}"
            )

    # Calculate final evaluation metrics
    print("\nCalculating evaluation metrics...")
    metrics = calculate_metrics(ground_truth, predictions)

    # Print results
    print(f"\nModel: {MODEL_NAME}")
    print("=" * 50)
    print(f"F1 Score for Class 1: {metrics['f1_class_1']:.4f}")
    print(f"F1 Score for Class 2: {metrics['f1_class_2']:.4f}")
    print(f"F1 Score for Class 3: {metrics['f1_class_3']:.4f}")
    print(f"Micro Average F1 Score: {metrics['micro_f1']:.4f}")
    print("\nDetailed Classification Report:")
    print(metrics['detailed_report'])

    # Save final results with metrics
    save_final_metrics(output_filename, results_list, metrics)
    print(f"\nFinal results saved to: {output_filename}")
    print(f"Total results saved: {len(results_list)}")


if __name__ == "__main__":
    main()