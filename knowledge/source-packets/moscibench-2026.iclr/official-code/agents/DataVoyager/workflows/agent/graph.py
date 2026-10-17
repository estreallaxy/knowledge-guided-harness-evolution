# -*- coding: utf-8 -*-
# @Desc    : DataVoyager workflow for MoSci Scientific Discovery

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
        
        # DataVoyager四个核心组件
        self.analysis = operator.Analysis(self.llm)        # Planner
        self.code_generate = operator.CodeGenerate(self.llm)  # Code Generator
        self.code_execute = operator.CodeExecute(self.llm)    # Data Analysis
        self.code_refine = operator.CodeRefine(self.llm)
        
        # MoSci specific operator for hypothesis testing and answer formatting
        self.scientific_conclusion = operator.ScientificConclusion(self.llm)
        
        # DataVoyager Critic组件
        self.critic = operator.Critic(self.llm)               # Critic
        
    # Signature MUST match MoSciBenchmark.evaluate_problem call
    async def __call__(self, 
                task_data: Dict[str, Any],
                datasets_dir: str,
                work_path: str) -> Tuple[str, float]:
        """
        DataVoyager Scientific Discovery workflow: 
        Analysis -> CodeGen -> Execute -> Critic -> ScientificConclusion
        Returns (formatted_answer, total_cost).
        """
        
        task_id = task_data.get('id', 'unknown')
        final_answer = ""
        plan = ""
        final_code = ""
        exec_result: Dict[str, Any] = {}
        critic_suggestions = ""

        try:
            # 从实验配置中获取Analysis参数
            analysis_config = self.exp_config.get("analysis", {})
            include_workflow = analysis_config.get("include_workflow", False)
            include_domain_knowledge = analysis_config.get("include_domain_knowledge", False)
            
            # 1. DataVoyager Planner: Analyze the scientific problem and create a research plan
            analysis_result = await self.analysis(
                task_data=task_data,
                datasets_dir=datasets_dir,
                work_path=work_path,
                include_workflow=include_workflow,  # 使用实验配置
                include_domain_knowledge=include_domain_knowledge  # 使用实验配置
            )
            
            plan = analysis_result.get("plan", "") 
            if not plan or "error" in analysis_result:
                logger.error(f"Scientific analysis failed for task {task_id}: {analysis_result.get('error', 'No plan generated')}")
                cost = self.llm.get_usage_summary().get("total_cost", 0.0)
                return f"Error: Analysis failed", cost

            # 2. DataVoyager Code Generator: Generate scientific analysis code based on the research plan
            code_gen_result = await self.code_generate(
                task_data=task_data,
                datasets_dir=datasets_dir,
                work_path=work_path,
                plan=plan
            )
            
            code = code_gen_result.get("response", "") or code_gen_result.get("python_code", "")
            final_code = code
             
            if not code or "error" in code_gen_result:
                logger.error(f"Code generation failed for task {task_id}: {code_gen_result.get('error', 'No code generated')}")
                cost = self.llm.get_usage_summary().get("total_cost", 0.0)
                return f"Error: Code generation failed", cost

            # 3. DataVoyager Data Analysis: Execute the scientific analysis code in the work_path
            exec_result = await self.code_execute(
                code=code, 
                output_dir=work_path,  # 使用work_path作为输出目录
                timeout=3600  # 60 minutes timeout for scientific analysis
            )

            # 4. Code refinement loop if execution failed
            MAX_RETRIES = 3
            retries = 0
            while not exec_result.get("success") and retries < MAX_RETRIES:
                retries += 1
                logger.warning(f"Code execution failed for task {task_id}. Retrying ({retries}/{MAX_RETRIES})... Error: {exec_result.get('error')}\nSTDERR: {exec_result.get('stderr')}")
                
                # Use CodeRefine to fix the code based on execution error
                code_refine_result = await self.code_refine(
                    task_data=task_data,
                    datasets_dir=datasets_dir,
                    work_path=work_path,
                    plan=plan,
                    prev_code=code, 
                    exec_result=exec_result
                )
                
                code = code_refine_result.get("response", "") or code_refine_result.get("python_code", "")
                if not code or "error" in code_refine_result:
                    logger.error(f"Code refinement failed for task {task_id}: {code_refine_result.get('error', 'No code generated')}")
                    break
                
                final_code = code
                # Re-execute the refined code
                exec_result = await self.code_execute(
                    code=code, 
                    output_dir=work_path,  # 使用work_path作为输出目录
                    timeout=3600
                )

            # 5. DataVoyager Critic: Generate initial conclusion and get critic feedback
            if exec_result.get("success"):
                # Generate initial conclusion
                initial_conclusion_result = await self.scientific_conclusion(
                    task_data=task_data,
                    work_path=work_path
                )
                
                initial_answer = initial_conclusion_result.get("formatted_answer", "") or initial_conclusion_result.get("response", "")
                
                if initial_answer:
                    # Read analysis results for critic evaluation
                    results_file = os.path.join(work_path, "scientific_computation_results.txt")
                    analysis_results_text = ""
                    if os.path.exists(results_file):
                        try:
                            with open(results_file, 'r', encoding='utf-8') as f:
                                analysis_results_text = f.read()
                        except:
                            analysis_results_text = "[Could not read analysis results]"
                    
                    # Get critic feedback
                    critic_result = await self.critic(
                        task_data=task_data,
                        plan=plan,
                        code=final_code,
                        exec_result=exec_result,
                        analysis_results=analysis_results_text,
                        current_answer=initial_answer
                    )
                    
                    critic_suggestions = critic_result.get("suggestions", "")
                    logger.info(f"DataVoyager Critic feedback for task {task_id}: {critic_suggestions[:200]}...")
                    
                    # Store critic suggestions for the final conclusion
                    task_data_with_critic = task_data.copy()
                    task_data_with_critic["critic_suggestions"] = critic_suggestions
                    
                    # 6. Generate final scientific conclusion with critic feedback
                    final_conclusion_result = await self.scientific_conclusion(
                        task_data=task_data_with_critic,
                        work_path=work_path
                    )
                    
                    final_answer = final_conclusion_result.get("formatted_answer", "") or final_conclusion_result.get("response", "")
                    
                else:
                    final_answer = "Error: No initial conclusion generated"
            else:
                final_answer = "Error: Code execution failed"
            
            if not final_answer:
                final_answer = f"Error: No valid scientific conclusion generated"

            if exec_result.get("success"):
                logger.info(f"DataVoyager workflow successful for task {task_id}. Work saved in: {work_path}")
            else:
                logger.error(f"Final code execution failed for task {task_id}. Error: {exec_result.get('error')}\nWork path: {work_path}")
                if not final_answer.startswith("Error:"):
                    final_answer = f"Error: {exec_result.get('error', 'Execution failed')}"

        except Exception as e:
            logger.error(f"DataVoyager workflow error for task {task_id}: {type(e).__name__} - {e}\nWork path: {work_path}\nPlan: {plan}\nCode:\n{final_code}\nExec: {exec_result}")
            final_answer = f"Error: {str(e)}"

        # Always return the formatted answer and cost accumulated so far
        cost = self.llm.get_usage_summary().get("total_cost", 0.0)
        return final_answer, cost