# -*- coding: utf-8 -*-
# @Date    : 8/23/2024 10:00 AM
# @Author  : all
# @Desc    : Evaluation for different datasets

from typing import Dict, Literal, Tuple
from pathlib import Path

from benchmarks.mosci import MoSciBenchmark

class Evaluator:
    """
    Complete the evaluation for different datasets here
    """

    def __init__(self, eval_path: str):
        self.eval_path = eval_path

    async def graph_evaluate(
        self, dataset: str, graph, params: dict, path: str, is_test: bool = False
    ) -> Tuple[float, float, float]:
        
        
        print(f"Evaluating dataset: {dataset}")
        data_path = self._get_data_path(dataset, is_test)

        benchmark = MoSciBenchmark(name=dataset, file_path=data_path, log_path=path)
        # Use params to configure the graph and benchmark
        configured_graph = await self._configure_graph(dataset, graph, params)
        if is_test:
            va_list = None  # For test data, generally use None to test all
        else:
            va_list = None  # Use None to test all Validation data, or set va_list (e.g., [1, 2, 3]) to use partial data
        return await benchmark.run_evaluation(configured_graph, va_list)

    async def _configure_graph(self, dataset, graph, params: dict):
        # Here you can configure the graph based on params
        # For example: set LLM configuration, dataset configuration, etc.
        dataset_config = params.get("dataset", {})
        llm_config = params.get("llm_config", {})
        exp_config = params.get("exp_config", {})  # 获取实验配置
        return graph(name=dataset, llm_config=llm_config, dataset=dataset_config, exp_config=exp_config)

    def _get_data_path(self, dataset: str, test: bool) -> str:
        data_path = f"data/{dataset.lower()}/discovery_tasks.json"
        return data_path if test else data_path
