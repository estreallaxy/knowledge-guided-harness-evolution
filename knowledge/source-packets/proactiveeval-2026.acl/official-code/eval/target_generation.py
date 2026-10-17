import os
import re
import json
import logging
import httpx
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tools import get_model_response
from config import UnifiedConfig
from prompt.target_planning_prompt import target_generation_prompt
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseParser:
    
    @staticmethod
    def extract_json_from_code_block(response: str) -> str:
        if "```json" in response:
            return response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            return response.split("```")[1].split("```")[0].strip()
        return response
    
    @staticmethod
    def parse_json_safely(json_str: str) -> Optional[Dict]:
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return None
    
    @staticmethod
    def extract_with_regex(response: str, pattern: str, group: int = 1) -> Optional[str]:
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        return match.group(group) if match else None
    
    @classmethod
    def transform_response_to_target(cls, response: Any) -> Tuple[str, List[str]]:
        try:
            if isinstance(response, dict):
                target = response.get("Target", "")
                sub_targets = response.get("sub_targets", [])
                if isinstance(sub_targets, list):
                    sub_targets = [str(item) for item in sub_targets]
                else:
                    sub_targets = []
                return target, sub_targets
            
            if isinstance(response, str):
                cleaned_response = cls.extract_json_from_code_block(response)
                
                # parse json
                parsed = cls.parse_json_safely(cleaned_response)
                if parsed:
                    target = parsed.get("Target", "")
                    sub_targets = parsed.get("sub_targets", [])
                    
                    # handle nested json
                    if isinstance(target, str) and target.startswith("{"):
                        inner_parsed = cls.parse_json_safely(target)
                        if inner_parsed and "Target" in inner_parsed:
                            inner_target = inner_parsed["Target"]
                            inner_sub_targets = inner_parsed.get("sub_targets", [])
                            # ensure sub_targets is a list of strings
                            if isinstance(inner_sub_targets, list):
                                inner_sub_targets = [str(item) for item in inner_sub_targets]
                            else:
                                inner_sub_targets = []
                            return inner_target, inner_sub_targets
                    if isinstance(sub_targets, list):
                        sub_targets = [str(item) for item in sub_targets]
                    else:
                        sub_targets = []
                    return target, sub_targets
                
                # use regex as fallback
                target = cls.extract_with_regex(cleaned_response, r'"Target"\s*:\s*"([^"]+)"')
                sub_targets_str = cls.extract_with_regex(cleaned_response, r'"sub_targets"\s*:\s*(\[.*?\])')
                
                sub_targets = []
                if sub_targets_str:
                    sub_targets_parsed = cls.parse_json_safely(sub_targets_str)
                    if isinstance(sub_targets_parsed, list):
                        sub_targets = [str(item) for item in sub_targets_parsed]
                
                return target or "", sub_targets
            
            return "", []
            
        except Exception as e:
            logger.error(f"parse response failed: {e}")
            return "", []

class TargetGenerator:
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.evaluated_model.api_key,
            base_url=config.evaluated_model.base_url,
            http_client=httpx.Client(proxy=os.environ.get("HTTP_PROXY", ""))
        )
        self.parser = ResponseParser()
    
    def generate_response(self, prompt: str) -> str:
        logger.info(f"request model: {self.config.evaluated_model.model_name}")
        return get_model_response(
            self.client,
            model_name=self.config.evaluated_model.model_name,
            messages=[{"role": "system", "content": prompt}],
            temperature=self.config.evaluated_model.temperature,
            eval_mode=True
        )
        
    
    def process_single_item(self, item: Dict, domain: str, trigger_description: str) -> Dict:
        # generate one target and sub_targets
        try:
            env = item["item"]["environment"]
            env_str = f"user_information: {env['user_information']}, trigger_factor: {env['trigger_factor']}"
            ground_truth_target = item["item"]["target"]
            ground_truth_subtarget = item["item"]["sub_target"]
            
            prompt = target_generation_prompt.format(env_str=env_str, trigger_description=trigger_description)
            
            generated_target, generated_subtarget = "", []
            
            for attempt in range(self.config.fixed_params["max_retries"]):
                try:
                    response = self.generate_response(prompt)
                    logger.debug(f"response: {response}")
                    
                    generated_target, generated_subtarget = self.parser.transform_response_to_target(response)
                    
                    if generated_subtarget:
                        break
                        
                except Exception as e:
                    logger.warning(f"attempt {attempt + 1} failed: {e}")
                    continue
            
            # clean invalid target
            if generated_target == "{\\" or not generated_target:
                generated_target = "None"
            
            return {
                "environment": env,
                "target": ground_truth_target,
                "generated_target": generated_target,
                "sub_target": ground_truth_subtarget,
                "generated_sub_target": generated_subtarget
            }
            
        except Exception as e:
            logger.error(f"error: {e}")
            return {}

class TargetGenerationPipeline:    
    def __init__(self, config: UnifiedConfig):
        self.config = config
        self.generator = TargetGenerator(config)
    
    def process_domain(self, domain_config: Dict) -> List[Dict]:
        logger.info(f"process domain: {domain_config['name']}")
        
        # check input file
        if not os.path.exists(domain_config['input_file']):
            logger.warning(f"input file not found: {domain_config['input_file']}")
            return []
        
        # load data
        try:
            with open(domain_config['input_file'], 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"load data failed: {e}")
            return []
        
        # parallel processing
        results = []
        with ThreadPoolExecutor(max_workers=self.config.task_config.max_workers) as executor:
            futures = [
                executor.submit(
                    self.generator.process_single_item,
                    item,
                    domain_config['name'],
                    domain_config['trigger_description']
                )
                for item in data
            ]
            
            for future in tqdm(futures, desc=f"generate target - {domain_config['name']}"):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"error: {e}")
        
        return results
    
    def save_results(self, results: List[Dict], output_file: str):
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            
            logger.info(f"results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"save results failed: {e}")
    
    def run(self, domains: List[str], eval_difficulty: str = "all"):
        logger.info(f"run target generation pipeline, domains: {domains}, eval_difficulty: {eval_difficulty}")
        
        for domain in domains:
            try:
                domain_config = self.config.get_domain_config(domain, eval_difficulty)
                
                # build output file path
                model_name_safe = self.config.get_model_name_safe(self.config.evaluated_model.model_name)
                if eval_difficulty == "all":
                    output_filename = f"{domain}_generated_target.json"
                else:
                    output_filename = f"{domain}_generated_target_{eval_difficulty}.json"
                
                output_path = f"target_planning_generation/{model_name_safe}"
                output_file = f"{output_path}/{output_filename}"
                
                results = self.process_domain(domain_config)
                
                if results:
                    self.save_results(results, output_file)
                    logger.info(f"domain {domain} processed, generated {len(results)} results")
                else:
                    logger.warning(f"domain {domain} generated no results")
                    
            except Exception as e:
                logger.error(f"error: {e}")

def main():
    config = UnifiedConfig()
    
    # check if need to run target_planning task
    if config.task_config.task in ["target_planning", "all"]:
        model_name_safe = config.get_model_name_safe(config.evaluated_model.model_name)
        if not os.path.exists(f"target_planning_generation/{model_name_safe}"):
            logger.info("start target_planning task, generate target and sub_targets now")
            # create pipeline
            pipeline = TargetGenerationPipeline(config)
            # run pipeline
            pipeline.run(config.fixed_params["domains"], "all")
        else:
            logger.info("target_planning results already exist, skip generation task")
    else:
        logger.info("skip target_planning task")

if __name__ == "__main__":
    main() 