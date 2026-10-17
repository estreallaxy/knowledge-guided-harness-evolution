# -*- coding: utf-8 -*-
# @Desc    : NoDataGuess workflow for MoSci Scientific Discovery

import os
import asyncio
from typing import Literal, Dict, Any, Tuple
from pathlib import Path
import workspace.MLE.workflows.template.operator as operator
import workspace.MLE.workflows.agent.prompt as prompt_custom 
from scripts.async_llm import create_llm_instance
from scripts.logs import logger

# Define DatasetType for MoSci
DatasetType = Literal[ "MoSci"]


class Workflow:
    def __init__(
        self,
        name: str,
        llm_config: Dict,
        dataset: DatasetType, # dataset name "MoSci"
        exp_config: Dict = None,  # 添加实验配置参数
    ) -> None:
        self.name = name
        self.dataset = dataset
        self.llm = create_llm_instance(llm_config)
        self.exp_config = exp_config or {}  # 存储实验配置
        
        # NoDataGuess只需要一个算子
        self.nodata_guess = operator.NoDataGuess(self.llm)
        
    # Signature MUST match MoSciBenchmark.evaluate_problem call
    async def __call__(self, 
                task_data: Dict[str, Any],
                datasets_dir: str,
                work_path: str) -> Tuple[str, float]:
        """
        NoDataGuess workflow: 
        直接基于data_description.json和领域知识猜测科学假设结论
        Returns (formatted_answer, total_cost).
        """
        
        task_id = task_data.get('id', 'unknown')
        final_answer = ""

        try:
            logger.info(f"=== NoDataGuess Workflow Starting for task {task_id} ===")
            logger.info(f"Using data_description.json from: {Path(datasets_dir).parent / 'data_description.json'}")
            logger.info("Making educated guess based on dataset description and domain knowledge only")
            
            # 直接使用NoDataGuess算子进行猜测
            guess_result = await self.nodata_guess(
                task_data=task_data,
                datasets_dir=datasets_dir,
                work_path=work_path
            )
            
            final_answer = guess_result.get("formatted_answer", "") or guess_result.get("response", "")
            hypothesis_guess = guess_result.get("hypothesis_guess", "")
            
            if not final_answer:
                final_answer = "Error: No guess could be generated"
                logger.error(f"NoDataGuess failed to generate answer for task {task_id}")
            else:
                logger.info(f"NoDataGuess completed for task {task_id}")
                logger.info(f"Hypothesis guess: {hypothesis_guess[:200]}..." if len(hypothesis_guess) > 200 else hypothesis_guess)
                logger.info(f"Final answer: {final_answer}")

        except Exception as e:
            logger.error(f"NoDataGuess workflow error for task {task_id}: {type(e).__name__} - {e}")
            final_answer = f"Error: {str(e)}"

        # Always return the formatted answer and cost accumulated so far
        cost = self.llm.get_usage_summary().get("total_cost", 0.0)
        logger.info(f"NoDataGuess workflow completed for task {task_id}. Total cost: ${cost:.4f}")
        return final_answer, cost