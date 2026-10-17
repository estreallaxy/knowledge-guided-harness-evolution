import os
import json
import glob
import argparse
import time  # 导入时间模块用于计时
import threading  # 添加线程模块
from concurrent.futures import ThreadPoolExecutor, as_completed  # 添加线程池
import re

from cuarewardbench.core.llm_eval import LLMEvaluator
from cuarewardbench.core.data_io import get_instruction, load_data_items, prepare_result_filenames, load_existing_results
from cuarewardbench.core.metrics_calculator import compute_and_save_metrics
from cuarewardbench.core.result_parser import parse_llm_output
from cuarewardbench.core.config import (
    DEFAULT_ANNOTATION_FILE,
    DEFAULT_PROMPT_DIR,
    DEFAULT_TRAJECTORY_ROOT,
    SUPPORTED_EVAL_MODES,
    apply_model_overrides,
    get_model_config,
    validate_eval_mode,
)


# 命令行参数解析
parser = argparse.ArgumentParser(description="Evaluate cuarewardbench trajectories")
parser.add_argument("--eval_mode", default="sewsm_thinking", help=f"evaluation mode ({', '.join(SUPPORTED_EVAL_MODES)})")
parser.add_argument("--model_config", default="qwen2p5vl_32b_tione_config", help="Model config key in cuarewardbench/core/model_config.py")
parser.add_argument("--num_items", type=int, default=0, help="Number of items to evaluate. Set to 0 to evaluate all.")
parser.add_argument("--only_metric", action="store_true", help="not evaluate, only compute metric")
parser.add_argument("--temperature", type=float, default=0.0, help="LLM temperature")
parser.add_argument("--img_scale", type=float, default=1.0, help="Image scale factor (default: 1.0)")
parser.add_argument("--output_dir", default="results/crm_results", help="Output directory for results")
parser.add_argument("--max_screenshots", type=int, default=20, help="Maximum number of screenshots to use per task (0 for all)")
parser.add_argument("--exp_suffix", default="", help="Output directory")
parser.add_argument("--reward_type", default="or_ar", help="reward type: or, ar, or_ar")
parser.add_argument("--num_workers", type=int, default=4, help="Number of parallel workers (default: 4)")
parser.add_argument("--prompt_file", default="", help="Override prompt file name (e.g., osworld_sewsm_thinking_v2.json). If empty, auto-derived from eval_mode.")
parser.add_argument("--base_url", default=None, help="Override base_url in model_config (for example, https://your-openai-compatible-endpoint/v1)")
parser.add_argument("--api_key", default=None, help="Override api_key in model_config")
parser.add_argument("--timeout", type=int, default=None, help="Override request timeout in seconds from model_config")
parser.add_argument("--annotation_file", default=str(DEFAULT_ANNOTATION_FILE), help="Path to CUARewardBench annotation JSON/JSONL")
parser.add_argument("--trajectory_root", default=str(DEFAULT_TRAJECTORY_ROOT), help="Root directory of trajectory screenshots, organized as {model_setting}/{task_type}/{task_id}")
parser.add_argument("--prompt_dir", default=str(DEFAULT_PROMPT_DIR), help="Directory containing prompt JSON files")

args = parser.parse_args()

args.eval_mode = validate_eval_mode(args.eval_mode)
if args.eval_mode == "zerogui":
    args.reward_type = "or"
elif args.eval_mode == "opencua_reflect_thinking":
    args.reward_type = "ar"
if args.prompt_file:
    args.prompt_file = args.prompt_file
else:
    args.prompt_file = f"osworld_{args.eval_mode}.json"

# 路径通过命令行显式控制；默认使用开源仓库标准目录。
PROMPT_DIR = args.prompt_dir
BASE_DIR = args.trajectory_root
JSONL_PATH = args.annotation_file

# 全局线程锁，用于保护文件写入操作
save_lock = threading.Lock()

model_config = apply_model_overrides(
    get_model_config(args.model_config),
    base_url=args.base_url,
    api_key=args.api_key,
)
if args.timeout is not None:
    model_config["timeout"] = args.timeout
    print(f"[Override] timeout = {args.timeout}s")
args.model_config_name = args.model_config
args.model_config = model_config


def evaluate_cuarewardbench():
    """评估cuarewardbench数据集"""
    # 初始化评估器
    evaluator = LLMEvaluator(
        **model_config,
        prompt_file=args.prompt_file,
        prompt_dir=PROMPT_DIR
    )
    
    # 加载数据项
    data_items = load_data_items(JSONL_PATH, args)
        
    # 准备结果文件路径
    detailed_filepath, metrics_filename = prepare_result_filenames(JSONL_PATH, args)
    
    # 加载已有结果
    existing_results, evaluated_tasks = load_existing_results(detailed_filepath)
    
    # 处理任务评估
    all_results = existing_results
    if not args.only_metric:
        results = process_tasks(
            evaluator, data_items, existing_results, evaluated_tasks,
            detailed_filepath
        )
        # 注意：不需要合并results，因为existing_results已经通过增量保存包含了所有新结果
        # results只是用于统计和返回值，实际数据已经在existing_results中了
        all_results = existing_results
    # 从llm_output中解析出traj-level reward和action reward
    all_results = parse_llm_output(all_results, evaluator, args)
    # 计算并保存指标
    compute_and_save_metrics(
        all_results,
        detailed_filepath, metrics_filename, args
    )


def process_single_task_wrapper(data, evaluated_tasks, detailed_filepath, existing_results, total_tasks, current_index):
    """单个任务处理的包装函数，用于多线程执行"""
    model_setting = data["model_setting"]
    task_type = data["task_type"]
    task_id = data["task_id"]
    
    # 检查是否已评估过
    task_key = (model_setting, task_id)
    if task_key in evaluated_tasks:
        print(f"Skipping already evaluated task: {model_setting}/{task_id}")
        return None
    
    # 使用黄色加粗文本使进度信息更醒目
    print(f"\033[1;33m[Thread-{threading.current_thread().name}] Processing task {current_index}/{total_tasks}: {task_id}\033[0m")
    
    # 为每个线程创建独立的evaluator实例（确保线程安全）
    evaluator = LLMEvaluator(
        **model_config,
        prompt_file=args.prompt_file,
        prompt_dir=PROMPT_DIR
    )
    
    try:
        # 构建测试轨迹
        test_trajectory = prepare_test_trajectory(model_setting, task_type, task_id)
        
        # 构建任务配置
        task_config = {
            "instruction": data.get("instruction") or get_instruction(task_type, task_id)
        }
        
        # 评估单个任务
        result = evaluate_single_task(
            evaluator, task_config, test_trajectory, 
            model_setting, task_type, task_id, data
        )
        
        # 增量保存：每完成一个任务就立即保存
        if result:
            with save_lock:
                existing_results.append(result)
                save_incremental_results(detailed_filepath, existing_results)
        
        return result
    except Exception as e:
        print(f"\033[1;31mError processing task {task_id} in thread {threading.current_thread().name}: {str(e)}\033[0m")
        return None


def process_tasks(evaluator, data_to_process, existing_results, evaluated_tasks, 
                 detailed_filepath):
    """处理所有任务评估（多线程版本）"""
    results = []
    total_tasks = len(data_to_process)
    
    print(f"\n\033[1;32m{'='*60}\033[0m")
    print(f"\033[1;32mStarting parallel evaluation with {args.num_workers} workers\033[0m")
    print(f"\033[1;32mTotal tasks to process: {total_tasks}\033[0m")
    print(f"\033[1;32m{'='*60}\033[0m\n")
    
    # 使用线程池并行处理任务
    with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        # 提交所有任务
        future_to_data = {}
        for idx, data in enumerate(data_to_process, 1):
            future = executor.submit(
                process_single_task_wrapper,
                data, evaluated_tasks, detailed_filepath, 
                existing_results, total_tasks, idx
            )
            future_to_data[future] = (data, idx)
        
        # 收集结果（仅用于统计，不再保存）
        completed = 0
        for future in as_completed(future_to_data):
            completed += 1
            data, idx = future_to_data[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    print(f"\033[1;36m✓ Completed {completed}/{total_tasks} tasks\033[0m")
            except Exception as e:
                task_id = data.get("task_id", "unknown")
                print(f"\033[1;31m✗ Task {task_id} generated an exception: {str(e)}\033[0m")
    
    print(f"\n\033[1;32m{'='*60}\033[0m")
    print(f"\033[1;32mAll tasks completed! Successfully evaluated: {len(results)}/{total_tasks}\033[0m")
    print(f"\033[1;32m{'='*60}\033[0m\n")
    
    return results

def prepare_test_trajectory(model_setting, task_type, task_id):
    """准备测试轨迹（截图列表）"""
    task_dir = os.path.join(BASE_DIR, model_setting, task_type, task_id)
    screenshot_files = glob.glob(os.path.join(task_dir, "step_*.png"))
    screenshot_files.sort(key=lambda x: int(os.path.basename(x).split('_')[1]))

    task_dir_marker = os.path.join(f"{BASE_DIR}_w_action", model_setting, task_type, task_id)
    screenshot_files_marker = glob.glob(os.path.join(task_dir_marker, "step_*.png"))
    screenshot_files_marker.sort(key=lambda x: int(os.path.basename(x).split('_')[1]))
    if not screenshot_files_marker:
        screenshot_files_marker = list(screenshot_files)

    # 限制最大截图数量
    if args.max_screenshots > 0:
        screenshot_files = screenshot_files[-args.max_screenshots:]

    # 查找轨迹文件
    traj_files = glob.glob(os.path.join(task_dir, "traj*.jsonl"))
    if not traj_files:
        print(f"警告: 在目录 {task_dir} 中没有找到轨迹文件")
        raise ValueError("轨迹文件不存在")
    
    actions = []
    traj_file = traj_files[0]
    # 读取轨迹文件
    with open(traj_file, 'r', encoding='utf-8') as f:
        jsonl_lines = f.readlines()

    # 处理每个action，将其绘制到下一个步骤的图片上
    for i in range(len(jsonl_lines)):  
        try:
            data = json.loads(jsonl_lines[i])
            action_text = data.get('action', '')
            if isinstance(action_text, dict):
                action_text = action_text.get('command', '')
            
            # import pdb; pdb.set_trace()
            # 使用正则表达式移除所有'''包裹的内容
            action_text = re.sub(r"'''.*?'''", "", action_text, flags=re.DOTALL)
            action_text = action_text.replace('import pyautogui', '').replace("import time","").replace("\n\n","").replace("\n\n","")
            # 移除以#开头到行尾的注释
            action_text = re.sub(r"#.*?\n", "", action_text)
            actions.append(action_text)
        except json.JSONDecodeError:
            print(f"JSON解析错误，跳过步骤 {i+1}")

    test_traj = {
        "actions": actions,
        "screenshots": screenshot_files,
        "screenshots_marker": screenshot_files_marker
        }
    return test_traj

def evaluate_single_task(evaluator, task_config, test_trajectory, 
                        model_setting, task_type, task_id, data):
    """评估单个任务"""
    gt_result = int(data["result"])
    step_num = int(data["step_num"])
    comments = data["comments"]
    instruction = data["instruction"]
    categories = [
        "key_bad_in_fail",
        "key_good_before_bad_in_fail",
        "key_bad_in_success",
        "key_good_after_bad_in_success",
        "key_good_in_success",
        "redundant_in_success",
    ]
    for category in categories:
        if category not in data:
            data[category] = []

    action_annos = {
        "key_bad_in_fail" : data["key_bad_in_fail"],
        "key_good_before_bad_in_fail": data["key_good_before_bad_in_fail"],
        "key_good_in_success": data["key_good_in_success"],
        "key_bad_in_success": data["key_bad_in_success"],
        "key_good_after_bad_in_success": data["key_good_after_bad_in_success"],
        "redundant_in_success": data["redundant_in_success"],
    }
    # 将所有action_annos中的列表合并成一个列表
    action_annos_list = []
    for action_list in action_annos.values():
        if isinstance(action_list, list):
            action_annos_list.extend(action_list)

    try:
        start_time = time.time()
        print(f'===================\\"Evaluated {task_id}, {model_setting} ========================')
        eval_output_dict = dict()
        if args.eval_mode == "opencua_reflect_thinking":
            for action in action_annos_list:
                eval_output = evaluator.evaluate_task_step(task_config, test_trajectory, action, eval_mode=args.eval_mode, img_scale=args.img_scale)
                action = str(action)
                eval_output_dict[action] = eval_output["llm_output"]
            llm_output = eval_output_dict
        elif args.eval_mode in ["sewsm_targetar"]:
            for action in action_annos_list:
                eval_output = evaluator.evaluate_task(task_config, test_trajectory, action, eval_mode=args.eval_mode, img_scale=args.img_scale)
                action = str(action)
                eval_output_dict[action] = eval_output["llm_output"]
            llm_output = eval_output_dict
        else:
            eval_output = evaluator.evaluate_task(task_config, test_trajectory, eval_mode=args.eval_mode, img_scale=args.img_scale)
            llm_output = eval_output.get("llm_output", "")
        eval_time = time.time() - start_time        
        # 构建结果记录
        result = {
            "task_id": task_id,
            "task_type": task_type,
            "model_setting": model_setting,
            "reward_fn": model_config['model'],
            "step_num": step_num,
            "gt": gt_result,
            "pred": -2,
            "instruction": instruction,
            "llm_output": llm_output,
            "action_annos": action_annos,
            "action_reward_list": [],
            "eval_time": eval_time,
            "comments": comments
        }
        
        print(llm_output)
        print(f"Evaluated {task_id}: GT={gt_result}, Time={eval_time:.2f}s")
        print(f"========================================================================")
        
        return result
    
    except Exception as e:
        print(f"Error evaluating task {task_id}: {str(e)}")
        return None

def save_incremental_results(filepath, results):
    """增量保存结果到文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving incremental results: {str(e)}")


if __name__ == "__main__":
    evaluate_cuarewardbench()