"""Main entry point for MR.PEA"""
import os
import logging
import yaml
from datetime import datetime
from src import MRPEAAgent
from src.config_loader import load_main_config, load_prompt_configs
from openai import OpenAI


# Configure logging
log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_filename = f'{log_dir}/mrpea_{timestamp}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_openai_client(config):
    """Create OpenAI client based on configuration"""
    openai_config = config.get('openai', {})

    api_key = openai_config.get('api_key') or os.getenv('OPENAI_API_KEY') or os.getenv('AZURE_API_KEY')
    if not api_key:
        logger.error("OpenAI API key not found. Set OPENAI_API_KEY or AZURE_API_KEY env var, or add api_key to config.")
        return None

    try:
        client_kwargs = {'api_key': api_key}
        client_kwargs['base_url'] = openai_config['base_url']

        client = OpenAI(**client_kwargs)
        logger.info("OpenAI client initialized successfully")
        return client

    except Exception as e:
        logger.error(f"Failed to create OpenAI client: {e}")
        return None


def create_linkup_client(config):
    """Create LinkUp client for web search"""
    try:
        from linkup import LinkupClient
    except ImportError:
        logger.error("LinkUp package not installed. Install with: pip install linkup-sdk")
        return None

    web_search_config = config.get('web_search', {})
    api_key = web_search_config.get('linkup_api_key') or os.getenv('LINKUP_API_KEY')

    try:
        client = LinkupClient(api_key=api_key)
        logger.info("LinkUp client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create LinkUp client: {e}")
        return None


def main():
    logger.info("MR.PEA - Meta-Reasoning Prompt Engineering Agent")
    logger.info("=" * 50)

    # Load main configuration
    try:
        config = load_main_config()
        logger.info("Loaded main configuration successfully")
    except Exception as e:
        logger.error(f"Failed to load main configuration: {e}")
        return

    # Load prompt configurations (selects web/non-web templates based on enable_web_search in config)
    try:
        enable_web_search = config.get('web_search', {}).get('enabled', False)
        prompt_config = load_prompt_configs(enable_web_search=enable_web_search)
        logger.info("Loaded prompt configurations successfully")
    except Exception as e:
        logger.error(f"Failed to load prompt configurations: {e}")
        return

    # Create LinkUp client if web search is enabled
    linkup_client = None
    if enable_web_search:
        linkup_client = create_linkup_client(config)
        if linkup_client is None:
            logger.error("Failed to initialize LinkUp client. Install linkup-sdk and set LINKUP_API_KEY or config linkup_api_key.")
            return

    # Create OpenAI client
    openai_client = create_openai_client(config)
    if openai_client is None:
        logger.error("Failed to initialize OpenAI client. Please check your API key and configuration.")
        return

    # Read task_name and task_file from the main configuration
    task_cfg = config.get('task', {})
    task_name = task_cfg.get('task_name')
    task_file = task_cfg.get('task_file', 'config/tasks_simple.yaml')

    if not task_name:
        logger.error("Task name not specified in the configuration")
        return

    # Load task configuration
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            tasks = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {task_file}")
        return
    except Exception as e:
        logger.error(f"Failed to load task configuration: {e}")
        return

    if 'tasks' not in tasks or task_name not in tasks['tasks']:
        logger.error(f"Task '{task_name}' not found in configuration")
        return

    task_config = tasks['tasks'][task_name]

    logger.info(f"Task: {task_config['task_description']}")
    logger.info("=" * 50)

    # Initialize agent with loaded configuration and client
    agent = MRPEAAgent(
        config=config,
        openai_client=openai_client,
        linkup_client=linkup_client,
        system_prompts=prompt_config['system_prompts'],
        user_message=prompt_config['user_prompts']
    )

    # Run optimization
    best_prompt = agent.optimize_prompt(
        task_description=task_config['task_description'],
        task_objective=task_config['task_objective'],
        sample_question=task_config['sample_question']
    )

    logger.info(f"\nOptimized Prompt for {task_name}:")
    logger.info("=" * 40)
    logger.info(best_prompt)
    logger.info("=" * 40)

    # Save results
    agent.save_results(task_name, best_prompt)

    # Show memory statistics
    stats = agent.get_memory_stats()
    logger.info(f"\nMemory Statistics:")
    logger.info(f"   Prompts: {stats['prompts_count']}")
    logger.info(f"   Knowledge entries: {stats['knowledge_count']}")
    logger.info(f"   Examples: {stats['examples_count']}")
    logger.info(f"   Feedback entries: {stats['feedback_count']}")
    logger.info(f"   Memory file size: {stats['memory_file_size']} bytes")

    # Show final token usage summary
    from src.agents.base_agent import BaseAgent
    logger.info("\nFINAL TOKEN USAGE SUMMARY:")
    usage = BaseAgent.get_total_token_usage()
    logger.info(f"   Total Input Tokens: {usage['total_input_tokens']:,}")
    logger.info(f"   Total Output Tokens: {usage['total_output_tokens']:,}")
    logger.info(f"   Total Tokens: {usage['total_tokens']:,}")
    logger.info(f"   Total API Calls: {usage['total_api_calls']:,}")


if __name__ == "__main__":
    main()
