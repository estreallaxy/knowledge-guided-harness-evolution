import yaml
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class ModelConfig:
    api_key: str
    base_url: str
    model_name: str
    temperature: float

@dataclass
class TaskConfig:
    task: str
    output_folder_name: Dict[str, str]
    version_num: int
    max_workers: int

class UnifiedConfig:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # parse config
        self.evaluated_model = ModelConfig(**self.config["evaluated_model"])
        self.judge_model = ModelConfig(**self.config["judge_model"])
        self.task_config = TaskConfig(
            task=self.config["task"],
            output_folder_name=self.config["output_folder_name"],
            version_num=self.config["version_num"],
            max_workers=self.config["max_workers"]
        )
        
        self.fixed_params = self._get_fixed_params()
    
    def _load_config(self) -> Dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_fixed_params(self) -> Dict:
        return {
            # domain settings
            "domains": [
                "persuasion",
                "system_operation", 
                "ambigious_instruction",
                "long-term_follow_up",
                "glasses_assistant",
                "recommendation"
            ],
            
            # inference trigger factor description 
            "domain_descriptions": {
                "persuasion": "the trigger factor is assistant's information, ability, or experience.",
                "long-term_follow_up": "the trigger factor is a past conversation history that inspires the assistant proactively initiate conversation now.",
                "system_operation": "the trigger factor is the specific sequence of opeation behaviors currently captured from the user.",
                "ambigious_instruction": "the trigger factor is an instruction with vague elements and unclear user intention.",
                "glasses_assistant": "the trigger factor is either an external event the user perceives or the user's own state/behavior at that moment captured from a smart glasses.",
                "recommendation": "the trigger factor is assistant's preference, habits, or favors",
            },
            
            # file path settings
            "dataset_base_path": "../dataset",
            "conversation_results_path": "conversation_results",
            
            # target planning evaluation difficulty settings
            "eval_difficulties": {
                "all": "eval.json",
                "fair": "fair.json", 
                "hard": "hard.json"
            },
            
            # conversation generation parameters
            "conversation_params": {
                "max_turns": 6,
                "window_size": 6,
                "begin_index": 0,
                "end_index": 5
            },
            
            # retry parameters
            "max_retries": 5,
            "max_attempts": 2
        }
    
    def get_model_name_safe(self, model_name: str) -> str:
        return model_name.replace("/", "_").replace(":", "_")
    
    def get_output_path(self, task_type: str) -> str:
        model_name_safe = self.get_model_name_safe(self.evaluated_model.model_name)
        folder_name = self.task_config.output_folder_name[task_type]
        version_num = self.task_config.version_num
        return f"{folder_name}_v{version_num}/{model_name_safe}"
    
    
    def get_domain_config(self, domain: str, eval_difficulty: str = "all") -> Dict:
        trigger_description = self.fixed_params["domain_descriptions"].get(domain, "")
        filename = self.fixed_params["eval_difficulties"][eval_difficulty]
        input_file = f"{self.fixed_params['dataset_base_path']}/{domain}/{filename}"
        
        return {
            "name": domain,
            "trigger_description": trigger_description,
            "input_file": input_file
        } 