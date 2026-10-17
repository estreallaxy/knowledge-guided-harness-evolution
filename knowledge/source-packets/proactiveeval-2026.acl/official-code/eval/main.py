import os
import sys
import logging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import UnifiedConfig
from target_generation import TargetGenerationPipeline
from target_planning_eval import TargetPlanningEvaluator
from conversation_generation import ConversationGenerator
from conversation_dialogue_eval import ConversationEvaluator, MetricsCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MainRunner:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = UnifiedConfig(config_path)
        logger.info(f"load config completed, task type: {self.config.task_config.task}")
    
    def run_target_planning_generation(self):
        logger.info("start target planning generation task")
        
        if os.path.exists(f"target_planning_generation/{self.config.get_model_name_safe(self.config.evaluated_model.model_name)}"):
            logger.info("target planning results exist, skip generation step")
            return True
        
        try:
            pipeline = TargetGenerationPipeline(self.config)
            pipeline.run(self.config.fixed_params["domains"], "all")
            logger.info("target planning generation task completed")
            return True
        except Exception as e:
            logger.error(f"target planning generation task failed: {e}")
            return False
    
    def run_target_planning_evaluation(self):
        logger.info("start target planning evaluation task")
        
        if not os.path.exists(f"target_planning_generation/{self.config.get_model_name_safe(self.config.evaluated_model.model_name)}"):
            logger.error("target planning results not exist, please run generation task first")
            return False
        
        try:
            evaluator = TargetPlanningEvaluator(self.config)
            metrics = evaluator.target_evaluation_by_domain(self.config.fixed_params["domains"])
            logger.info("target planning evaluation task completed")
            return True
        except Exception as e:
            logger.error(f"target planning evaluation task failed: {e}")
            return False
    
    def run_dialogue_guidance_generation(self):
        logger.info("start dialogue guidance generation task")
        
        if os.path.exists(f"conversation_results/{self.config.get_model_name_safe(self.config.evaluated_model.model_name)}"):
            logger.info("dialogue guidance results exist, skip generation step")
            return True
        
        try:
            generator = ConversationGenerator(self.config)
            
            result_base_dir = Path(f"{self.config.fixed_params['conversation_results_path']}/{self.config.get_model_name_safe(self.config.evaluated_model.model_name)}")
            result_base_dir.mkdir(parents=True, exist_ok=True)
            
            # 处理每个领域
            for domain in self.config.fixed_params["domains"]:
                file_domain = domain.replace("/", "_")
                test_data_file = f"{self.config.fixed_params['dataset_base_path']}/{file_domain}/eval.json"
                result_file = result_base_dir / f"{file_domain}_v{self.config.task_config.version_num}.json"
                
                logger.info(f"processing domain: {domain}")
                generator.test(test_data_file, result_file, file_domain)
            
            logger.info("dialogue guidance generation task completed")
            return True
        except Exception as e:
            logger.error(f"dialogue guidance generation task failed: {e}")
            return False
    
    def run_dialogue_guidance_evaluation(self):
        logger.info("start dialogue guidance evaluation task")
        
        if not os.path.exists(f"conversation_results/{self.config.get_model_name_safe(self.config.evaluated_model.model_name)}"):
            logger.error("dialogue guidance results not exist, please run generation task first")
            return False
        
        try:
            evaluator = ConversationEvaluator(self.config)
            metrics_calculator = MetricsCalculator()
            
            domain_metrics = []
            all_results = []
            total_guidance = 0
            total_turns = 0
            total_convs = 0
            
            for domain in self.config.fixed_params["domains"]:
                file_domain = domain.replace("/", "_")
                input_path = f"{self.config.fixed_params['conversation_results_path']}/{self.config.get_model_name_safe(self.config.evaluated_model.model_name)}/{file_domain}_v{self.config.task_config.version_num}.json"
                output_path = f"{self.config.get_output_path('dialogue_guidance')}/{file_domain}_v{self.config.task_config.version_num}.json"
                
                try:
                    results = evaluator.evaluate_conversations(input_path, output_path, file_domain)
                    all_results.extend(results)
                    
                    metrics = metrics_calculator.calculate_domain_metrics(results)
                    
                    if metrics["valid_convs"] > 0:
                        domain_metrics.append([
                            domain, 
                            metrics["avg_guidance"], 
                            metrics["avg_turns"], 
                            metrics["valid_convs"]
                        ])
                        
                        total_guidance += metrics["avg_guidance"] * metrics["valid_convs"]
                        total_turns += metrics["avg_turns"] * metrics["valid_convs"]
                        total_convs += metrics["valid_convs"]
                        
                        logger.info(f"Domain {domain}: avg_guidance={metrics['avg_guidance']:.4f}, avg_turns={metrics['avg_turns']:.2f}, convs={metrics['valid_convs']}")
                
                except Exception as e:
                    logger.error(f"Error processing domain {domain}: {e}")
                    continue
            
            combined_output_path = f"{self.config.get_output_path('dialogue_guidance')}/dialogue_guidance_v_{self.config.task_config.version_num}.json"
            evaluator._save_combined_results(all_results, combined_output_path)
            
            overall_metrics = {
                "avg_guidance": total_guidance / total_convs if total_convs > 0 else 0,
                "avg_turns": total_turns / total_convs if total_convs > 0 else 0,
                "valid_convs": total_convs
            }
            
            csv_path = f"{self.config.get_output_path('dialogue_guidance')}/metrics_summary.csv"
            metrics_calculator.save_metrics_summary(domain_metrics, overall_metrics, csv_path)
            
            type_metrics = metrics_calculator.calculate_collaboration_type_metrics(all_results)
            collaboration_csv_path = f"{self.config.get_output_path('dialogue_guidance')}/collaboration_type_metrics_summary.csv"
            metrics_calculator.save_collaboration_type_metrics_summary(type_metrics, collaboration_csv_path)
            
            logger.info(f"Overall metrics: avg_guidance={overall_metrics['avg_guidance']:.4f}, avg_turns={overall_metrics['avg_turns']:.2f}, total_convs={overall_metrics['valid_convs']}")
            
            logger.info("Collaboration Type Metrics:")
            for collab_type, metrics in type_metrics.items():
                logger.info(f"{collab_type}: avg_guidance={metrics['avg_guidance']:.4f}, avg_turns={metrics['avg_turns']:.2f}, convs={metrics['valid_convs']}")
            
            logger.info("dialogue guidance evaluation task completed")
            return True
        except Exception as e:
            logger.error(f"dialogue guidance evaluation task failed: {e}")
            return False
    
    def run(self):
        task = self.config.task_config.task
        
        if task == "target_planning":
            success1 = self.run_target_planning_generation()
            success2 = self.run_target_planning_evaluation()
            return success1 and success2
        
        elif task == "dialogue_guidance":
            success1 = self.run_dialogue_guidance_generation()
            success2 = self.run_dialogue_guidance_evaluation()
            return success1 and success2
        
        elif task == "all":
            logger.info("start all tasks")
            
            target_success1 = self.run_target_planning_generation()
            target_success2 = self.run_target_planning_evaluation()
            
            dialogue_success1 = self.run_dialogue_guidance_generation()
            dialogue_success2 = self.run_dialogue_guidance_evaluation()
            
            all_success = target_success1 and target_success2 and dialogue_success1 and dialogue_success2
            
            if all_success:
                logger.info("all tasks executed successfully")
            else:
                logger.error("executed failed")
            
            return all_success
        
        else:
            logger.error(f"unknown task type: {task}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="main runner")
    parser.add_argument("--config", type=str, default="config.yaml", help="config file path")
    
    args = parser.parse_args()
    
    try:
        runner = MainRunner(args.config)
        success = runner.run()
        
        if success:
            logger.info("all tasks executed successfully")
            sys.exit(0)
        else:
            logger.error("executed failed")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"runner initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 

# python main.py --config config.yaml