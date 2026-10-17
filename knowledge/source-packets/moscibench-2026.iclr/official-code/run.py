# -*- coding: utf-8 -*-
# @Date    : 08/28/2025
# @Author  : baseline runner
# @Desc    : Static baseline evaluation runner (no optimization, only evaluation)

import os
from datetime import datetime

from scripts.utils.baseline_runner import BaselineRunner
from scripts.utils.argument_parser import parse_args, create_exp_config
from scripts.async_llm import LLMsConfig
from scripts.trajectory import TrajectoryRecorder
from scripts.logs import logger
from scripts.utils.workspace_utils import setup_baseline_workflow_directories
from scripts.utils.download_data import download



def main():
    """Main function for baseline evaluation"""
    args = parse_args()
    args.dataset = args.dataset.replace("-", "_")  
    download(args.dataset)  
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create trajectory file path
    os.environ["TRAJECTORY_FILE"] = f"trajectory/{args.dataset}/baseline_{args.baseline_name}_{timestamp}.jsonl"
    
    # Create trajectory recorder
    recorder = TrajectoryRecorder.instance()

    try:
        # Create experiment configuration
        exp_config = create_exp_config(args)
        
        # Record baseline evaluation start
        recorder.record({
            "event": "baseline_start",
            "dataset": args.dataset,
            "baseline": args.baseline_name,
            "timestamp": datetime.now().isoformat(),
            "args": vars(args)
        })

        # Load model configuration
        models_config = LLMsConfig.default()
        exec_llm_config = models_config.get(args.exec_model_name)
        if exec_llm_config is None:
            raise ValueError(
                f"The execution model '{args.exec_model_name}' was not found in the configuration. "
                f"Please add it to the configuration or specify a valid model."
            )

        # Setup baseline workflow directories
        setup_baseline_workflow_directories(
            args.dataset, 
            args.optimized_path, 
            args.initial_round_path, 
            args.baseline_name
        )
        
        # Record baseline runner initialization
        recorder.record({
            "event": "baseline_runner_init",
            "exec_model": args.exec_model_name,
            "num_runs": args.num_runs,
            "baseline_name": args.baseline_name,
            "baseline_path": args.initial_round_path,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create baseline runner
        baseline_runner = BaselineRunner(
            dataset=args.dataset,
            exec_llm_config=exec_llm_config,
            optimized_path=args.optimized_path,
            baseline_name=args.baseline_name,
            exp_config=exp_config,
        )
        
        # Record evaluation start
        recorder.record({
            "event": "baseline_evaluation_start",
            "mode": "Baseline",
            "baseline_name": args.baseline_name,
            "timestamp": datetime.now().isoformat()
        })
        
        # Run baseline evaluation(s)
        if args.num_runs > 1:
            logger.info(f"Running {args.num_runs} baseline evaluations for statistical analysis...")
            scores = baseline_runner.run_multiple_baselines(num_runs=args.num_runs)
            
            # Record results
            recorder.record({
                "event": "baseline_multiple_results",
                "scores": scores,
                "num_runs": args.num_runs,
                "baseline_name": args.baseline_name,
                "timestamp": datetime.now().isoformat()
            })
        else:
            logger.info("Running single baseline evaluation...")
            score = baseline_runner.run_baseline()
            
            # Record results
            recorder.record({
                "event": "baseline_single_result",
                "score": score,
                "baseline_name": args.baseline_name,
                "timestamp": datetime.now().isoformat()
            })
        
        # Record completion
        recorder.record({
            "event": "baseline_evaluation_complete",
            "mode": "Baseline",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info("Baseline evaluation completed successfully!")
        
    except Exception as e:
        # Record error
        recorder.record({
            "event": "error",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat()
        })
        logger.error(f"Baseline evaluation failed: {e}")
        raise
        
    finally:
        # Record end
        recorder.record({
            "event": "baseline_end",
            "timestamp": datetime.now().isoformat()
        })
        
        # Close recorder
        recorder.close()
        print(f"Baseline trajectory saved to: {os.environ['TRAJECTORY_FILE']}")


if __name__ == "__main__":
    main()

