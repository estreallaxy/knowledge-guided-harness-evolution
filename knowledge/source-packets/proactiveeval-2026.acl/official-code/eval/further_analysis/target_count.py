
import json
import os
import csv
import httpx
import re
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging
from typing import List, Dict, Any
from pathlib import Path
# New import for robust retries
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5),
    reraise=True 
)
def get_model_response(client, model_name, messages, temperature=0.0, eval_mode=False):
    logger.debug(f"Requesting response from {model_name}")
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=100 if eval_mode else 1000,
        timeout=30.0, # prevent too long response
    )
    return response.choices[0].message.content


def _clean_and_parse(response: str) -> Dict[str, Any]:
    try:
        match = re.search(r'```json\s*(\{.*\}|\[.*\])\s*```', response, re.DOTALL)
        if match:
            response = match.group(1)
        else:
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

        response = response.strip()
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.error(f"Response content that failed parsing: {repr(response)}")
        raise

class TargetDensityEvaluator:
    INPUT_BASE_DIR = Path("../dialogue_guidance_v1")
    OUTPUT_BASE_DIR = Path("target_density")

    def __init__(self, max_workers: int = 20, eval_model: str = "deepseek-chat"):
        self.max_workers = max_workers
        self.eval_model = eval_model
      
        # Ensure output directory exists
        self.OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)

        self.client = OpenAI(
            api_key="",
            base_url="",
            http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
        )

    def count_sub_targets_in_message(self, sub_targets: List[str], message: str) -> int:
        prompt = f"""<Task>
You need to analyze the sub-targets that appear in the messages and count the number of targets that appear.
</Task>
<Sub-targets>
{sub_targets}
</Sub-targets>
<Message>
message: {message}
</Message>
<Rule>
Return only in JSON format: {{"count": (the number of sub-targets appeared in the message)}}
</Rule>
"""
        messages = [{"role": "system", "content": prompt}]

        try:
            response_text = get_model_response(
                client=self.client,
                model_name=self.eval_model,
                messages=messages,
                is_gpt=self.is_gpt,
                temperature=0.0,
                eval_mode=True
            )
            result = _clean_and_parse(response_text)
            return result.get("count", 0)
        except RetryError as e:
            logger.error(f"API call failed after multiple retries: {e}")
            logger.error(f"Message content that failed: {repr(message[:100])}...")
            return 0 # Return 0 if all retries fail
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing message: {e}")
            logger.error(f"Message content that failed: {repr(message[:100])}...")
            return 0

    def process_single_conversation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """process a single conversation"""
        sub_targets = data["sub-target"]
        conversation = data["conversation"]

        assistant_messages = [msg["content"] for msg in conversation if msg["role"] == "assistant"]

        if not assistant_messages:
            return {
                "target": data["target"],
                "target_dense": 0,
                "collaboration_type": data.get("collaboration_type", "Unknown"),
            }

        counts = [self.count_sub_targets_in_message(sub_targets, msg) for msg in assistant_messages]

        all_count = sum(counts)
        turns = len(conversation) // 2
        target_dense = all_count / turns if turns > 0 else 0

        result = {
            "target": data["target"],
            "target_dense": target_dense,
            "collaboration_type": data.get("collaboration_type", "Unknown")
        }
        for i, count in enumerate(counts):
            result[f"message_{i+1}"] = count

        return result

    def process_model_data(self, model_name: str) -> Dict[str, Any]:
        """process all data for a single model."""
        input_path = self.INPUT_BASE_DIR / model_name / "dialogue_guidance_v_1.json"

        if not input_path.exists():
            logger.warning(f"File not found: {input_path}")
            return {"model_name": model_name, "results": [], "avg_target_dense": 0}

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data_list = json.load(f)

            logger.info(f"Processing {len(data_list)} conversations for model {model_name}")

            results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_item = {executor.submit(self.process_single_conversation, item): item for item in data_list}
              
                for future in tqdm(as_completed(future_to_item), total=len(data_list), desc=f"Evaluating {model_name}"):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        item = future_to_item[future]
                        logger.error(f"Error processing conversation for target '{item.get('target', 'Unknown')}': {e}")
                        results.append({"target": item.get('target', 'Unknown'), "target_dense": 0, "collaboration_type": "Error"})

            valid_densities = [r["target_dense"] for r in results if "target_dense" in r]
            avg_target_dense = sum(valid_densities) / len(valid_densities) if valid_densities else 0

            return {
                "model_name": model_name,
                "results": results,
                "avg_target_dense": avg_target_dense
            }
        except Exception as e:
            logger.error(f"Failed to process model file {input_path}: {e}")
            return {"model_name": model_name, "results": [], "avg_target_dense": 0}

    def save_results(self, model_name: str, results: List[Dict[str, Any]]):
        output_dir = self.OUTPUT_BASE_DIR / model_name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "target_count.json"

        output_data = [{
            "target": result["target"],
            "counts": {k: v for k, v in result.items() if k.startswith("message_")},
            "collaboration_type": result["collaboration_type"]
        } for result in results]

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Results for {model_name} saved to {output_path}")

    def update_csv_summary(self, model_results: List[Dict[str, Any]]):
        csv_path = self.OUTPUT_BASE_DIR / "target_density_summary.csv"
      
        existing_data = {}
        if csv_path.exists():
            try:
                with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_data[row["model_name"]] = row
            except Exception as e:
                logger.warning(f"Could not read existing CSV file at {csv_path}. A new one will be created. Error: {e}")

        for model_result in model_results:
            existing_data[model_result["model_name"]] = {
                "model_name": model_result["model_name"],
                "avg_target_dense": f"{model_result['avg_target_dense']:.4f}",
                "total_conversations": len(model_result["results"])
            }

        sorted_data = sorted(existing_data.values(), key=lambda x: x["model_name"])
      
        if not sorted_data:
            logger.warning("No data to write to CSV summary.")
            return

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["model_name", "avg_target_dense", "total_conversations"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sorted_data)
        logger.info(f"CSV summary updated at {csv_path}")

    def get_available_models(self) -> List[str]:
        if not self.INPUT_BASE_DIR.exists():
            return []
      
        return [
            item.name for item in self.INPUT_BASE_DIR.iterdir() 
            if item.is_dir() and (item / "dialogue_guidance_v_1.json").exists()
        ]

    def run(self, model_names: List[str] = None):
        if model_names is None:
            model_names = self.get_available_models()
      
        if not model_names:
            logger.error(f"No models found in {self.INPUT_BASE_DIR}. Please check the directory structure.")
            return
      
        logger.info(f"Found {len(model_names)} models to process: {model_names}")
        logger.info(f"Using evaluation model: {self.eval_model} (is_gpt: {self.is_gpt})")
        logger.info(f"Concurrency level (max_workers): {self.max_workers}")

        all_model_results = []
        for i, model_name in enumerate(model_names):
            logger.info(f"\n--- Processing model {i+1}/{len(model_names)}: {model_name} ---")
            result = self.process_model_data(model_name)
          
            if result["results"]:
                self.save_results(result["model_name"], result["results"])
                all_model_results.append(result)
            else:
                logger.warning(f"No results were generated for model {result['model_name']}. Skipping save and summary.")
          
            # Add a delay between processing models to prevent rate limit
            if i < len(model_names) - 1: # Not sleep in the last model
                logger.info(f"Pausing for 5 seconds before processing the next model...")
                time.sleep(5)

        if all_model_results:
            self.update_csv_summary(all_model_results)
            logger.info("\n=== Final Processing Summary ===")
            for model_result in all_model_results:
                logger.info(
                    f"Model: {model_result['model_name']:<30} | "
                    f"Conversations: {len(model_result['results']):<5} | "
                    f"Avg Target Density: {model_result['avg_target_dense']:.4f}"
                )
        else:
            logger.info("Processing complete, but no model results were generated.")


if __name__ == "__main__":
    evaluator = TargetDensityEvaluator(
        max_workers=30,
        eval_model="deepseek-chat"
    )
  
    model_names_to_run = ["qwen_qwen3-235b-a22b-07-25"]
    evaluator.run(model_names_to_run)

