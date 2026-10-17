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

    # Create the few-shot messages for thinking-then-probability approach
    messages = [
        {
            "role": "system",
            "content": """You are a decision-making assistant. Given a scenario and an outcome, you need to evaluate two conditions and determine which one makes the outcome more likely.

First, think through the reasoning step by step, then assign probabilities to each condition indicating how likely they make the outcome.

Your response must be in this exact format:
Thinking: [Your step-by-step reasoning process]
P(Condition 1): [probability between 0 and 1]
P(Condition 2): [probability between 0 and 1]
Decision: [Choose the condition with higher probability, or "Both" if probabilities are equal within 0.05]

For example:
Thinking: Let me analyze this step by step. First, I need to understand what makes marathon performance better. Endurance runs build aerobic capacity and stamina, which are crucial for long-distance running. Speed workouts improve anaerobic capacity and running economy. For marathon performance specifically, endurance is more critical because marathons are primarily aerobic events. Condition 1 provides general knowledge but lacks specific evidence. Condition 2 provides concrete research evidence showing endurance training is more effective for marathon performance. The study specifically mentions improvements in aerobic capacity and muscular endurance, which are exactly what marathon runners need.
P(Condition 1): 0.4
P(Condition 2): 0.9
Decision: Condition 2"""
        },
        {
            "role": "user",
            "content": "Scenario: Alex is training for a marathon and is deciding whether to focus more on endurance runs or speed workouts.\nOutcome: Since Alex wants to maximize his marathon performance, he decides to prioritize endurance runs over speed workouts.\nCondition 1: Alex understands that long-distance runners typically incorporate endurance runs into their training routines.\nCondition 2: Alex reads a study showing that endurance training significantly improves marathon performance by increasing aerobic capacity and muscular endurance more effectively than speed workouts."
        },
        {
            "role": "assistant",
            "content": "Thinking: Let me analyze this step by step. First, I need to understand what makes marathon performance better. Endurance runs build aerobic capacity and stamina, which are crucial for long-distance running. Speed workouts improve anaerobic capacity and running economy. For marathon performance specifically, endurance is more critical because marathons are primarily aerobic events. Condition 1 provides general knowledge but lacks specific evidence. Condition 2 provides concrete research evidence showing endurance training is more effective for marathon performance. The study specifically mentions improvements in aerobic capacity and muscular endurance, which are exactly what marathon runners need.\nP(Condition 1): 0.4\nP(Condition 2): 0.9\nDecision: Condition 2"
        },
        {
            "role": "user",
            "content": "Scenario: Liam is deciding whether to carry an umbrella before leaving for work.\nOutcome: Since Liam wants to avoid getting wet, he decides to bring an umbrella.\nCondition 1: Liam checks the weather forecast and sees that rain is expected today.\nCondition 2: Liam sees that the forecast predicts precipitation throughout the day."
        },
        {
            "role": "assistant",
            "content": "Thinking: Let me think through this carefully. Both conditions are about weather forecasting, but I need to consider if they provide different levels of information. Condition 1 mentions 'rain is expected today' while Condition 2 mentions 'precipitation throughout the day'. Rain and precipitation are essentially the same thing - precipitation is just a more formal term for rain. Both conditions convey the same information: there will be rain today. Since both provide identical information about the weather, they should have the same probability of leading to the decision to bring an umbrella.\nP(Condition 1): 0.85\nP(Condition 2): 0.85\nDecision: Both"
        },
        {
            "role": "user",
            "content": "Scenario: Emma is choosing between two restaurants for dinner.\nOutcome: Emma decides to go to Restaurant A for dinner.\nCondition 1: Emma sees that Restaurant A has good reviews online.\nCondition 2: Emma hears from a friend that Restaurant A has good food."
        },
        {
            "role": "assistant",
            "content": "Thinking: Let me analyze this step by step. Both conditions provide positive information about Restaurant A, but they come from different sources. Condition 1 mentions online reviews, which can be helpful but may not always be reliable or personal. Condition 2 mentions a friend's recommendation, which provides a personal endorsement but may be subjective. Both sources have their merits - online reviews give broader consensus while friend recommendations provide trusted personal experience. Since both conditions equally support the decision to choose Restaurant A and neither provides significantly stronger evidence than the other, they should have equal probabilities.\nP(Condition 1): 0.5\nP(Condition 2): 0.5\nDecision: Both"
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
            temperature=0.1,
            max_tokens=500  # Increased for thinking process
        )

        result = response.choices[0].message.content.strip()

        # Parse the result to extract thinking, probabilities and decision
        lines = result.split('\n')
        prob_1 = 0.0
        prob_2 = 0.0
        prediction = 1  # Default prediction
        thinking = ""

        for line in lines:
            line = line.strip()
            if line.startswith('Thinking:'):
                thinking = line.replace('Thinking:', '').strip()
            elif line.startswith('P(Condition 1):'):
                try:
                    prob_1 = float(line.split(':')[1].strip())
                except:
                    prob_1 = 0.0
            elif line.startswith('P(Condition 2):'):
                try:
                    prob_2 = float(line.split(':')[1].strip())
                except:
                    prob_2 = 0.0
            elif line.startswith('Decision:'):
                decision_part = line.replace('Decision:', '').strip().lower()
                if 'condition 1' in decision_part or 'statement 1' in decision_part:
                    prediction = 1
                elif 'condition 2' in decision_part or 'statement 2' in decision_part:
                    prediction = 2
                elif 'both' in decision_part:
                    prediction = 3

        # If no clear decision found, use probability comparison
        if prediction == 1:  # Default case, check probabilities
            if abs(prob_1 - prob_2) < 0.05:  # Within 0.05 threshold
                prediction = 3  # Both
            elif prob_1 > prob_2:
                prediction = 1  # Condition 1
            else:
                prediction = 2  # Condition 2

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
    df = pd.read_csv('common2sense_human_annotation.csv')

    print(f"Dataset contains {len(df)} rows")
    print(f"Using model: {MODEL_NAME}")

    # Define output filename
    output_filename = f"./results/thinking_probability_results_{MODEL_NAME.replace(':', '-').replace('/', '_')}.json"

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