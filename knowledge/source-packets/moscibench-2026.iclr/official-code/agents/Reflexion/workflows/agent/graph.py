# -*- coding: utf-8 -*-
# @Desc    :  Reflexion (Oracle) workflow for MoSci Scientific Discovery

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
        
        # DataVoyager核心组件
        self.analysis = operator.Analysis(self.llm)        # Planner
        self.code_generate = operator.CodeGenerate(self.llm)  # Code Generator
        self.code_execute = operator.CodeExecute(self.llm)    # Data Analysis
        self.code_refine = operator.CodeRefine(self.llm)
        self.scientific_conclusion = operator.ScientificConclusion(self.llm)
        self.critic = operator.Critic(self.llm)               # Critic
        
        # Reflexion (Oracle) 组件
        self.reflexion = operator.Reflexion(self.llm)         # Reflexion
        
        # Oracle评估器算子
        oracle_type = exp_config.get("oracle_type", "llm")  # "llm" or "simple"
        self.oracle = operator.Oracle(self.llm, evaluation_type=oracle_type)
        
        # Reflexion配置
        self.max_trials = exp_config.get("max_trials", 3)
        
    async def _single_trial(self, task_data: Dict[str, Any], datasets_dir: str, 
                           work_path: str, trial_num: int, plan: str = "", 
                           previous_reflection: str = "") -> Tuple[str, Dict]:
        """执行单次试验"""
        task_id = task_data.get('id', 'unknown')
        final_answer = ""
        final_code = ""
        exec_result: Dict[str, Any] = {}
        
        # 如果有前一次的反思，将其加入task_data
        if previous_reflection:
            task_data_with_reflection = task_data.copy()
            task_data_with_reflection["previous_reflection"] = previous_reflection
            logger.info(f"Trial {trial_num}: Using previous reflection for improvement")
        else:
            task_data_with_reflection = task_data
        
        try:
            # 1. DataVoyager Planner (如果没有提供plan)
            if not plan:
                analysis_config = self.exp_config.get("analysis", {})
                include_workflow = analysis_config.get("include_workflow", False)
                include_domain_knowledge = analysis_config.get("include_domain_knowledge", False)
                
                logger.info(f"DataVoyager Trial {trial_num}: Planner analyzing task {task_id}")
                analysis_result = await self.analysis(
                    task_data=task_data_with_reflection,
                    datasets_dir=datasets_dir,
                    work_path=work_path,
                    include_workflow=include_workflow,
                    include_domain_knowledge=include_domain_knowledge
                )
                plan = analysis_result.get("plan", "")
            else:
                logger.info(f"DataVoyager Trial {trial_num}: Using plan from previous analysis")
            
            if not plan or "error" in str(plan):
                return f"Error: Analysis failed", {
                    "success": False, 
                    "error": "No plan generated", 
                    "plan": plan, 
                    "code": "",
                    "exec_result": {}
                }

            # 2. DataVoyager Code Generator
            logger.info(f"DataVoyager Trial {trial_num}: Code Generator creating code for task {task_id}")
            code_gen_result = await self.code_generate(
                task_data=task_data_with_reflection,
                datasets_dir=datasets_dir,
                work_path=work_path,
                plan=plan
            )
            
            code = code_gen_result.get("response", "") or code_gen_result.get("python_code", "")
            final_code = code
            
            if not code or "error" in code_gen_result:
                return f"Error: Code generation failed", {
                    "success": False, 
                    "error": "No code generated", 
                    "plan": plan, 
                    "code": final_code,
                    "exec_result": {}
                }

            # 3. DataVoyager Data Analysis
            logger.info(f"DataVoyager Trial {trial_num}: Data Analysis executing code for task {task_id}")
            exec_result = await self.code_execute(
                code=code, 
                output_dir=work_path,
                timeout=3600
            )

            # 4. Code refinement loop if execution failed (减少重试次数，为Reflexion留出空间)
            MAX_RETRIES = 2
            retries = 0
            while not exec_result.get("success") and retries < MAX_RETRIES:
                retries += 1
                logger.warning(f"DataVoyager Trial {trial_num}: Code execution failed. Retrying ({retries}/{MAX_RETRIES})...")
                
                code_refine_result = await self.code_refine(
                    task_data=task_data_with_reflection,
                    datasets_dir=datasets_dir,
                    work_path=work_path,
                    plan=plan,
                    prev_code=code, 
                    exec_result=exec_result
                )
                
                code = code_refine_result.get("response", "") or code_refine_result.get("python_code", "")
                if not code or "error" in code_refine_result:
                    break
                
                final_code = code
                exec_result = await self.code_execute(
                    code=code, 
                    output_dir=work_path,
                    timeout=3600
                )

            # 5. DataVoyager Critic + Scientific Conclusion
            if exec_result.get("success"):
                # Generate initial conclusion
                initial_conclusion_result = await self.scientific_conclusion(
                    task_data=task_data_with_reflection,
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
                    task_data_with_reflection["work_path"] = work_path  # 确保work_path在task_data中
                    critic_result = await self.critic(
                        task_data=task_data_with_reflection,
                        plan=plan,
                        code=final_code,
                        exec_result=exec_result,
                        analysis_results=analysis_results_text,
                        current_answer=initial_answer
                    )
                    
                    critic_suggestions = critic_result.get("suggestions", "")
                    
                    # Generate final conclusion with critic feedback
                    if critic_suggestions:
                        task_data_with_critic = task_data_with_reflection.copy()
                        task_data_with_critic["critic_suggestions"] = critic_suggestions
                        
                        final_conclusion_result = await self.scientific_conclusion(
                            task_data=task_data_with_critic,
                            work_path=work_path
                        )
                        
                        final_answer = final_conclusion_result.get("formatted_answer", "") or final_conclusion_result.get("response", "")
                    else:
                        final_answer = initial_answer
                else:
                    final_answer = "Error: No initial conclusion generated"
            else:
                final_answer = f"Error: Code execution failed - {exec_result.get('error', 'Unknown error')}"

            if not final_answer:
                final_answer = "Error: No valid scientific conclusion generated"

            return final_answer, {
                "success": exec_result.get("success", False),
                "plan": plan,
                "code": final_code,
                "exec_result": exec_result,
                "error": exec_result.get("error")
            }
            
        except Exception as e:
            logger.error(f"Trial {trial_num} error for task {task_id}: {type(e).__name__} - {e}")
            return f"Error: {str(e)}", {
                "success": False,
                "plan": plan,
                "code": final_code,
                "exec_result": exec_result,
                "error": str(e)
            }
    
    # Signature MUST match MoSciBenchmark.evaluate_problem call
    async def __call__(self, 
                task_data: Dict[str, Any],
                datasets_dir: str,
                work_path: str) -> Tuple[str, float]:
        """
        DataVoyager with Reflexion (Oracle) workflow:
        Trial 1 -> Oracle Feedback -> Reflexion -> Trial 2 -> Oracle -> Reflexion -> Trial 3
        Returns (formatted_answer, total_cost).
        """
        
        task_id = task_data.get('id', 'unknown')
        final_answer = ""
        plan = ""
        previous_reflection = ""
        
        # 创建trial-specific工作目录
        base_work_path = work_path
        
        try:
            logger.info(f"=== DataVoyager Reflexion Workflow Starting for task {task_id} ===")
            logger.info(f"Max trials: {self.max_trials}, Oracle type: {self.exp_config.get('oracle_type', 'llm')}")
            
            # Reflexion (Oracle) 循环
            for trial_num in range(1, self.max_trials + 1):
                trial_work_path = os.path.join(base_work_path, f"trial_{trial_num}")
                os.makedirs(trial_work_path, exist_ok=True)
                
                logger.info(f"=== DataVoyager Reflexion Trial {trial_num}/{self.max_trials} for task {task_id} ===")
                
                # 执行单次试验
                trial_answer, trial_info = await self._single_trial(
                    task_data, datasets_dir, trial_work_path, trial_num, plan, previous_reflection
                )
                
                # 记录当前试验结果
                final_answer = trial_answer
                trial_plan = trial_info.get("plan", "")
                trial_code = trial_info.get("code", "")
                trial_exec_result = trial_info.get("exec_result", {})
                trial_success = trial_info.get("success", False)
                
                logger.info(f"Trial {trial_num} completed. Success: {trial_success}")
                logger.info(f"Trial {trial_num} answer: {trial_answer[:200]}...")
                
                # Oracle 评估 (使用算子)
                try:
                    oracle_score = await self.oracle(trial_answer, task_data, trial_work_path)
                except Exception as e:
                    logger.warning(f"Oracle evaluator error: {e}")
                    oracle_score = 0.0
                
                logger.info(f"DataVoyager Trial {trial_num} Oracle Score: {oracle_score}")
                
                # 如果Oracle评分 >= 1.0，任务完成
                if oracle_score >= 1.0:
                    logger.info(f"🎉 DataVoyager Reflexion SUCCESS: Task {task_id} solved in trial {trial_num} with HMS = {oracle_score}")
                    break
                
                # 如果不是最后一次试验且Oracle评分 < 1.0，进行Reflexion
                if trial_num < self.max_trials and oracle_score < 1.0:
                    logger.info(f"DataVoyager Reflexion: Trial {trial_num} failed (HMS = {oracle_score}), generating reflection...")
                    
                    # 生成反思
                    try:
                        reflexion_result = await self.reflexion(
                            task_data=task_data,
                            trial_num=trial_num,
                            max_trials=self.max_trials,
                            previous_plan=trial_plan,
                            previous_answer=trial_answer,
                            hms_score=oracle_score,
                            work_path=trial_work_path
                        )
                        
                        # 获取反思内容用于下一次试验
                        previous_reflection = reflexion_result.get("reflection", "")
                        if not previous_reflection:
                            logger.warning(f"DataVoyager Reflexion failed to generate reflection for trial {trial_num + 1}")
                        else:
                            logger.info(f"DataVoyager Reflexion completed for trial {trial_num}")
                            logger.info(f"Reflection preview: {previous_reflection[:200]}...")
                    
                    except Exception as e:
                        logger.error(f"Reflexion generation error: {e}")
                        previous_reflection = ""
                    
                    logger.info(f"Preparing for trial {trial_num + 1} with reflection feedback...")
                else:
                    logger.info(f"📊 DataVoyager Reflexion: Final trial {trial_num} completed with HMS = {oracle_score}")

            # 最终总结
            final_oracle_score = oracle_score if 'oracle_score' in locals() else 0.0
            if final_oracle_score >= 1.0:
                logger.info(f"DataVoyager Reflexion SUCCESS: Task {task_id} solved with HMS = {final_oracle_score}")
            else:
                logger.info(f"DataVoyager Reflexion FAILED: Task {task_id} not solved after {self.max_trials} trials (Final HMS = {final_oracle_score})")
            
            logger.info(f"DataVoyager Reflexion workflow completed for task {task_id} after {self.max_trials} trials")

        except Exception as e:
            logger.error(f"DataVoyager Reflexion workflow error for task {task_id}: {type(e).__name__} - {e}")
            final_answer = f"Error: {str(e)}"

        # Always return the formatted answer and cost accumulated so far
        cost = self.llm.get_usage_summary().get("total_cost", 0.0)
        logger.info(f"DataVoyager Reflexion workflow completed for task {task_id}. Total cost: ${cost:.4f}")
        return final_answer, cost