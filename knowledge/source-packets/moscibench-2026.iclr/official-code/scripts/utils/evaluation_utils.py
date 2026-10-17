from scripts.evaluator import Evaluator
from typing import Dict, List

class EvaluationUtils:
    def __init__(self, root_path: str):
        self.root_path = root_path

    async def evaluate_graph(self, dataset: str, graph, llm_config: dict, directory: str, validation_n: int = 1, is_test: bool = False, exp_config: Dict = None):
        """
        Evaluate the graph and return average score
        
        Args:
            dataset: Dataset name
            graph: Graph object to evaluate
            llm_config: LLM configuration
            directory: Directory to save evaluation results
            validation_n: Number of validation runs
            is_test: Whether this is a test evaluation
            
        Returns:
            Average score across validation runs
        """
        evaluator = Evaluator(eval_path=directory)
        sum_score = 0

        # 准备参数字典，包含实验配置
        params = {
            "llm_config": llm_config,
            "dataset": {},
            "exp_config": exp_config or {},  # 传递实验配置
        }
        
        for i in range(validation_n):
            score, avg_cost, total_cost = await evaluator.graph_evaluate(
                dataset,
                graph,
                params,
                directory,
                is_test=is_test
            )
            sum_score += score

        return sum_score / validation_n