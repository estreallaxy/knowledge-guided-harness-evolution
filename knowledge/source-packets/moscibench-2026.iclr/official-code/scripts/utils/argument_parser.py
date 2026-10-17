# -*- coding: utf-8 -*-
# @Date    : 12/25/2024
# @Author  : argument parser
# @Desc    : Command line argument parsing for baseline runner

import argparse


def parse_args():
    """Parse command line arguments for baseline evaluation"""
    parser = argparse.ArgumentParser(description="Multi-Model Scientific Discovery")
    
    # Basic configuration
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Dataset name (e.g., aerial-cactus-identification, MATH, etc.)",
    )
    parser.add_argument(
        "--optimized_path",
        type=str,
        default="workspace",
        help="Root path for storing baseline results",
    )
    parser.add_argument(
        "--baseline_name",
        type=str,
        default="ReAct",
        help="Name of the baseline to use (e.g., MLE, Custom_Baseline)",
    )
    parser.add_argument(
        "--num_runs", 
        type=int, 
        default=1, 
        help="Number of independent baseline runs"
    )
    parser.add_argument(
        "--if_force_download",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Whether to enforce dataset download",
    )
    parser.add_argument(
        "--exec_model_name",
        type=str,
        default="o4-mini-2025-04-16",
        help="Model name for execution tasks",
    )
    parser.add_argument(
        "--initial_round_path",
        type=str,
        default='agents',
        help="Directory containing baseline workflows",
    )

    # Experiment configuration parameters
    parser.add_argument(
        "--include_workflow",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Whether to include workflow information in Analysis prompt",
    )
    parser.add_argument(
        "--include_domain_knowledge",
        type=lambda x: x.lower() == "true", 
        default=False,
        help="Whether to include domain knowledge information in Analysis prompt",
    )
    parser.add_argument(
        "--analysis_timeout",
        type=int,
        default=3600,
        help="Timeout for scientific analysis execution (seconds)",
    )
    parser.add_argument(
        "--max_retries",
        type=int,
        default=3,
        help="Maximum retries for code refinement",
    )

  # Reflexion (Oracle) configuration parameters
    parser.add_argument(
        "--max_trials",
        type=int,
        default=3,
        help="Maximum number of trials for Reflexion (Oracle) workflow (default: 3)",
    )
    parser.add_argument(
        "--oracle_type",
        type=str,
        choices=["llm", "simple"],
        default="llm",
        help="Oracle evaluator type: 'llm' for LLM-based evaluation, 'simple' for string matching (default: llm)",
    )

    # Best of N configuration parameters
    parser.add_argument(
        "--max_n",
        type=int,
        default=1,
        help="Maximum number of inference attempts for Best of N baseline (default: 1)",
    )

    return parser.parse_args()


def create_exp_config(args) -> dict:
    """Create experiment configuration dictionary from parsed arguments"""
    return {
        "analysis": {
            "include_workflow": args.include_workflow,
            "include_domain_knowledge": args.include_domain_knowledge,
        },
        "execution": {
            "timeout": args.analysis_timeout,
            "max_retries": args.max_retries,
        },
        "model": {
            "exec_model_name": args.exec_model_name,
        },
        "best_of_n": {
            "max_n": args.max_n  
        },
        "dataset": args.dataset,
        "baseline_name": args.baseline_name,
        "max_trials": args.max_trials, 
        "oracle_type": args.oracle_type,
        "runtime_args": vars(args),  
    }