# -*- coding: utf-8 -*-
# @Desc    : Best of N workflow for MoSci Scientific Discovery with self-consistency

import os
import asyncio
from typing import Literal, Dict, Any, Tuple, List
from pathlib import Path
from collections import Counter
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
        # Initialize operators needed for scientific discovery
        self.analysis = operator.Analysis(self.llm)
        self.code_generate = operator.CodeGenerate(self.llm)
        self.code_execute = operator.CodeExecute(self.llm)
        self.code_refine = operator.CodeRefine(self.llm)
        
        # MoSci specific operator for hypothesis testing and answer formatting
        self.scientific_conclusion = operator.ScientificConclusion(self.llm)

    def _extract_answer_key(self, answer: str) -> str:
        """
        从答案中提取关键部分，用于自一致性比较
        去除格式化信息，只保留核心内容
        """
        # 移除常见的前缀和格式
        clean_answer = answer.strip()
        
        # 移除Error前缀
        if clean_answer.startswith("Error:"):
            return clean_answer
            
        # 提取主要答案内容，可以根据具体格式调整
        # 这里假设答案格式比较规范，可以根据实际情况调整提取逻辑
        lines = clean_answer.split('\n')
        # 寻找包含实际答案的行（可能需要根据具体格式调整）
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('*'):
                # 进一步清理格式字符
                key = line.replace('**', '').replace('*', '').strip()
                if key:
                    return key
        
        return clean_answer

    def _find_consensus_answer(self, answers: List[str]) -> str:
        """
        通过自一致性找到最一致的答案
        
        Args:
            answers: 多次推理的答案列表
            
        Returns:
            最终的一致性答案
        """
        if not answers:
            return "Error: No answers generated"
            
        # 提取答案的关键部分进行比较
        answer_keys = [self._extract_answer_key(ans) for ans in answers]
        
        # 统计每个答案出现的频次
        answer_counter = Counter(answer_keys)
        
        # 找出出现频次最高的答案
        most_common = answer_counter.most_common(1)[0]
        consensus_key, count = most_common
        
        # 记录一致性信息
        total_attempts = len(answers)
        consensus_ratio = count / total_attempts
        
        logger.info(f"Self-consistency results: {count}/{total_attempts} ({consensus_ratio:.2%}) consensus on answer")
        logger.debug(f"Answer frequency distribution: {dict(answer_counter)}")
        
        # 返回原始答案（找到第一个匹配consensus_key的完整答案）
        for answer in answers:
            if self._extract_answer_key(answer) == consensus_key:
                return answer
                
        return answers[0]  # fallback

    async def _run_single_inference(self, 
                                   task_data: Dict[str, Any],
                                   datasets_dir: str,
                                   work_path: str,
                                   attempt_num: int) -> str:
        """
        运行单次推理流程
        
        Args:
            task_data: 任务数据
            datasets_dir: 数据集目录
            work_path: 工作路径
            attempt_num: 尝试编号
            
        Returns:
            单次推理的答案
        """
        task_id = task_data.get('id', 'unknown')
        attempt_work_path = os.path.join(work_path, f"attempt_{attempt_num}")
        os.makedirs(attempt_work_path, exist_ok=True)
        
        try:
            # 从实验配置中获取Analysis参数
            analysis_config = self.exp_config.get("analysis", {})
            include_workflow = analysis_config.get("include_workflow", False)
            include_domain_knowledge = analysis_config.get("include_domain_knowledge", False)
            
            # 1. Analyze the scientific problem and create a research plan
            analysis_result = await self.analysis(
                task_data=task_data,
                datasets_dir=datasets_dir,
                work_path=attempt_work_path,
                include_workflow=include_workflow,
                include_domain_knowledge=include_domain_knowledge
            )
            
            plan = analysis_result.get("plan", "") 
            if not plan or "error" in analysis_result:
                logger.warning(f"Analysis failed for task {task_id} attempt {attempt_num}: {analysis_result.get('error', 'No plan generated')}")
                return f"Error: Analysis failed in attempt {attempt_num}"

            # 2. Generate scientific analysis code based on the research plan
            code_gen_result = await self.code_generate(
                task_data=task_data,
                datasets_dir=datasets_dir,
                work_path=attempt_work_path,
                plan=plan
            )
            
            code = code_gen_result.get("response", "") or code_gen_result.get("python_code", "")
             
            if not code or "error" in code_gen_result:
                logger.warning(f"Code generation failed for task {task_id} attempt {attempt_num}: {code_gen_result.get('error', 'No code generated')}")
                return f"Error: Code generation failed in attempt {attempt_num}"

            # 3. Execute the scientific analysis code
            exec_result = await self.code_execute(
                code=code, 
                output_dir=attempt_work_path,
                timeout=3600
            )

            # 4. Code refinement loop if execution failed
            MAX_RETRIES = 2  # 减少重试次数以节省时间
            retries = 0
            while not exec_result.get("success") and retries < MAX_RETRIES:
                retries += 1
                logger.debug(f"Code execution failed for task {task_id} attempt {attempt_num}. Retrying ({retries}/{MAX_RETRIES})...")
                
                code_refine_result = await self.code_refine(
                    task_data=task_data,
                    datasets_dir=datasets_dir,
                    work_path=attempt_work_path,
                    plan=plan,
                    prev_code=code, 
                    exec_result=exec_result
                )
                
                code = code_refine_result.get("response", "") or code_refine_result.get("python_code", "")
                if not code or "error" in code_refine_result:
                    logger.warning(f"Code refinement failed for task {task_id} attempt {attempt_num}")
                    break
                
                exec_result = await self.code_execute(
                    code=code, 
                    output_dir=attempt_work_path,
                    timeout=3600
                )

            # 5. Generate scientific conclusion
            conclusion_result = await self.scientific_conclusion(
                task_data=task_data,
                work_path=attempt_work_path
            )
            
            answer = conclusion_result.get("formatted_answer", "") or conclusion_result.get("response", "")
            
            if not answer:
                answer = f"Error: No valid scientific conclusion generated in attempt {attempt_num}"
            elif not exec_result.get("success"):
                logger.warning(f"Execution failed for task {task_id} attempt {attempt_num}, but got conclusion")
                
            logger.info(f"Completed attempt {attempt_num} for task {task_id}")
            return answer

        except Exception as e:
            logger.error(f"Error in attempt {attempt_num} for task {task_id}: {type(e).__name__} - {e}")
            return f"Error: Exception in attempt {attempt_num}: {str(e)}"

    # Signature MUST match MoSciBenchmark.evaluate_problem call
    async def __call__(self, 
                task_data: Dict[str, Any],
                datasets_dir: str,
                work_path: str) -> Tuple[str, float]:
        """
        Best of N MoSci Scientific Discovery workflow with self-consistency
        Returns (consensus_answer, total_cost).
        """
        
        task_id = task_data.get('id', 'unknown')
        
        # 从实验配置中获取Best of N的参数
        best_of_n_config = self.exp_config.get("best_of_n", {})
        max_n = best_of_n_config.get("max_n", 3)  # 默认3次尝试
        
        logger.info(f"Starting Best of N workflow for task {task_id} with max_n={max_n}")
        
        try:
            # 并行运行多次推理
            tasks = []
            for i in range(max_n):
                task = self._run_single_inference(
                    task_data=task_data,
                    datasets_dir=datasets_dir,
                    work_path=work_path,
                    attempt_num=i+1
                )
                tasks.append(task)
            
            # 等待所有推理完成
            answers = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常结果
            valid_answers = []
            for i, answer in enumerate(answers):
                if isinstance(answer, Exception):
                    logger.error(f"Exception in attempt {i+1} for task {task_id}: {answer}")
                    valid_answers.append(f"Error: Exception in attempt {i+1}")
                else:
                    valid_answers.append(answer)
            
            # 通过自一致性找到最佳答案
            final_answer = self._find_consensus_answer(valid_answers)
            
            logger.info(f"Best of N workflow completed for task {task_id}. Final answer determined through self-consistency.")
            
        except Exception as e:
            logger.error(f"Best of N workflow error for task {task_id}: {type(e).__name__} - {e}")
            final_answer = f"Error: {str(e)}"

        # 返回最终答案和总成本
        cost = self.llm.get_usage_summary().get("total_cost", 0.0)
        llm_usage = self.llm.get_usage_summary()
        return final_answer, llm_usage