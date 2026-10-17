import asyncio
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Tuple, Optional, Dict
import pandas as pd

from benchmarks.benchmark import BaseBenchmark
from scripts.logs import logger
from tqdm.asyncio import tqdm_asyncio


class MoSciBenchmark(BaseBenchmark):
    """
    Benchmark class for Multimodal Scientific Discovery tasks.
    """
    def __init__(self, name: str, file_path: str, log_path: str):
        """
        Initializes the MoSciBenchmark.
        Args:
            name: Benchmark name ("MoSci").
            file_path: Path to the discovery_tasks.json file.
            log_path: Directory to save logs and results.
        """
        super().__init__(name, file_path, log_path)
        
        # Extract data directory from file_path
        self.tasks_file = Path(file_path)
        self.data_dir = self.tasks_file.parent
        self.datasets_dir = self.data_dir / "datasets"
        
        # Create log directory
        Path(self.log_path).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MoSciBenchmark initialized with data_dir: {self.data_dir}")
        logger.info(f"Datasets directory: {self.datasets_dir}")

    def get_result_columns(self) -> List[str]:
        return [
            "task_id",
            "task_type", 
            "scientific_domain",
            "problem_type",
            "prediction",
            "expected_output",
            "extracted_answer",
            "score",
            "cost",
            "error_message"
        ]

    def extract_answer(self, text: str, answer_format: str, expected_output: Any) -> Optional[Any]:
        """从graph回答中提取答案 - 优先提取{}括号中的内容"""
        try:
            text = str(text).strip()
            
            # 优先提取花括号中的内容
            bracket_matches = re.findall(r'\{([^}]+)\}', text)
            if bracket_matches:
                # 取最后一个匹配（最可能是答案）
                extracted_content = bracket_matches[-1].strip()
                
                # 如果提取的内容是 "NA"，直接返回
                if extracted_content.upper() == "NA":
                    return "NA"
                
                # 根据expected_output类型转换提取的内容
                if isinstance(expected_output, bool):
                    content_lower = extracted_content.lower()
                    if content_lower in ['true', '1', 'yes', 't']:
                        return True
                    elif content_lower in ['false', '0', 'no', 'f']:
                        return False
                    # 如果不是明确的布尔值，返回原始内容
                    return extracted_content
                        
                elif isinstance(expected_output, (int, float)):
                    # 尝试转换为数值
                    try:
                        # 移除可能的百分号
                        numeric_content = extracted_content.replace('%', '').strip()
                        return float(numeric_content)
                    except ValueError:
                        # 如果无法转换为数值，返回原始内容
                        return extracted_content
                            
                elif isinstance(expected_output, str):
                    # 直接返回字符串内容
                    return extracted_content
                
                # 其他类型，返回原始内容
                return extracted_content
            
            # 如果没有找到花括号内容，使用原有的提取逻辑作为fallback
            
            # 处理True/False格式
            if isinstance(expected_output, bool):
                text_lower = text.lower()
                if 'true' in text_lower:
                    return True
                elif 'false' in text_lower:
                    return False
            
            # 处理填空题格式 - 寻找花括号中的内容（原逻辑保留作为备用）
            if "{" in answer_format and "}" in answer_format:
                # 如果是数值类型
                if isinstance(expected_output, (int, float)):
                    # 寻找数值
                    numbers = re.findall(r'-?\d+\.?\d*', text)
                    if numbers:
                        try:
                            return float(numbers[-1])
                        except ValueError:
                            pass
                
                # 如果是字符串类型，寻找可能的特征名称
                elif isinstance(expected_output, str):
                    # 移除了硬编码的特征列表，让LLM自己在{}中提供答案
                    # 如果没有{}内容，尝试提取最后一个单词作为特征名
                    words = re.findall(r'\b[A-Za-z][A-Za-z0-9._]*\b', text)
                    if words:
                        return words[-1]
            
            # 处理百分比格式
            if "%" in answer_format:
                percentages = re.findall(r'(\d+\.?\d*)%', text)
                if percentages:
                    return float(percentages[-1])
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting answer: {e}")
            return None

    def calculate_score(self, expected_output: Any, prediction: Any, judge_type: str = "==") -> Tuple[float, Any]:
        """计算得分 - 支持不同的判断类型"""
        try:
            if prediction is None:
                return 0.0, prediction
            
            # 特殊处理 "NA" 预测值 - 直接判断为错误
            if isinstance(prediction, str) and prediction.strip().upper() == "NA":
                return 0.0, prediction
            
            # 处理数值比较
            if isinstance(expected_output, (int, float)):
                if isinstance(prediction, (int, float)):
                    # 根据judge_type进行不同的比较
                    if judge_type == ">=":
                        is_correct = prediction >= expected_output
                    elif judge_type == "<=":
                        is_correct = prediction <= expected_output
                    elif judge_type == ">":
                        is_correct = prediction > expected_output
                    elif judge_type == "<":
                        is_correct = prediction < expected_output
                    elif judge_type == "==" or judge_type is None:
                        # 原有的数值容差比较 (10%容差)
                        tolerance = abs(expected_output) * 0.1 if expected_output != 0 else 0.1
                        is_correct = abs(expected_output - prediction) <= tolerance
                    else:
                        # 默认使用相等比较
                        tolerance = abs(expected_output) * 0.1 if expected_output != 0 else 0.1
                        is_correct = abs(expected_output - prediction) <= tolerance
                    
                    return (1.0 if is_correct else 0.0), prediction
                else:
                    try:
                        pred_str = str(prediction).strip()
                        # 检查是否为 "NA"
                        if pred_str.upper() == "NA":
                            return 0.0, prediction
                        
                        pred_num = float(pred_str)
                        # 同样的判断逻辑
                        if judge_type == ">=":
                            is_correct = pred_num >= expected_output
                        elif judge_type == "<=":
                            is_correct = pred_num <= expected_output
                        elif judge_type == ">":
                            is_correct = pred_num > expected_output
                        elif judge_type == "<":
                            is_correct = pred_num < expected_output
                        elif judge_type == "==" or judge_type is None:
                            tolerance = abs(expected_output) * 0.1 if expected_output != 0 else 0.1
                            is_correct = abs(expected_output - pred_num) <= tolerance
                        else:
                            tolerance = abs(expected_output) * 0.1 if expected_output != 0 else 0.1
                            is_correct = abs(expected_output - pred_num) <= tolerance
                        
                        return (1.0 if is_correct else 0.0), pred_num
                    except:
                        return 0.0, prediction
            
            # 处理字符串比较 - 对于字符串，judge_type通常是"=="
            if isinstance(expected_output, str):
                pred_str = str(prediction).strip()
                expected_str = str(expected_output).strip()
                
                # 检查预测值是否为 "NA"
                if pred_str.upper() == "NA":
                    return 0.0, prediction
                
                is_correct = pred_str.lower() == expected_str.lower()
                return (1.0 if is_correct else 0.0), pred_str
            
            # 处理布尔值比较 - 对于布尔值，judge_type通常是"=="
            if isinstance(expected_output, bool):
                if isinstance(prediction, bool):
                    is_correct = expected_output == prediction
                    return (1.0 if is_correct else 0.0), prediction
                else:
                    pred_str = str(prediction).lower().strip()
                    
                    # 检查预测值是否为 "NA"
                    if pred_str.upper() == "NA":
                        return 0.0, prediction
                    
                    if pred_str in ['true', '1', 'yes']:
                        pred_bool = True
                    elif pred_str in ['false', '0', 'no']:
                        pred_bool = False
                    else:
                        return 0.0, prediction
                    is_correct = expected_output == pred_bool
                    return (1.0 if is_correct else 0.0), pred_bool
            
            return 0.0, prediction
            
        except Exception as e:
            logger.warning(f"Error calculating score: {e}")
            return 0.0, prediction

    async def evaluate_graph(self, dataset: str, graph: Callable, llm_config: dict, directory: str, validation_n: int = 1, is_test: bool = False):
        """
        Evaluate the graph and return average score
        直接使用MoSciBenchmark的评估逻辑，不需要额外的evaluation_utils
        
        Args:
            dataset: Dataset name (用于兼容性，实际使用self.name)
            graph: Graph object/function to evaluate  
            llm_config: LLM configuration (用于兼容性)
            directory: Directory to save evaluation results
            validation_n: Number of validation runs
            is_test: Whether this is a test evaluation
            
        Returns:
            Average score across validation runs
        """
        logger.info(f"Starting graph evaluation with {validation_n} validation runs")
        
        # 加载数据 - 使用现有的load_data方法
        data = await self.load_data()
        if not data:
            logger.warning("No task data loaded for evaluation.")
            return 0.0
        
        logger.info(f"Loaded {len(data)} tasks for evaluation")
        
        total_score = 0.0
        all_results = []
        
        # 运行多次验证
        for validation_round in range(validation_n):
            logger.info(f"Starting validation round {validation_round + 1}/{validation_n}")
            
            # 使用现有的evaluate_all_problems方法
            round_results = await self.evaluate_all_problems(data, graph, max_concurrent_tasks=10)
            all_results.extend(round_results)
            
            # 计算本轮得分
            if round_results:
                round_scores = [result[7] for result in round_results if result[7] is not None]  # score is at index 7
                round_avg = sum(round_scores) / len(round_scores) if round_scores else 0.0
                total_score += round_avg
                logger.info(f"Validation round {validation_round + 1} average score: {round_avg:.3f}")
            else:
                logger.warning(f"No results in validation round {validation_round + 1}")
        
        # 计算总平均得分
        final_avg_score = total_score / validation_n if validation_n > 0 else 0.0
        
        # 保存所有结果到指定目录
        if all_results:
            # 临时修改log_path以保存到指定目录
            original_log_path = self.log_path
            self.log_path = directory
            
            try:
                columns = self.get_result_columns()
                accuracy, avg_cost, total_cost = self.save_results_to_csv(all_results, columns)
                logger.info(f"Graph evaluation completed. Final average score: {final_avg_score:.3f}")
                logger.info(f"Results saved to: {directory}")
            finally:
                # 恢复原始log_path
                self.log_path = original_log_path
        
        return final_avg_score
    async def evaluate_problem(self, problem: dict, graph: Callable) -> Tuple[Any, ...]:
        """评估单个科学发现任务"""
        task_id = problem.get('id', 'unknown')
        error_message = None
        cost = 0.0
        prediction_text = ""
        
        try:
            expected_output = problem["evaluation"]
            judge_type = problem.get("judge_type", "==")  # 从任务中获取judge_type，默认为"=="
            
            # 为每个task创建独立的工作路径
            work_path = Path(self.log_path) / f"task_{task_id}"
            work_path.mkdir(parents=True, exist_ok=True)
            
            # 直接调用graph，传入任务数据、数据集路径和工作路径
            logger.debug(f"Running graph for task {task_id} with work_path: {work_path}")
            
            # Graph应该返回(prediction, cost)
            prediction_text, cost = await graph(
                task_data=problem,
                datasets_dir=str(self.datasets_dir.absolute()),
                work_path=str(work_path.absolute())
            )
            
            # 提取答案
            extracted_answer = self.extract_answer(
                prediction_text, 
                problem.get("answer_format", ""), 
                expected_output
            )

            print("extracted_answer", extracted_answer)
            # 计算得分 - 传递judge_type参数
            score, processed_prediction = self.calculate_score(expected_output, extracted_answer, judge_type)
            
            # 记录不匹配情况
            if score == 0:
                self.log_mismatch(
                    problem=f"Task {task_id}",
                    expected_output=expected_output,
                    prediction=prediction_text,
                    extracted_output=processed_prediction
                )
                error_message = f"Answer extraction failed or incorrect (judge_type: {judge_type})"
            
            return (
                task_id,
                problem.get('task_type', ''),
                problem.get('scientific_domain', ''),
                problem.get('problem_type', ''),
                prediction_text,
                expected_output,
                processed_prediction,
                score,
                cost,
                error_message
            )
            
        except Exception as e:
            error_message = f"Error evaluating task {task_id}: {type(e).__name__} - {e}"
            logger.error(error_message)
            return (
                task_id,
                problem.get('task_type', ''),
                problem.get('scientific_domain', ''),
                problem.get('problem_type', ''),
                str(e),
                problem.get("evaluation", ""),
                None,
                0.0,
                cost,
                error_message
            )

    async def evaluate_all_problems(self, data: List[dict], graph: Callable, max_concurrent_tasks: int = 10):
        """评估所有任务"""
        semaphore = asyncio.Semaphore(max_concurrent_tasks)

        async def sem_evaluate(problem):
            async with semaphore:
                try:
                    # 为科学发现任务设置较长的超时时间
                    return await asyncio.wait_for(
                        self.evaluate_problem(problem, graph), 
                        timeout=1800  # 30分钟超时
                    )
                except asyncio.TimeoutError:
                    task_id = problem.get("id", "unknown")
                    logger.error(f"Timeout evaluating task: {task_id}")
                    error_msg = "Task evaluation timed out"
                    return (
                        task_id,
                        problem.get('task_type', ''),
                        problem.get('scientific_domain', ''),
                        problem.get('problem_type', ''),
                        "TIMEOUT",
                        problem.get("evaluation", ""),
                        None,
                        0.0,
                        0.0,
                        error_msg
                    )
                except Exception as e:
                    task_id = problem.get("id", "unknown")
                    logger.error(f"Unexpected error for task {task_id}: {e}")
                    error_msg = f"Unexpected error: {type(e).__name__} - {e}"
                    return (
                        task_id,
                        problem.get('task_type', ''),
                        problem.get('scientific_domain', ''),
                        problem.get('problem_type', ''),
                        str(e),
                        problem.get("evaluation", ""),
                        None,
                        0.0,
                        0.0,
                        error_msg
                    )

        tasks = [sem_evaluate(problem) for problem in data]
        results = await tqdm_asyncio.gather(*tasks, desc=f"Evaluating {self.name} tasks", total=len(data))
        return [r for r in results if r is not None]

    def save_results_to_csv(self, results: List[Tuple[Any, ...]], columns: List[str]):
        """保存结果到CSV"""
        df = pd.DataFrame(results, columns=columns)
        
        # 计算准确率 (只计算有效结果)
        valid_results = df[df['score'].notna()]
        accuracy = float(valid_results['score'].mean()) if not valid_results.empty else 0.0
        
        # 计算总成本和平均成本
        costs = df['cost'].dropna()
        total_cost = float(costs.sum()) if not costs.empty else 0.0
        avg_cost = total_cost / len(df) if len(df) > 0 else 0.0
        
        # 保存详细结果
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mosci_results_{accuracy:.3f}_{current_time}.csv"
        output_file = Path(self.log_path) / filename
        df.to_csv(output_file, index=False, float_format='%.5f')
        
        # 按任务类型统计
        if not df.empty:
            task_type_stats = df.groupby('task_type')['score'].agg(['mean', 'count']).round(3)
            logger.info("Task Type Performance:")
            logger.info(f"\n{task_type_stats}")
        
        logger.info(f"Results saved to {output_file}")
        logger.info(f"Overall Accuracy: {accuracy:.3f}")
        logger.info(f"Total Cost: {total_cost:.3f}")
        logger.info(f"Average Cost per Task: {avg_cost:.3f}")
        
        return accuracy, avg_cost, total_cost

    async def run_evaluation(self, graph: Callable, va_list: Optional[List[int]] = None, max_concurrent_tasks: int = 10):
        """运行评估"""
        # 加载数据
        data = await self.load_data(va_list)
        if not data:
            logger.warning("No task data loaded.")
            return 0.0, 0.0, 0.0
            
        logger.info(f"Loaded {len(data)} scientific discovery tasks")
        
        # 评估所有任务
        results = await self.evaluate_all_problems(data, graph, max_concurrent_tasks)
        
        if not results:
            logger.warning("No results obtained from evaluation.")
            return 0.0, 0.0, 0.0

        # 保存结果
        columns = self.get_result_columns()
        accuracy, avg_cost, total_cost = self.save_results_to_csv(results, columns)
        
        return accuracy, avg_cost, total_cost

    async def load_data(self, va_list: Optional[List[int]] = None) -> List[dict]:
        """加载discovery_tasks.json数据"""
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                all_tasks = json.load(f)
            
            # 过滤出有效的任务 (有id和evaluation字段)
            valid_tasks = []
            for task in all_tasks:
                if isinstance(task, dict) and 'id' in task and 'evaluation' in task:
                    valid_tasks.append(task)
            
            # 如果指定了va_list，则只选择对应的任务
            if va_list is not None:
                selected_tasks = []
                for task in valid_tasks:
                    if task['id'] in va_list:
                        selected_tasks.append(task)
                return selected_tasks
            
            return valid_tasks
            
        except Exception as e:
            logger.error(f"Error loading tasks from {self.tasks_file}: {e}")
            return []