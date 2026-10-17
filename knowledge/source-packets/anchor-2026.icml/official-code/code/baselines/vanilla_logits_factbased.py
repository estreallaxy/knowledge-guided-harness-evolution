import json
import requests
import pandas as pd
from typing import Dict, List, Any, Set, Optional
import time
import logging
import os
from pathlib import Path
import re
import numpy as np
from sklearn.metrics import f1_score, classification_report

# Configure logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CommonSenseAnalyzer:
    def __init__(self, base_url: str, api_key: str, model_name: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def call_llm(self, prompt: str, temperature: float = 0.0, enable_logprobs: bool = False) -> Dict[str, Any]:
        """Call LLM API with optional logprobs"""
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": 800
        }

        # Add logprobs if requested and supported
        if enable_logprobs:
            # Try different logprobs formats for different APIs
            data["logprobs"] = True
            data["top_logprobs"] = 20

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return {"choices": [{"message": {"content": f"ERROR: {e}"}}]}

    def create_support_prompts(self, scenario: str, gold_statement: str, sentence: str) -> Dict[str, str]:
        """Create prompts to evaluate if sentence supports gold_statement in given scenario"""

        prompts = {}

        # Logits-based prompt - try a more explicit format for probability extraction
        prompts["logits"] = f"""Given the scenario and gold statement, analyze whether the sentence supports the gold statement.

Scenario: {scenario}

Gold Statement: {gold_statement}

Sentence: {sentence}

Please provide your answer as a probability between 0.0 and 1.0 that the sentence supports the gold statement.

Probability:"""

        # Direct probability prompt
        prompts["direct_prob"] = f"""Given the scenario and gold statement, analyze whether the sentence supports the gold statement.

Scenario: {scenario}

Gold Statement: {gold_statement}

Sentence: {sentence}

Please provide your confidence as a probability between 0.0 and 1.0 that the sentence supports the gold statement, where:
- 0.0 means the sentence completely contradicts or doesn't support the gold statement
- 0.5 means neutral/uncertain
- 1.0 means the sentence completely supports the gold statement

Probability:"""

        # Factor-based analysis prompt
        prompts["factor_based"] = f"""Given the scenario and gold statement, analyze whether the sentence supports the gold statement by breaking it down into 5 key factors.

Scenario: {scenario}

Gold Statement: {gold_statement}

Sentence: {sentence}

Please analyze the sentence by identifying 5 key factors/aspects that are relevant to determining support for the gold statement. For each factor, provide a probability between 0.00 and 1.00 (two decimal places) indicating how much that factor supports the gold statement.

Format your response exactly like this:

Factor 1: [Brief description of factor]
Probability: 0.XX

Factor 2: [Brief description of factor]
Probability: 0.XX

Factor 3: [Brief description of factor]
Probability: 0.XX

Factor 4: [Brief description of factor]
Probability: 0.XX

Factor 5: [Brief description of factor]
Probability: 0.XX

Average Probability: [Calculate the average of the 5 probabilities]"""

        return prompts

    def extract_probability(self, response_text: str) -> Optional[float]:
        """Extract probability from response text"""
        # Look for probability patterns
        patterns = [
            r"probability[:\s]*([0-9]*\.?[0-9]+)",
            r"confidence[:\s]*([0-9]*\.?[0-9]+)",
            r"([0-9]*\.?[0-9]+)",  # Any number
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response_text.lower())
            if matches:
                try:
                    prob = float(matches[-1])  # Take the last match
                    if 0.0 <= prob <= 1.0:
                        return prob
                    elif 0 <= prob <= 100:  # Convert percentage
                        return prob / 100.0
                except ValueError:
                    continue
        return None

    def extract_factor_probabilities(self, response_text: str) -> tuple[List[float], Optional[float]]:
        """Extract factor probabilities and average from factor-based response"""
        factor_probs = []
        avg_prob = None

        try:
            # Look for factor probabilities
            factor_pattern = r"probability[:\s]*([0-9]*\.?[0-9]+)"
            matches = re.findall(factor_pattern, response_text.lower())

            # Take first 5 matches as factor probabilities
            for match in matches[:5]:
                try:
                    prob = float(match)
                    if 0.0 <= prob <= 1.0:
                        factor_probs.append(prob)
                    elif 0 <= prob <= 100:  # Convert percentage
                        factor_probs.append(prob / 100.0)
                except ValueError:
                    continue

            # Look for average probability
            avg_pattern = r"average[:\s]*probability[:\s]*([0-9]*\.?[0-9]+)"
            avg_matches = re.findall(avg_pattern, response_text.lower())

            if avg_matches:
                try:
                    avg_prob = float(avg_matches[-1])
                    if avg_prob > 1.0 and avg_prob <= 100:  # Convert percentage
                        avg_prob = avg_prob / 100.0
                except ValueError:
                    pass

            # If no average found but we have factor probabilities, calculate it
            if avg_prob is None and len(factor_probs) > 0:
                avg_prob = sum(factor_probs) / len(factor_probs)

            # Pad factor_probs to 5 elements if needed
            while len(factor_probs) < 5:
                factor_probs.append(None)

        except Exception as e:
            logger.warning(f"Error extracting factor probabilities: {e}")

        return factor_probs[:5], avg_prob

    def extract_logits_probability(self, response: Dict[str, Any]) -> Optional[float]:
        """Extract probability from logits - fallback to text extraction if logprobs not available"""
        try:
            # Try to extract from logprobs if available
            if "choices" in response and response["choices"]:
                choice = response["choices"][0]

                # Check if logprobs are available
                if "logprobs" in choice and choice["logprobs"]:
                    logprobs_data = choice["logprobs"]

                    # Different API formats
                    if "content" in logprobs_data and logprobs_data["content"]:
                        # OpenAI format
                        for token_data in logprobs_data["content"][:5]:
                            if "top_logprobs" in token_data:
                                support_logprob = None
                                unsupport_logprob = None

                                for top_token in token_data["top_logprobs"]:
                                    token_text = top_token["token"].lower().strip()
                                    if "support" in token_text and "unsupport" not in token_text:
                                        support_logprob = top_token["logprob"]
                                    elif "unsupport" in token_text:
                                        unsupport_logprob = top_token["logprob"]

                                if support_logprob is not None and unsupport_logprob is not None:
                                    support_prob = np.exp(support_logprob)
                                    unsupport_prob = np.exp(unsupport_logprob)
                                    total_prob = support_prob + unsupport_prob
                                    return support_prob / total_prob

                    elif "token_logprobs" in logprobs_data:
                        # Alternative format
                        tokens = logprobs_data.get("tokens", [])
                        token_logprobs = logprobs_data.get("token_logprobs", [])

                        for i, token in enumerate(tokens[:5]):
                            if i < len(token_logprobs):
                                token_text = token.lower().strip()
                                if "support" in token_text and "unsupport" not in token_text:
                                    return max(0.5, np.exp(token_logprobs[i]))
                                elif "unsupport" in token_text:
                                    return min(0.5, 1.0 - np.exp(token_logprobs[i]))

                # Fallback: extract probability from response text
                response_text = choice["message"]["content"]
                return self.extract_probability(response_text)

        except Exception as e:
            logger.warning(f"Error extracting logits probability: {e}")

        return None

    def analyze_single_sentence(self, scenario: str, gold_statement: str, sentence: str, sentence_name: str) -> Dict[
        str, Any]:
        """Analyze single sentence support for gold statement"""

        prompts = self.create_support_prompts(scenario, gold_statement, sentence)
        results = {}

        for method, prompt in prompts.items():
            logger.info(f"Processing {sentence_name} - {method}")

            # For logits method, we'll try to get logprobs but fallback to text extraction
            enable_logprobs = (method == "logits")

            response = self.call_llm(prompt, enable_logprobs=enable_logprobs)

            if "choices" in response and len(response["choices"]) > 0:
                response_text = response["choices"][0]["message"]["content"]

                # Handle different method types
                if method == "logits":
                    # Try logits extraction, fallback to text extraction
                    prob = self.extract_logits_probability(response)
                    results[f"{sentence_name}_{method}_probability"] = prob

                elif method == "direct_prob":
                    # Extract probability from text
                    prob = self.extract_probability(response_text)
                    results[f"{sentence_name}_{method}_probability"] = prob

                elif method == "factor_based":
                    # Extract factor probabilities and average
                    factor_probs, avg_prob = self.extract_factor_probabilities(response_text)

                    # Store individual factor probabilities
                    for i, factor_prob in enumerate(factor_probs, 1):
                        results[f"{sentence_name}_{method}_factor{i}_probability"] = factor_prob

                    # Store average probability
                    results[f"{sentence_name}_{method}_probability"] = avg_prob

            else:
                response_text = "API call failed"
                if method == "factor_based":
                    results[f"{sentence_name}_{method}_probability"] = None
                    for i in range(1, 6):
                        results[f"{sentence_name}_{method}_factor{i}_probability"] = None
                else:
                    results[f"{sentence_name}_{method}_probability"] = None

            results[f"{sentence_name}_{method}_response"] = response_text

            # Add delay to avoid API limits
            time.sleep(1)

        return results

    def compare_probabilities(self, prob1: Optional[float], prob2: Optional[float], threshold: float = 0.01) -> int:
        """Compare two probabilities and return prediction label"""
        if prob1 is None or prob2 is None:
            return 3  # Equal (uncertain due to missing data)

        diff = abs(prob1 - prob2)
        if diff <= threshold:
            return 3  # Equal (within threshold)
        elif prob1 > prob2:
            return 1  # Sentence 1 has higher probability
        else:
            return 2  # Sentence 2 has higher probability

    def analyze_single_row(self, row: pd.Series, index: int) -> Dict[str, Any]:
        """Analyze single row from the dataset"""
        scenario = row['scenario']
        gold_statement = row['gold_statement']
        sentence_1 = row['sentence_1']
        sentence_2 = row['sentence_2']
        human_prediction = row['human_prediction']

        logger.info(f"Processing row {index}")

        results = {
            "row_index": index,
            "scenario": scenario,
            "gold_statement": gold_statement,
            "sentence_1": sentence_1,
            "sentence_2": sentence_2,
            "human_prediction": human_prediction
        }

        # Analyze sentence_1
        sentence1_results = self.analyze_single_sentence(scenario, gold_statement, sentence_1, "sentence1")
        results.update(sentence1_results)

        # Analyze sentence_2
        sentence2_results = self.analyze_single_sentence(scenario, gold_statement, sentence_2, "sentence2")
        results.update(sentence2_results)

        # Compare probabilities and make predictions
        for method in ["logits", "direct_prob", "factor_based"]:
            prob1_key = f"sentence1_{method}_probability"
            prob2_key = f"sentence2_{method}_probability"

            prob1 = results.get(prob1_key)
            prob2 = results.get(prob2_key)

            prediction = self.compare_probabilities(prob1, prob2)
            results[f"{method}_prediction"] = prediction

            # Calculate accuracy if we have valid prediction
            accuracy = 1 if prediction == human_prediction else 0
            results[f"{method}_accuracy"] = accuracy

        return results

    def get_processed_indices(self, output_path: str) -> Set[int]:
        """Get already processed row indices from existing results file"""
        if not os.path.exists(output_path):
            return set()

        try:
            existing_df = pd.read_csv(output_path, encoding='utf-8-sig')
            processed_indices = set(existing_df['row_index'].astype(int))
            logger.info(f"Found {len(processed_indices)} already processed rows in {output_path}")
            return processed_indices
        except Exception as e:
            logger.warning(f"Could not read existing results file: {e}")
            return set()

    def write_result_to_csv(self, result: Dict[str, Any], output_path: str, is_first: bool = False):
        """Write single result to CSV file"""
        df = pd.DataFrame([result])

        if is_first or not os.path.exists(output_path):
            # Write header for first result or if file doesn't exist
            df.to_csv(output_path, index=False, encoding='utf-8-sig', mode='w')
        else:
            # Append without header
            df.to_csv(output_path, index=False, encoding='utf-8-sig', mode='a', header=False)

    def analyze_dataset(self, data_path: str, output_path: str = "commonsense_analysis_results.csv"):
        """Analyze entire dataset with resume capability"""
        logger.info(f"Starting dataset analysis: {data_path}")
        logger.info(f"Results will be saved to: {output_path}")

        # Read data
        df = pd.read_csv(data_path, encoding='utf-8-sig')

        # Get already processed indices
        processed_indices = self.get_processed_indices(output_path)

        # Filter out already processed rows
        remaining_indices = [i for i in df.index if i not in processed_indices]

        logger.info(f"Total rows: {len(df)}")
        logger.info(f"Already processed: {len(processed_indices)}")
        logger.info(f"Remaining to process: {len(remaining_indices)}")

        if not remaining_indices:
            logger.info("All rows have been processed!")
            # Calculate final statistics
            self.calculate_final_statistics(output_path)
            return

        # Process remaining rows
        for i, row_idx in enumerate(tqdm(remaining_indices, desc="Processing rows")):
            row = df.iloc[row_idx]

            try:
                result = self.analyze_single_row(row, row_idx)

                # Write result immediately
                is_first_write = (len(processed_indices) == 0 and i == 0)
                self.write_result_to_csv(result, output_path, is_first_write)

                logger.info(f"✓ Completed row {row_idx}, saved to {output_path}")

            except Exception as e:
                logger.error(f"Error processing row {row_idx}: {e}")

                # Write error record
                error_result = {
                    "row_index": row_idx,
                    "scenario": row['scenario'],
                    "gold_statement": row['gold_statement'],
                    "sentence_1": row['sentence_1'],
                    "sentence_2": row['sentence_2'],
                    "human_prediction": row['human_prediction'],
                    "error": str(e)
                }

                # Add error entries for all expected columns
                for sentence in ["sentence1", "sentence2"]:
                    for method in ["logits", "direct_prob", "factor_based"]:
                        error_result[f"{sentence}_{method}_response"] = f"ERROR: {e}"
                        error_result[f"{sentence}_{method}_probability"] = None

                        # Add factor probabilities for factor_based method
                        if method == "factor_based":
                            for factor_num in range(1, 6):
                                error_result[f"{sentence}_{method}_factor{factor_num}_probability"] = None

                for method in ["logits", "direct_prob", "factor_based"]:
                    error_result[f"{method}_prediction"] = None
                    error_result[f"{method}_accuracy"] = None

                is_first_write = (len(processed_indices) == 0 and i == 0)
                self.write_result_to_csv(error_result, output_path, is_first_write)

                logger.info(f"✗ Error for row {row_idx}, saved error record to {output_path}")

        logger.info("Dataset analysis completed!")

        # Calculate final statistics
        self.calculate_final_statistics(output_path)

    def calculate_final_statistics(self, output_path: str):
        """Calculate final statistics including F1 scores for 3-class prediction"""
        if not os.path.exists(output_path):
            logger.warning("No results file found for statistics calculation")
            return

        try:
            df = pd.read_csv(output_path, encoding='utf-8-sig')
            logger.info("\n=== Final Experiment Results Statistics ===")

            methods = ["logits", "direct_prob", "factor_based"]

            for method in methods:
                prediction_col = f"{method}_prediction"

                if prediction_col not in df.columns:
                    continue

                # Get predictions and true labels
                valid_data = df.dropna(subset=[prediction_col, 'human_prediction'])

                if len(valid_data) == 0:
                    logger.info(f"{method.upper()}: No valid predictions")
                    continue

                y_true = valid_data['human_prediction'].astype(int)
                y_pred = valid_data[prediction_col].astype(int)

                # Calculate accuracy
                accuracy = (y_true == y_pred).mean()

                # Calculate F1 scores
                try:
                    # F1 scores for each class
                    f1_scores = f1_score(y_true, y_pred, labels=[1, 2, 3], average=None, zero_division=0)

                    # Micro F1 (equivalent to accuracy for multiclass)
                    micro_f1 = f1_score(y_true, y_pred, average='micro', zero_division=0)

                    # Macro F1
                    macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)

                    # Weighted F1
                    weighted_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

                    logger.info(f"{method.upper()}:")
                    logger.info(f"  Valid predictions: {len(valid_data)}/{len(df)}")
                    logger.info(f"  Overall accuracy: {accuracy:.3f}")
                    logger.info(f"  Class 1 F1: {f1_scores[0]:.3f}")
                    logger.info(f"  Class 2 F1: {f1_scores[1]:.3f}")
                    logger.info(f"  Class 3 F1: {f1_scores[2]:.3f}")
                    logger.info(f"  Micro F1: {micro_f1:.3f}")
                    logger.info(f"  Macro F1: {macro_f1:.3f}")
                    logger.info(f"  Weighted F1: {weighted_f1:.3f}")

                    # Prediction distribution
                    pred_counts = y_pred.value_counts().sort_index()
                    true_counts = y_true.value_counts().sort_index()

                    logger.info(f"  Prediction distribution:")
                    for class_label in [1, 2, 3]:
                        pred_count = pred_counts.get(class_label, 0)
                        true_count = true_counts.get(class_label, 0)
                        logger.info(f"    Class {class_label}: Predicted {pred_count}, True {true_count}")

                    # Show classification report
                    logger.info(f"  Classification Report:")
                    report = classification_report(y_true, y_pred, labels=[1, 2, 3],
                                                   target_names=['Class 1', 'Class 2', 'Class 3'],
                                                   zero_division=0)
                    for line in report.split('\n'):
                        if line.strip():
                            logger.info(f"    {line}")

                except Exception as e:
                    logger.error(f"Error calculating F1 scores for {method}: {e}")

                # Show average probabilities for each sentence
                for sentence in ["sentence1", "sentence2"]:
                    prob_col = f"{sentence}_{method}_probability"
                    if prob_col in df.columns:
                        valid_probs = df[prob_col].dropna()
                        if len(valid_probs) > 0:
                            avg_prob = valid_probs.mean()
                            std_prob = valid_probs.std()
                            logger.info(f"  {sentence} probability - Mean: {avg_prob:.3f}, Std: {std_prob:.3f}")

                # For factor_based method, show average factor probabilities
                if method == "factor_based":
                    logger.info(f"  Factor analysis for {method.upper()}:")
                    for sentence in ["sentence1", "sentence2"]:
                        factor_probs = []
                        for factor_num in range(1, 6):
                            factor_col = f"{sentence}_{method}_factor{factor_num}_probability"
                            if factor_col in df.columns:
                                valid_factor_probs = df[factor_col].dropna()
                                if len(valid_factor_probs) > 0:
                                    avg_factor_prob = valid_factor_probs.mean()
                                    factor_probs.append(avg_factor_prob)
                                    logger.info(f"    {sentence} Factor {factor_num} avg: {avg_factor_prob:.3f}")

                        if factor_probs:
                            overall_factor_avg = sum(factor_probs) / len(factor_probs)
                            logger.info(f"    {sentence} Overall factor avg: {overall_factor_avg:.3f}")

        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")


def main():
    """Main function for complete analysis"""
    # Configuration parameters
    BASE_URL = ""
    API_KEY = ""
    MODEL_NAME = ""
    DATA_PATH = "common2sense_human_annotation.csv"
    OUTPUT_PATH = f"commonsense_analysis_results_{MODEL_NAME.replace(':','-')}.csv"

    logger.info("=== CommonSense Analysis Started ===")
    logger.info(f"Base URL: {BASE_URL}")
    logger.info(f"Model: {MODEL_NAME}")
    logger.info(f"Input: {DATA_PATH}")
    logger.info(f"Output: {OUTPUT_PATH}")

    # Create analyzer
    analyzer = CommonSenseAnalyzer(BASE_URL, API_KEY, MODEL_NAME)

    # Run analysis with resume capability
    analyzer.analyze_dataset(DATA_PATH, OUTPUT_PATH)

    logger.info("=== Analysis Completed ===")


if __name__ == "__main__":
    main()