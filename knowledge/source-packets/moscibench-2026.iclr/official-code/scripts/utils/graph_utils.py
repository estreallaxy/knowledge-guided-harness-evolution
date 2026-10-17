import os
from scripts.logs import logger


class GraphUtils:
    def __init__(self, root_path: str):
        self.root_path = root_path

    def create_round_directory(self, graph_path: str, round_identifier: str) -> str:
        """
        Create directory for a specific round/run
        
        Args:
            graph_path: Base workflows path
            round_identifier: Round identifier (can be string like "1_run_1_baseline")
            
        Returns:
            Path to the created directory
        """
        # 如果已经包含round_前缀，直接使用；否则添加前缀
        if round_identifier.startswith('round_'):
            directory_name = round_identifier
        else:
            directory_name = f"round_{round_identifier}"
            
        directory = os.path.join(graph_path, directory_name)
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created round directory: {directory}")
        return directory

    def load_graph(self, round_number: int, workflows_path: str):
        """
        Load graph workflow class from the agent directory (not round_X)
        
        Args:
            round_number: Round number (for compatibility, but we use agent directory)
            workflows_path: Path to workflows directory
            
        Returns:
            Workflow class
        """
        # 转换路径为模块名格式
        workflows_path = workflows_path.replace("\\", ".").replace("/", ".")
        
        # 使用agent目录而不是round_X目录
        graph_module_name = f"{workflows_path}.agent.graph"

        try:
            graph_module = __import__(graph_module_name, fromlist=[""])
            graph_class = getattr(graph_module, "Workflow")
            logger.info(f"Successfully loaded graph from {graph_module_name}")
            return graph_class
        except ImportError as e:
            logger.error(f"Error loading graph from agent directory: {e}")
            # 提供更详细的错误信息
            logger.error(f"Attempted to load: {graph_module_name}")
            logger.error(f"Make sure the agent directory exists and contains graph.py with Workflow class")
            raise
        except AttributeError as e:
            logger.error(f"Error: Workflow class not found in {graph_module_name}: {e}")
            logger.error("Make sure graph.py contains a class named 'Workflow'")
            raise

    def load_graph_from_directory(self, workflows_path: str, directory_name: str = "agent"):
        """
        Load graph workflow class from a specific directory
        
        Args:
            workflows_path: Path to workflows directory
            directory_name: Directory name to load from (default: "agent")
            
        Returns:
            Workflow class
        """
        # 转换路径为模块名格式
        workflows_path = workflows_path.replace("\\", ".").replace("/", ".")
        graph_module_name = f"{workflows_path}.{directory_name}.graph"

        try:
            graph_module = __import__(graph_module_name, fromlist=[""])
            graph_class = getattr(graph_module, "Workflow")
            logger.info(f"Successfully loaded graph from {graph_module_name}")
            return graph_class
        except ImportError as e:
            logger.error(f"Error loading graph from {directory_name} directory: {e}")
            logger.error(f"Attempted to load: {graph_module_name}")
            raise
        except AttributeError as e:
            logger.error(f"Error: Workflow class not found in {graph_module_name}: {e}")
            raise