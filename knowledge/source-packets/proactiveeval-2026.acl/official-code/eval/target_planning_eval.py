import os
import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tools import get_model_response
from prompt.target_planning_eval_examples import (
    persuasion_examples, 
    ambigious_instruction_examples, 
    long_term_follow_up_examples,
    system_operation_examples,
    glasses_assistant_examples,
    recommendation_examples
)
from prompt.target_planning_prompt import target_planning_eval_prompt
from config import UnifiedConfig

def clean_json_response(response):
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError:
        try:
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            
            if response.endswith("```"):
                response = response[:-3]
                
            response = response.strip()
            result = json.loads(response)
            return result
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Response content: {repr(response)}")
            raise

# 示例映射
EXAMPLES_DICT = {
    "persuasion": persuasion_examples,
    "ambigious_instruction": ambigious_instruction_examples,
    "long-term_follow_up": long_term_follow_up_examples,
    "system_operation": system_operation_examples,
    "glasses_assistant": glasses_assistant_examples,
    "recommendation": recommendation_examples
}

class TargetPlanningEvaluator:
    
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.eval_client = OpenAI(
            api_key=config.judge_model.api_key,
            base_url=config.judge_model.base_url,
            http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
        )
    
    def get_eval_response(self, prompt):
        message = get_model_response(
            self.eval_client, 
            model_name=self.config.judge_model.model_name, 
            messages=[{"role": "system", "content": prompt}],  
            temperature=self.config.judge_model.temperature, 
            eval_mode=True
        )
        # print(f"message is: {message}")
        return message

    def create_evaluation_prompt(self, result, domain_name, env_str):
        generated_target_dict = {
            "target": result["generated_target"],
            "sub_target": result["generated_sub_target"]
        }
        
        ground_truth_target_dict = {
            "target": result["target"],
            "sub_target": result["sub_target"]
        }
        
        generation_0 = json.dumps(ground_truth_target_dict)
        generation_1 = json.dumps(generated_target_dict)
        
        return target_planning_eval_prompt.format(
            trigger_description=self.config.fixed_params["domain_descriptions"][domain_name],
            env_str=env_str,
            generation_0=generation_0,
            generation_1=generation_1,
            examples=EXAMPLES_DICT[domain_name]
        )
    def evaluate_single_result(self, result, domain_name, env_str):
        prompt = self.create_evaluation_prompt(result, domain_name, env_str)
        response = self.get_eval_response(prompt)
        response = clean_json_response(response)
        print(f"response is: {response}")
        print(f"response['score'] is: {response['score']}")
            
        return {
            "environment": result["environment"],
            "target": result["target"],
            "generated_target": result["generated_target"],
            "sub_target": result["sub_target"],
            "generated_sub_target": result["generated_sub_target"],
            "score": response["score"],
            "reason": response["reason"]
        }

    def evaluate_targets(self, results, domain):
        """evaluate quality of generated targets"""
        domain_name = domain.replace("/", "_")
        if domain not in EXAMPLES_DICT:
            raise KeyError(f"Domain '{domain}' not found in EXAMPLES_DICT. Available keys: {list(EXAMPLES_DICT.keys())}")
        print(f"examples is: {EXAMPLES_DICT[domain]}")
        
        evaluated_results = []
        
        with ThreadPoolExecutor(max_workers=self.config.task_config.max_workers) as executor:
            future_tasks = []
            for result in results:
                env = result['environment']
                env_str = f"user_information: {env['user_information']}, trigger_factor: {env['trigger_factor']}"
                
                future = executor.submit(
                    self.evaluate_single_result,
                    result,
                    domain,
                    env_str
                )
                future_tasks.append(future)
            
            for future in tqdm(as_completed(future_tasks), 
                             total=len(results), 
                             desc=f"Evaluating targets for {domain}"):
                try:
                    evaluated_result = future.result()
                    evaluated_results.append(evaluated_result)
                except Exception as e:
                    print(f"Task failed with error: {e}")
        
        return evaluated_results

    def calculate_avg_metrics(self, evaluated_results):
        if not evaluated_results:
            return 0.0
        return sum(result['score'] for result in evaluated_results) / len(evaluated_results)

    def find_input_file(self, test_model_name, domain):
        file_domain_name = domain.replace("/", "_")
        
        # check target_planning_result_v1
        planning_v1_file = f"{self.config.get_output_path('target_planning')}/{test_model_name}/{file_domain_name}_v{self.config.task_config.version_num}.json"
        if os.path.exists(planning_v1_file):
            print(f"find file: {planning_v1_file}")
            return planning_v1_file
        
        # check target_planning_generation
        planning_generation_file = f"target_planning_generation/{test_model_name}/{file_domain_name}_generated_target.json"
        if os.path.exists(planning_generation_file):
            print(f"find file: {planning_generation_file}")
            return planning_generation_file
        
        return None

    def target_evaluation_by_domain(self, domains):
        """evaluate quality of generated targets by domain"""
        test_model_name = self.config.get_model_name_safe(self.config.evaluated_model.model_name)
        results_dir = Path(self.config.get_output_path("target_planning"))
        results_dir.mkdir(parents=True, exist_ok=True)
        
        all_metrics = []
        all_results = []
        
        for domain in domains:
            # find input file
            input_file = self.find_input_file(test_model_name, domain)
            output_file = results_dir / f"{domain.replace('/', '_')}_v{self.config.task_config.version_num}.json"
            
            print(f"input_file is: {input_file}")
            print(f"output_file is: {output_file}")
            print(f"\n=== Processing domain: {domain} ===")
            
            try:
                # check if input file exists
                if not input_file or not os.path.exists(input_file):
                    print(f"warning: input file not found {input_file}")
                    continue
                    
                with open(input_file, 'r', encoding='utf-8') as f:
                    generated_results = json.load(f)

                evaluated_results = self.evaluate_targets(generated_results, domain)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(evaluated_results, f, indent=4, ensure_ascii=False)
                
                avg_score = self.calculate_avg_metrics(evaluated_results)
                domain_metrics = {
                    'domain': domain,
                    'score': avg_score,
                    'count': len(evaluated_results)
                }
                all_metrics.append(domain_metrics)
                all_results.extend(evaluated_results)
                
                print(f"Results saved to {output_file}")
                print(f"domain: {domain} | Score: {avg_score:.4f} | Count: {len(evaluated_results)}")
                
            except Exception as e:
                print(f"Error processing domain {domain}: {e}")
        
        if all_results:
            total_avg_score = self.calculate_avg_metrics(all_results)
            all_metrics.append({
                'domain': 'OVERALL',
                'score': total_avg_score,
                'count': len(all_results)
            })
            
            metrics_df = pd.DataFrame(all_metrics)
            csv_file = results_dir / f"summary_v{self.config.task_config.version_num}.csv"
            metrics_df.to_csv(csv_file, index=False)
            print(f"\nMetrics summary saved to {csv_file}")
            print(f"Overall Metrics | Score: {total_avg_score:.4f} | Total Count: {len(all_results)}")
        else:
            print("No results were generated for any domain.")
        
        return all_metrics

def main():
    config = UnifiedConfig()
    
    # check if need to run target_planning evaluation task
    if config.task_config.task in ["target_planning", "all"]:
        # check if result exists
        model_name_safe = config.get_model_name_safe(config.evaluated_model.model_name)
        print(f"target_planning_generation/{model_name_safe}")
        if not os.path.exists(f"target_planning_generation/{model_name_safe}"):
            print("target_planning results not exist, please run target_generation_refactored.py first")
            return
        
        print("start target_planning evaluation task")
        evaluator = TargetPlanningEvaluator(config)
        metrics = evaluator.target_evaluation_by_domain(config.fixed_params["domains"])
    else:
        print("skip target_planning evaluation task")

if __name__ == "__main__":
    main() 