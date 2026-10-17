import os
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import httpx
from openai import OpenAI
from tqdm import tqdm
from tools import get_model_response
from prompt.conversation_eval_prompt import (
    Guidance_Acc_evaluation_input_prompt,
    Guidance_Acc_evaluation_prompt_short
)
from config import UnifiedConfig

@dataclass
class EvaluationResult:
    environment: Dict[str, Any]
    target: str
    sub_target: List[str]
    conversation: List[Dict[str, Any]]
    guidance: Dict[str, Any]
    collaboration_type: str

class JSONResponseParser:
    @staticmethod
    def clean_json_response(response: str) -> Dict[str, Any]:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return JSONResponseParser._clean_and_parse(response)
    
    @staticmethod
    def _clean_and_parse(response: str) -> Dict[str, Any]:
        try:
            # remove markdown code block
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            
            if response.endswith("```"):
                response = response[:-3]
                
            response = response.strip()
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Response content: {repr(response)}")
            raise

class GuidanceEvaluator:
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.judge_model.api_key,
            base_url=config.judge_model.base_url,
            http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
        )
    
    def evaluate_guidance(
        self, 
        environment: Dict[str, Any], 
        conversation: List[Dict[str, Any]], 
        target: str, 
        sub_target: List[str], 
        file_domain: str
    ) -> Dict[str, Any]:
        for attempt in range(self.config.fixed_params["max_attempts"]):
            try:
                prompt = self._build_prompt(environment, conversation, target, sub_target)
                response = self._get_model_response(prompt)
                parsed_response = JSONResponseParser.clean_json_response(response)
                
                return {
                    "guidance": {
                        "thought": parsed_response["thought"],
                        "score": parsed_response["score"]
                    }
                }
            except Exception as e:
                if attempt == self.config.fixed_params["max_attempts"] - 1:
                    return {
                        "guidance": {
                            "score": 0, 
                            "thought": f"Failed to parse response: {str(e)}"
                        }
                    }
                print(f"Error parsing response, attempt {attempt + 1}: {e}")
        
        return {"guidance": {"score": 0, "thought": "All attempts failed"}}
    
    def _get_model_response(self, prompt: str) -> str:
        return get_model_response(
            self.client,
            model_name=self.config.judge_model.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.judge_model.temperature,
            eval_mode=True
        )
    
    def _build_prompt(
        self, 
        environment: Dict[str, Any], 
        conversation: List[Dict[str, Any]], 
        target: str, 
        sub_target: List[str]
    ) -> str:
        return (
            Guidance_Acc_evaluation_prompt_short + '\n' + 
            Guidance_Acc_evaluation_input_prompt.format(
                user_information=environment["user_information"],
                trigger_factor=environment["trigger_factor"],
                conversation=conversation,
                target=target,
                sub_target=sub_target
            )
        )

class ConversationEvaluator:
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.guidance_evaluator = GuidanceEvaluator(config)
    
    def evaluate_conversations(
        self, 
        input_path: str, 
        output_path: str, 
        file_domain: str
    ) -> List[EvaluationResult]:
        data = self._load_data(input_path)
        results = self._process_conversations(data, file_domain)
        self._save_results(results, output_path)
        return results
    
    def _load_data(self, input_path: str) -> List[Dict[str, Any]]:
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _process_conversations(
        self, 
        data: List[Dict[str, Any]], 
        file_domain: str
    ) -> List[EvaluationResult]:
        results = []
        
        def process_item(item: Dict[str, Any]) -> EvaluationResult:
            conversation = item.get('conversation', [])
            environment = item.get('environment', {})
            target = item.get('target', '')
            sub_target = item.get('sub_target', [])
            collaboration_type = item.get('collaboration_type', '')
            
            guidance_scores = self.guidance_evaluator.evaluate_guidance(
                environment, conversation, target, sub_target, file_domain
            )
            
            return EvaluationResult(
                environment=environment,
                target=target,
                sub_target=sub_target,
                conversation=conversation,
                guidance=guidance_scores['guidance'],
                collaboration_type=collaboration_type
            )
        
        with ThreadPoolExecutor(max_workers=self.config.task_config.max_workers) as executor:
            futures = [executor.submit(process_item, item) for item in data]
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Evaluating conversations"):
                results.append(future.result())
        
        return results
    
    def _save_results(self, results: List[EvaluationResult], output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        results_dict = [
            {
                "environment": result.environment,
                "target": result.target,
                "sub-target": result.sub_target,
                "conversation": result.conversation,
                "guidance": result.guidance,
                "collaboration_type": result.collaboration_type
            }
            for result in results
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=4, ensure_ascii=False)
        
        print(f"Results saved to {output_path}")
    
    def _save_combined_results(self, all_results: List[EvaluationResult], output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        results_dict = [
            {
                "environment": result.environment,
                "target": result.target,
                "sub-target": result.sub_target,
                "conversation": result.conversation,
                "guidance": result.guidance,
                "collaboration_type": result.collaboration_type
            }
            for result in all_results
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=4, ensure_ascii=False)
        
        print(f"Combined results saved to {output_path}")

class MetricsCalculator:
    @staticmethod
    def calculate_domain_metrics(results: List[EvaluationResult]) -> Dict[str, float]:
        valid_results = [
            result for result in results 
            if isinstance(result.guidance, dict) and 'score' in result.guidance
        ]
        
        if not valid_results:
            return {"avg_guidance": 0, "avg_turns": 0, "valid_convs": 0}
        
        total_guidance = sum(result.guidance['score'] for result in valid_results)
        total_turns = sum(len(result.conversation) for result in valid_results)
        
        return {
            "avg_guidance": total_guidance / len(valid_results),
            "avg_turns": total_turns / len(valid_results),
            "valid_convs": len(valid_results)
        }
    
    @staticmethod
    def save_metrics_summary(
        domain_metrics: List[tuple], 
        overall_metrics: Dict[str, float], 
        csv_path: str
    ) -> None:
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("domain,Average Guidance,Average Turns,Number of Conversations\n")
            for domain, guidance, turns, convs in domain_metrics:
                f.write(f"{domain},{guidance:.4f},{turns:.2f},{convs}\n")
            f.write(f"Overall,{overall_metrics['avg_guidance']:.4f},{overall_metrics['avg_turns']:.2f},{overall_metrics['valid_convs']}\n")
        
        print(f"Metrics summary saved to {csv_path}")
    
    @staticmethod
    def calculate_collaboration_type_metrics(results: List[EvaluationResult]) -> Dict[str, Dict[str, float]]:
        valid_results = [
            result for result in results 
            if isinstance(result.guidance, dict) and 'score' in result.guidance
        ]
        
        if not valid_results:
            return {}
        
        # group by collaboration_type
        type_groups = {}
        for result in valid_results:
            collab_type = result.collaboration_type
            if collab_type not in type_groups:
                type_groups[collab_type] = []
            type_groups[collab_type].append(result)
        
        # calculate metrics for each type
        type_metrics = {}
        for collab_type, type_results in type_groups.items():
            total_guidance = sum(result.guidance['score'] for result in type_results)
            total_turns = sum(len(result.conversation) for result in type_results)
            
            type_metrics[collab_type] = {
                "avg_guidance": total_guidance / len(type_results),
                "avg_turns": total_turns / len(type_results),
                "valid_convs": len(type_results)
            }
        
        return type_metrics
    
    @staticmethod
    def save_collaboration_type_metrics_summary(
        type_metrics: Dict[str, Dict[str, float]], 
        csv_path: str
    ) -> None:
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("Collaboration Type,Average Guidance,Average Turns,Number of Conversations\n")
            # sort by order: High, Mid, Low
            order = ['High', 'Mid', 'Low']
            for collab_type in order:
                if collab_type in type_metrics:
                    metrics = type_metrics[collab_type]
                    f.write(f"{collab_type},{metrics['avg_guidance']:.4f},{metrics['avg_turns']:.2f},{metrics['valid_convs']}\n")
            
            for collab_type, metrics in type_metrics.items():
                if collab_type not in order:
                    f.write(f"{collab_type},{metrics['avg_guidance']:.4f},{metrics['avg_turns']:.2f},{metrics['valid_convs']}\n")
        
        print(f"Collaboration type metrics summary saved to {csv_path}")

def main():
    config = UnifiedConfig()
    
    # check if need to run dialogue_guidance evaluation task
    if config.task_config.task in ["dialogue_guidance", "all"]:
        # check if result exists
        model_name_safe = config.get_model_name_safe(config.evaluated_model.model_name)
        if not os.path.exists(f"conversation_results/{model_name_safe}"):
            print("dialogue_guidance results not exist, please run conversation_generation_refactored.py first")
            return
        
        print("start dialogue_guidance evaluation task")
        
        evaluator = ConversationEvaluator(config)
        metrics_calculator = MetricsCalculator()
        domain_metrics = []
        all_results = []
        total_guidance = 0
        total_turns = 0
        total_convs = 0
    
        for domain in config.fixed_params["domains"]:
            file_domain = domain.replace("/", "_")
            model_name_safe = config.get_model_name_safe(config.evaluated_model.model_name)
            input_path = f"conversation_results/{model_name_safe}/{file_domain}.json"
            output_path = f"{config.get_output_path('dialogue_guidance')}/{file_domain}_v{config.task_config.version_num}.json"
            
            try:
                results = evaluator.evaluate_conversations(input_path, output_path, file_domain)
                all_results.extend(results)
                
                # calculate domain metrics
                metrics = metrics_calculator.calculate_domain_metrics(results)
                
                if metrics["valid_convs"] > 0:
                    domain_metrics.append([
                        domain, 
                        metrics["avg_guidance"], 
                        metrics["avg_turns"], 
                        metrics["valid_convs"]
                    ])
                    
                    total_guidance += metrics["avg_guidance"] * metrics["valid_convs"]
                    total_turns += metrics["avg_turns"] * metrics["valid_convs"]
                    total_convs += metrics["valid_convs"]
                    
                    print(f"Domain {domain}: avg_guidance={metrics['avg_guidance']:.4f}, avg_turns={metrics['avg_turns']:.2f}, convs={metrics['valid_convs']}")
            
            except Exception as e:
                print(f"Error processing domain {domain}: {e}")
                continue
        
        combined_output_path = f"{config.get_output_path('dialogue_guidance')}/dialogue_guidance_v_{config.task_config.version_num}.json"
        evaluator._save_combined_results(all_results, combined_output_path)
        
        overall_metrics = {
            "avg_guidance": total_guidance / total_convs if total_convs > 0 else 0,
            "avg_turns": total_turns / total_convs if total_convs > 0 else 0,
            "valid_convs": total_convs
        }
        
        csv_path = f"{config.get_output_path('dialogue_guidance')}/metrics_summary.csv"
        metrics_calculator.save_metrics_summary(domain_metrics, overall_metrics, csv_path)
        
        type_metrics = metrics_calculator.calculate_collaboration_type_metrics(all_results)
        collaboration_csv_path = f"{config.get_output_path('dialogue_guidance')}/collaboration_type_metrics_summary.csv"
        metrics_calculator.save_collaboration_type_metrics_summary(type_metrics, collaboration_csv_path)
        
        print(f"\nOverall metrics: avg_guidance={overall_metrics['avg_guidance']:.4f}, avg_turns={overall_metrics['avg_turns']:.2f}, total_convs={overall_metrics['valid_convs']}")
        
        print("\nCollaboration Type Metrics:")
        for collab_type, metrics in type_metrics.items():
            print(f"{collab_type}: avg_guidance={metrics['avg_guidance']:.4f}, avg_turns={metrics['avg_turns']:.2f}, convs={metrics['valid_convs']}")
    else:
        print("skip dialogue_guidance evaluation task")

if __name__ == "__main__":
    main() 