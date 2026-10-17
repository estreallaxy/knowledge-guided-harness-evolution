# -*- coding: utf-8 -*-
# @Date    : 12/25/2024
# @Author  : baseline runner utils
# @Desc    : BaselineRunner class and related functionality

import os
import asyncio
import time
import traceback
import json
import csv
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from scripts.utils.evaluation_utils import EvaluationUtils
from scripts.utils.graph_utils import GraphUtils
from scripts.logs import logger


class BaselineRunner:
    """
    Benchmark for LLM agent for multi-modal scientific discovery.
    """
    
    def __init__(
        self,
        dataset: str,
        exec_llm_config,
        optimized_path: str = None,
        baseline_name: str = "ReAct",
        exp_config: Dict = None,
    ) -> None:
        """
        Initialize the baseline runner
        
        Args:
            dataset: Dataset name
            exec_llm_config: Configuration for execution LLM
            optimized_path: Root path for storing results
            baseline_name: Name of the baseline to use (e.g., "ReAct")
            exp_config: Experiment configuration dictionary
        """
        self.execute_llm_config = exec_llm_config
        self.dataset = dataset
        self.baseline_name = baseline_name
        self.exp_config = exp_config or {}
        
        self.root_path = f"{optimized_path}/{self.baseline_name}/{self.dataset}"
        
        # Initialize utility classes
        self.graph_utils = GraphUtils(self.root_path)
        self.evaluation_utils = EvaluationUtils(self.root_path)
        
        # Graph will be loaded during run
        self.graph = None

    def run_baseline(self, run_id: int = 1) -> float:
        """
        Run the baseline evaluation on the static initial graph
        
        Args:
            run_id: ID of the current run (for logging purposes)
            
        Returns:
            Average score from validation runs
        """
        logger.info("=" * 60)
        logger.info(f"Starting Baseline Evaluation - Run {run_id}")
        logger.info("=" * 60)
        logger.info(f"Dataset: {self.dataset}")
        logger.info(f"Baseline: {self.baseline_name}")
        logger.info(f"Root Path: {self.root_path}")
        
        # Create event loop for async execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the baseline evaluation
            avg_score = loop.run_until_complete(self._run_baseline_async(run_id))
            
            logger.info("=" * 60)
            logger.info(f"Baseline Evaluation Run {run_id} Completed")
            logger.info(f"Final Average Score: {avg_score}")
            logger.info("=" * 60)
            
            return avg_score
            
        except Exception as e:
            logger.error(f"Error during baseline evaluation run {run_id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        finally:
            loop.close()

    async def _run_baseline_async(self, run_id: int) -> float:
        """
        Async implementation of baseline evaluation
        
        Args:
            run_id: ID of the current run
            
        Returns:
            Average score from validation runs
        """
        round_num = 1  # Always use round 1 for baseline
        graph_path = f"{self.root_path}/workflows"
        

        exp_suffix = self._generate_exp_config_suffix()
        
        # Create directory for baseline results (with exp_config and run_id suffix)
        directory_name = f"{round_num}_run_{run_id}_{exp_suffix}"
        directory = self.graph_utils.create_round_directory(graph_path, directory_name)
        logger.info(f"Created baseline directory: {directory}")

  
        self._save_experiment_config(directory, run_id)

        # Load the initial static graph
        try:
            self.graph = self.graph_utils.load_graph(round_num, graph_path)
            logger.info("Successfully loaded initial static graph")
        except Exception as e:
            logger.error(f"Failed to load initial graph: {e}")
            raise
        
        # Run evaluation with initial=True flag (same as first round in optimizer)
        logger.info(f"Starting baseline evaluation...")
        start_time = time.time()
        
        avg_score = await self.evaluation_utils.evaluate_graph(
            dataset=self.dataset,
            graph=self.graph,
            llm_config=self.execute_llm_config,
            directory=directory,
            validation_n=1,  # Single evaluation per run
            is_test=True,
            exp_config=self.exp_config  # 传递实验配置
        )
        
        end_time = time.time()
        evaluation_time = end_time - start_time
        
        logger.info(f"Evaluation completed in {evaluation_time:.2f} seconds")
        logger.info(f"Average score: {avg_score}")
        
        return avg_score

    def run_multiple_baselines(self, num_runs: int = 3) -> List[float]:
        """
        Run baseline evaluation multiple times to get statistical significance
        
        Args:
            num_runs: Number of independent baseline runs
            
        Returns:
            List of average scores from each run
        """
        logger.info(f"Running {num_runs} independent baseline evaluations...")
        
        scores = []
        last_run_directory = None  # 记录最后一个运行目录
        
        for run_idx in range(num_runs):
            logger.info(f"\n--- Baseline Run {run_idx + 1}/{num_runs} ---")
            
            try:
                score = self.run_baseline(run_id=run_idx + 1)
                scores.append(score)
                logger.info(f"Run {run_idx + 1} completed with score: {score}")
                
                # 记录最后一个运行目录
                if run_idx == num_runs - 1:  # 最后一次运行
                    exp_suffix = self._generate_exp_config_suffix()
                    directory_name = f"1_run_{run_idx + 1}_{exp_suffix}"
                    last_run_directory = os.path.join(
                        f"{self.root_path}/workflows", 
                        f"round_{directory_name}"
                    )
                
                # Add delay between runs to avoid potential resource conflicts
                if run_idx < num_runs - 1:
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"Run {run_idx + 1} failed: {e}")
                scores.append(None)
        
        # Calculate statistics
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            avg_score = sum(valid_scores) / len(valid_scores)
            min_score = min(valid_scores)
            max_score = max(valid_scores)
            
            # 计算标准差
            std_dev = 0.0
            if len(valid_scores) > 1:
                std_dev = (sum((s - avg_score) ** 2 for s in valid_scores) / len(valid_scores)) ** 0.5
            
            logger.info("\n" + "=" * 60)
            logger.info("BASELINE SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Baseline: {self.baseline_name}")
            logger.info(f"Dataset: {self.dataset}")
            logger.info(f"Successful runs: {len(valid_scores)}/{num_runs}")
            logger.info(f"Average score: {avg_score:.4f}")
            logger.info(f"Min score: {min_score:.4f}")
            logger.info(f"Max score: {max_score:.4f}")
            if len(valid_scores) > 1:
                logger.info(f"Standard deviation: {std_dev:.4f}")
            logger.info("=" * 60)
            
            # 保存统计信息到CSV文件
            self._save_baseline_summary_csv(
                last_run_directory, 
                valid_scores, 
                avg_score, 
                min_score, 
                max_score, 
                std_dev, 
                num_runs
            )
        
        return scores

    def _generate_exp_config_suffix(self) -> str:
        """
        根据实验配置生成目录名称后缀
        
        Returns:
            配置相关的后缀字符串
        """
        analysis_config = self.exp_config.get("analysis", {})
        execution_config = self.exp_config.get("execution", {})
        best_of_n_config = self.exp_config.get("best_of_n", {})  # 🔄 [NEW] 添加best_of_n配置
        
        suffix_parts = []
        
        # 🔄 [NEW] 添加模型名称前缀
        model_name = self._extract_short_model_name()
        if model_name:
            suffix_parts.append(model_name)
        
        # Analysis配置部分
        if analysis_config.get("include_workflow", False):
            suffix_parts.append("wf")  # workflow
        if analysis_config.get("include_domain_knowledge", False):
            suffix_parts.append("dk")  # domain_knowledge
            
        # 如果都没有启用，添加baseline标记
        if not any([analysis_config.get("include_workflow", False), 
                    analysis_config.get("include_domain_knowledge", False)]):
            suffix_parts.append("baseline")
        
        # 🔄 [FIXED] 对Reflexion baseline，添加trial个数描述
        if self.baseline_name.lower() == "reflexion":
            # 优先从execution_config中获取max_trials
            max_trials = execution_config.get("max_trials")
            if max_trials is None:
                # 备选：从runtime_args中获取
                max_trials = self.exp_config.get("runtime_args", {}).get("max_trials")
            
            # 如果还是找不到，使用默认值3
            if max_trials is None:
                max_trials = 3
                
            # 总是添加trial个数，不管是什么值
            suffix_parts.append(f"trial{max_trials}")
        
        # 🔄 [NEW] 对ReAct_BoN baseline，添加max_n参数描述
        elif self.baseline_name.lower() == "react_bon":
            # 优先从best_of_n_config中获取max_n
            max_n = best_of_n_config.get("max_n")
            if max_n is None:
                # 备选：从runtime_args中获取
                max_n = self.exp_config.get("runtime_args", {}).get("max_n")
            
            # 如果还是找不到，使用默认值1
            if max_n is None:
                max_n = 1
                
            # 总是添加BoN个数，不管是什么值
            suffix_parts.append(f"BoN{max_n}")
        
        # Execution配置部分（如果不是默认值）
        timeout = execution_config.get("timeout", 1800)
        if timeout != 1800:  # 非默认超时时间
            suffix_parts.append(f"t{timeout//60}m")  # 转换为分钟，如t30m
            
        # 组合后缀，如果为空则使用default
        return "_".join(suffix_parts) if suffix_parts else "default"

    def _extract_short_model_name(self) -> str:
        """
        从完整模型名称中提取简短版本
        
        Examples:
            "deepseek-ai/DeepSeek-V3" -> "DeepSeek-V3"
            "gpt-5-mini-2025-08-07" -> "gpt-5-mini"
            "o4-mini-2025-04-16" -> "o4-mini"
            "claude-3-sonnet" -> "claude-3-sonnet"
            
        Returns:
            简化的模型名称
        """
        try:
            # 从不同位置获取模型名称
            model_name = None
            
            # 方法1: 从exp_config中获取
            if 'model' in self.exp_config and 'exec_model_name' in self.exp_config['model']:
                model_name = self.exp_config['model']['exec_model_name']
            # 方法2: 从runtime_args中获取
            elif 'runtime_args' in self.exp_config and 'exec_model_name' in self.exp_config['runtime_args']:
                model_name = self.exp_config['runtime_args']['exec_model_name']
            # 方法3: 从LLM配置中获取
            elif hasattr(self.execute_llm_config, 'model_name'):
                model_name = self.execute_llm_config.model_name
            elif hasattr(self.execute_llm_config, 'model'):
                model_name = self.execute_llm_config.model
            
            if not model_name:
                return "unknown"
                
            model_name = str(model_name)
            
            import re
            
            # 🔄 [NEW] 处理 "provider/model-name" 格式，提取斜杠后的模型名称
            if '/' in model_name:
                model_name = model_name.split('/')[-1]  # 取最后一部分
            
            # 保留原始大小写，但做基本清理
            # 移除常见的日期格式 (YYYY-MM-DD, YYYYMMDD)
            model_name = re.sub(r'-\d{4}-\d{1,2}-\d{1,2}$', '', model_name)
            model_name = re.sub(r'-\d{8}$', '', model_name)
            model_name = re.sub(r'-\d{4}\d{2}\d{2}$', '', model_name)
            
            #  [MODIFIED] 保留版本号格式如 V3, v2 等，只移除简单的 -v1 格式
            model_name = re.sub(r'-v(\d+)$', r'-V\1', model_name)  # 转换为大写V格式
            
            #  [MODIFIED] 只替换不必要的特殊字符，保留连字符
            model_name = re.sub(r'[^a-zA-Z0-9\-_]', '', model_name)
            
            # 移除多余的连字符和下划线
            model_name = re.sub(r'[-_]+', '-', model_name).strip('-_')
            
            # 限制长度
            if len(model_name) > 20:  # 🔄 [MODIFIED] 增加长度限制以容纳更长的模型名
                # 对于过长的名称，尝试保留关键部分
                parts = model_name.split('-')
                if len(parts) >= 2:
                    model_name = '-'.join(parts[:2])  # 保留前两部分
                else:
                    model_name = model_name[:20]  # 截断
            
            return model_name if model_name else "unknown"
            
        except Exception as e:
            logger.warning(f"Failed to extract short model name: {e}")
            return "unknown"

    def _save_experiment_config(self, directory: str, run_id: int) -> None:
        """
        保存实验配置到结果目录
        
        Args:
            directory: 结果目录路径
            run_id: 运行ID
        """
        try:
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d")
            
            # 从exp_config中获取模型名称
            exec_model_name = self.exp_config.get('model', {}).get('exec_model_name', 
                             self.exp_config.get('runtime_args', {}).get('exec_model_name', 'unknown'))
            
            # 构建LLM配置字典
            llm_config_dict = {
                "model_name": exec_model_name,
                "provider": getattr(self.execute_llm_config, 'provider', 'unknown') if hasattr(self.execute_llm_config, '__dict__') else 'unknown',
                "temperature": getattr(self.execute_llm_config, 'temperature', 0.0) if hasattr(self.execute_llm_config, '__dict__') else 0.0,
                "max_tokens": getattr(self.execute_llm_config, 'max_tokens', 0) if hasattr(self.execute_llm_config, '__dict__') else 0,
                "base_url": getattr(self.execute_llm_config, 'base_url', None) if hasattr(self.execute_llm_config, '__dict__') else None,
            }
            
            # 移除None值
            llm_config_dict = {k: v for k, v in llm_config_dict.items() if v is not None}
            
            # 准备完整的配置信息
            config_data = {
                "experiment_info": {
                    "run_id": run_id,
                    "dataset": self.dataset,
                    "baseline_name": self.baseline_name,
                    "timestamp": timestamp,
                    "directory": directory
                },
                "exp_config": self.exp_config,
                "llm_config": llm_config_dict,
                "paths": {
                    "root_path": self.root_path,
                    "result_directory": directory
                }
            }
            
            # 保存配置文件
            config_file_path = os.path.join(directory, f"experiment_config_run_{run_id}_{timestamp}.json")
            
            with open(config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Experiment configuration saved to: {config_file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save experiment configuration: {e}")
            logger.debug(f"Error details: {type(e).__name__} - {str(e)}")

    def _save_baseline_summary_csv(self, directory: str, valid_scores: List[float], 
                                avg_score: float, min_score: float, max_score: float, 
                                std_dev: float, total_runs: int) -> None:
        """
        保存baseline统计信息到CSV文件
        
        Args:
            directory: 最后一个运行目录
            valid_scores: 有效分数列表
            avg_score: 平均分数
            min_score: 最低分数
            max_score: 最高分数
            std_dev: 标准差
            total_runs: 总运行次数
        """
        try:
            # 如果目录不存在，创建它
            if directory and not os.path.exists(directory):
                logger.warning(f"Directory does not exist: {directory}, using root path instead")
                directory = self.root_path
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exp_suffix = self._generate_exp_config_suffix()
            short_model_name = self._extract_short_model_name()
            
            # 🔄 [MODIFIED] 文件名中包含模型名称
            csv_filename = f"baseline_summary_{self.dataset}_{short_model_name}_{exp_suffix}_{timestamp}.csv"
            csv_filepath = os.path.join(directory, csv_filename)
            
            # 准备CSV数据
            summary_data = {
                'timestamp': timestamp,
                'baseline_name': self.baseline_name,
                'dataset': self.dataset,
                'model_name': short_model_name,  # 🔄 [NEW] 添加模型名称字段
                'exp_config_suffix': exp_suffix,
                'total_runs': total_runs,
                'successful_runs': len(valid_scores),
                'failed_runs': total_runs - len(valid_scores),
                'average_score': round(avg_score, 4),
                'min_score': round(min_score, 4),
                'max_score': round(max_score, 4),
                'std_deviation': round(std_dev, 4) if std_dev > 0 else 0.0,
                'individual_scores': ';'.join(map(str, [round(s, 4) for s in valid_scores])),
                'exp_config': str(self.exp_config)
            }
            
            # 写入CSV文件
            with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(summary_data.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerow(summary_data)
            
            logger.info(f"Baseline summary saved to: {csv_filepath}")
            
            # 同时保存详细的每次运行结果
            detailed_csv_filename = f"baseline_detailed_{self.dataset}_{short_model_name}_{exp_suffix}_{timestamp}.csv"
            detailed_csv_filepath = os.path.join(directory, detailed_csv_filename)
            
            with open(detailed_csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['run_id', 'score', 'status', 'baseline_name', 'dataset', 'model_name', 'timestamp']  # 🔄 [NEW] 添加model_name字段
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for i, score in enumerate(valid_scores, 1):
                    writer.writerow({
                        'run_id': i,
                        'score': round(score, 4),
                        'status': 'success',
                        'baseline_name': self.baseline_name,
                        'dataset': self.dataset,
                        'model_name': short_model_name,  # 🔄 [NEW] 添加模型名称
                        'timestamp': timestamp
                    })
            
            logger.info(f"Detailed baseline results saved to: {detailed_csv_filepath}")
            
        except Exception as e:
            logger.warning(f"Failed to save baseline summary CSV: {e}")
            logger.debug(f"Error details: {type(e).__name__} - {str(e)}")