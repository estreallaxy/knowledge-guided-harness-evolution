"""
Configuration loader utilities for MR.PEA system
Handles loading and merging of configuration files
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_main_config(config_file: str = None) -> Dict[str, Any]:
    """Load main configuration file"""
    if config_file is None:
        config_file = "config/mrpea_config.yaml"

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        logger.info(f"Configuration loaded from {config_file}")
        return config

    except FileNotFoundError:
        logger.warning(f"Config file {config_file} not found, using defaults")
        return get_default_config()
    except Exception as e:
        logger.error(f"Failed to load config file {config_file}: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values with nested structure"""
    return {
        'system': {
            'config_path': 'config/',
            'memory_dir': 'memory'
        },
        'task': {
            'task_name': 'default'
        },
        'web_search': {
            'enabled': False,
            'linkup_api_key': None,
            'max_searches': 2,
        },
        'confidence': {
            'threshold': 0.8,
        },
        'optimization': {
            'max_iterations': 10,
            'win_threshold': 3,
            'current_best_id': 0,
            'historical_prompt_limit': 5,
            'ranking': {
                'iteration_bonus': 0.1,
                'decay_factor': 0.9,
                'base_score': 1.0
            }
        },
        'memory': {
            'auto_save': True,
            'max_prompts': 100,
            'max_knowledge_entries': 50,
            'max_examples': 20
        },
        'output': {
            'results_dir': 'results/',
            'export_memory': True,
            'save_intermediate': False
        },
        'openai': {
            'api_key': None,
            'base_url': None,
            'organization': None
        },
        'agents': {
            'meta_reasoning': {'model': 'gpt-4o-mini', 'temperature': 0.7, 'max_tokens': 2048},
            'search_query': {'model': 'gpt-4o-mini', 'temperature': 0.3, 'max_tokens': 512},
            'prompt_engineering': {'model': 'gpt-4o-mini', 'temperature': 0.5, 'max_tokens': 2048},
            'prompt_refinement': {'model': 'gpt-4o-mini', 'temperature': 0.4, 'max_tokens': 2048},
            'evaluation': {'model': 'gpt-4o-mini', 'temperature': 0.2, 'max_tokens': 1024},
            'web_search': {'model': 'gpt-4o-mini', 'temperature': 0.3, 'max_tokens': 512},
            'meta_decision': {'model': 'gpt-4o-mini', 'temperature': 0.4, 'max_tokens': 1024}
        }
    }


def load_prompt_configs(config_path: str = "config/", enable_web_search: bool = False) -> Dict[str, Any]:
    """Load system and user prompt configurations, choosing the right files based on web search mode"""
    config_dir = Path(config_path)

    if enable_web_search:
        system_file = "prompts/system_prompts_web.yaml"
        user_file = "prompts/user_prompts_web.yaml"
        logger.info("Loading web-search-enabled prompt templates")
    else:
        system_file = "prompts/system_prompts.yaml"
        user_file = "prompts/user_prompts.yaml"
        logger.info("Loading base prompt templates (no web search)")

    try:
        with open(config_dir / system_file, 'r', encoding='utf-8') as f:
            system_prompts = yaml.safe_load(f)

        try:
            with open(config_dir / user_file, 'r', encoding='utf-8') as f:
                user_prompts = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"{user_file} not found, using empty dictionary")
            user_prompts = {}

        logger.info("Prompt configuration files loaded successfully")

        return {
            'system_prompts': system_prompts,
            'user_prompts': user_prompts
        }

    except Exception as e:
        logger.error(f"Failed to load prompt configurations: {e}")
        raise


def merge_config_overrides(base_config: Dict[str, Any], **overrides) -> Dict[str, Any]:
    """Merge configuration overrides with base configuration"""
    merged_config = base_config.copy()

    for key, value in overrides.items():
        if value is not None:
            merged_config[key] = value
            logger.debug(f"Config override: {key} = {value}")

    return merged_config
