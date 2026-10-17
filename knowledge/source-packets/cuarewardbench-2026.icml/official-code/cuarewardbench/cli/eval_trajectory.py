import os
import sys
import json
import glob
import argparse
import time
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

from cuarewardbench.core.llm_eval import LLMEvaluator
from cuarewardbench.core.config import (
    DEFAULT_PROMPT_DIR,
    REPO_ROOT,
    SUPPORTED_EVAL_MODES,
    apply_model_overrides,
    get_model_config,
    validate_eval_mode,
)


# 命令行参数解析
parser = argparse.ArgumentParser(description="Evaluate trajectories in a directory")
parser.add_argument("--traj_dir", default=None, help="Root directory containing trajectories to evaluate (single trial mode)")
parser.add_argument("--traj_dirs", default=None, help="Comma-separated list of trajectory directories to evaluate (multi-trial merged mode)")
parser.add_argument("--eval_mode", default="sewsm_thinking", help=f"evaluation mode ({', '.join(SUPPORTED_EVAL_MODES)})")
parser.add_argument("--model_config", default="qwen2p5vl_32b_tione_config", help="Model config key in cuarewardbench/core/model_config.py")
parser.add_argument("--temperature", type=float, default=0.0, help="LLM temperature")
parser.add_argument("--img_scale", type=float, default=1.0, help="Image scale factor (default: 1.0)")
parser.add_argument("--max_screenshots", type=int, default=20, help="Maximum number of screenshots to use per task (0 for all)")
parser.add_argument("--num_workers", type=int, default=4, help="Number of parallel workers (default: 4)")
parser.add_argument("--num_items", type=int, default=0, help="Number of trajectories to evaluate. Set to 0 to evaluate all.")
parser.add_argument("--skip_existing", action="store_true", default=True, help="Skip trajectories that already have result files")
parser.add_argument("--base_url", default=None, help="Override base_url in model_config")
parser.add_argument("--api_key", default=None, help="Override api_key in model_config")
parser.add_argument("--timeout", type=int, default=None, help="Override request timeout in seconds from model_config")
parser.add_argument("--prompt_file", default="", help="Override prompt file name. If empty, auto-derived from eval_mode.")
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

REPO_ROOT = str(REPO_ROOT)
PROMPT_DIR = args.prompt_dir

# 全局线程锁
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

# 从model_config中提取model_name用于文件命名
args.model_name = model_config.get("model", "unknown_model")


def scan_trajectory_dirs(root_dir):
    """扫描指定目录下的所有轨迹目录
    
    Args:
        root_dir: 轨迹根目录路径
        
    Returns:
        list: 包含轨迹信息的字典列表，每个字典包含：
            - task_type: 任务类型
            - task_id: 任务ID（轨迹目录名）
            - traj_dir: 轨迹目录完整路径
            - instruction: 从traj.jsonl读取的指令
    """
    trajectory_items = []
    skipped_count = 0
    skipped_fail_count = 0  # 新增：记录因 FAIL 被跳过的轨迹数
    
    # 遍历根目录下的所有task_type子目录
    if not os.path.exists(root_dir):
        raise ValueError(f"Root directory does not exist: {root_dir}")
    
    for task_type in os.listdir(root_dir):
        task_type_dir = os.path.join(root_dir, task_type)
        
        # 跳过非目录项
        if not os.path.isdir(task_type_dir):
            continue
        
        # 遍历task_type下的所有轨迹目录
        for task_id in os.listdir(task_type_dir):
            traj_dir = os.path.join(task_type_dir, task_id)
            
            # 跳过非目录项
            if not os.path.isdir(traj_dir):
                continue
            
            # 检查是否存在traj.jsonl
            traj_file = os.path.join(traj_dir, "traj.jsonl")
            if not os.path.exists(traj_file):
                print(f"Warning: traj.jsonl not found in {traj_dir}, skipping...")
                skipped_count += 1
                continue
            
            # 检查result.txt是否包含PENDING_FOR_RM（必需检查，确保只评估已完成的轨迹）
            result_file = os.path.join(traj_dir, "result.txt")
            if not os.path.exists(result_file):
                print(f"\033[1;33mWarning: result.txt not found in {traj_dir}, skipping...\033[0m")
                skipped_count += 1
                continue
            
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    result_content = f.read().strip()
                    if "PENDING_FOR_RM" not in result_content:
                        print(f"\033[1;33mSkipping {traj_dir}: result.txt does not contain PENDING_FOR_RM\033[0m")
                        skipped_count += 1
                        continue
            except Exception as e:
                print(f"\033[1;33mWarning: Failed to read result.txt in {traj_dir}, skipping... (Error: {str(e)})\033[0m")
                skipped_count += 1
                continue
            
            # 读取instruction（从第一行）
            try:
                with open(traj_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if not first_line:
                        print(f"\033[1;33mWarning: Empty traj.jsonl in {traj_dir}, skipping...\033[0m")
                        skipped_count += 1
                        continue
                    
                    first_data = json.loads(first_line)
                    instruction = first_data.get('instruction', '')
                    
                    if not instruction:
                        print(f"\033[1;33mWarning: No instruction found in {traj_dir}/traj.jsonl, skipping...\033[0m")
                        skipped_count += 1
                        continue
                
                # 新增：检查轨迹最后一步是否为 FAIL（超时失败），如果是则直接跳过
                # 根据统计分析，91.9% 的 FAIL 轨迹确实是失败的，跳过可节省大量评估算力
                with open(traj_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if last_line:
                            try:
                                last_data = json.loads(last_line)
                                last_action = last_data.get('action', '')
                                if last_action == 'FAIL':
                                    print(f"\033[1;35mSkipping FAIL trajectory: {task_id} (action=FAIL, likely timeout)\033[0m")
                                    skipped_fail_count += 1
                                    continue
                            except json.JSONDecodeError:
                                pass  # 解析失败则不跳过，继续正常评估
                
                # 构造轨迹数据项
                trajectory_items.append({
                    'task_type': task_type,
                    'task_id': task_id,
                    'traj_dir': traj_dir,
                    'instruction': instruction
                })
                
            except json.JSONDecodeError as e:
                print(f"\033[1;33mWarning: Invalid JSON in {traj_file}, skipping... (Error: {str(e)})\033[0m")
                skipped_count += 1
                continue
            except Exception as e:
                print(f"\033[1;33mWarning: Failed to read {traj_file}, skipping... (Error: {str(e)})\033[0m")
                skipped_count += 1
                continue
    
    print(f"\n{'='*60}")
    print(f"Found {len(trajectory_items)} valid trajectories to evaluate")
    if skipped_count > 0:
        print(f"\033[1;33mSkipped {skipped_count} invalid/incomplete trajectories\033[0m")
    if skipped_fail_count > 0:
        print(f"\033[1;35mSkipped {skipped_fail_count} FAIL trajectories (action=FAIL, directly marked as failed)\033[0m")
    print(f"{'='*60}\n")
    
    return trajectory_items


def prepare_trajectory_from_dir(traj_dir):
    """从轨迹目录准备测试轨迹数据
    
    Args:
        traj_dir: 轨迹目录路径
        
    Returns:
        dict: 包含actions和screenshots的轨迹数据
    """
    # 查找step_reset_*.png（初始状态截图）
    reset_screenshots = glob.glob(os.path.join(traj_dir, "step_reset_*.png"))
    
    # 查找所有step_*.png截图（不包括step_reset_*.png）
    # 使用字典来处理step_id重复的情况，只保留每个step_id的最后一个（参考traj2train.py）
    action_screenshots_dict = {}
    for f in glob.glob(os.path.join(traj_dir, "step_*.png")):
        # 排除step_reset_开头的文件
        if not os.path.basename(f).startswith("step_reset_"):
            # 提取step_id
            step_id = int(os.path.basename(f).split('_')[1].split('.')[0])
            # 如果step_id已存在，会被覆盖（保留最后一个）
            action_screenshots_dict[step_id] = f
    
    # 按step_id排序，转换为列表
    action_screenshots = [action_screenshots_dict[k] for k in sorted(action_screenshots_dict.keys())]
    
    # 组合截图列表：reset截图在最前面，然后是action截图
    screenshot_files = reset_screenshots + action_screenshots
    
    # 限制最大截图数量（注意：reset截图始终保留，只限制action截图）
    if args.max_screenshots > 0 and len(action_screenshots) > args.max_screenshots:
        # 保留reset截图 + 最后N张action截图
        screenshot_files = reset_screenshots + action_screenshots[-args.max_screenshots:]
    
    # 读取traj.jsonl获取actions
    traj_file = os.path.join(traj_dir, "traj.jsonl")
    actions = []
    
    with open(traj_file, 'r', encoding='utf-8') as f:
        jsonl_lines = f.readlines()
    
    # 处理每个action
    for i in range(len(jsonl_lines)):
        try:
            data = json.loads(jsonl_lines[i])
            action_text = data.get('action', '')
            if isinstance(action_text, dict):
                action_text = action_text.get('command', '')
            
            # 清理action文本
            action_text = re.sub(r"'''.*?'''", "", action_text, flags=re.DOTALL)
            action_text = action_text.replace('import pyautogui', '').replace("import time", "")
            action_text = action_text.replace("\\n\\n", "").replace("\\n\\n", "")
            action_text = re.sub(r"#.*?\\n", "", action_text)
            actions.append(action_text)
        except json.JSONDecodeError:
            print(f"JSON parsing error at line {i+1} in {traj_file}, skipping...")
    
    test_traj = {
        "actions": actions,
        "screenshots": screenshot_files,
        "screenshots_marker": screenshot_files  # 使用相同的截图列表
    }
    
    return test_traj


def evaluate_single_trajectory(evaluator, traj_item):
    """评估单个轨迹
    
    Args:
        evaluator: LLMEvaluator实例
        traj_item: 轨迹信息字典
        
    Returns:
        dict: 评估结果
    """
    traj_dir = traj_item['traj_dir']
    task_id = traj_item['task_id']
    instruction = traj_item['instruction']
    
    try:
        # 准备轨迹数据
        test_trajectory = prepare_trajectory_from_dir(traj_dir)
        
        # 构建任务配置
        task_config = {
            "instruction": instruction
        }
        
        # 评估
        start_time = time.time()
        eval_output = evaluator.evaluate_task(
            task_config, 
            test_trajectory, 
            eval_mode=args.eval_mode, 
            img_scale=args.img_scale
        )
        eval_time = time.time() - start_time
        
        llm_output = eval_output.get("llm_output", "")
        
        # 解析预测结果
        prediction = parse_prediction(llm_output, args.eval_mode)
        
        # 构建结果
        result = {
            "task_id": task_id,
            "task_type": traj_item['task_type'],
            "instruction": instruction,
            "prediction": prediction,
            "llm_output": llm_output,
            "eval_time": eval_time,
            "model": args.model_name,
            "eval_mode": args.eval_mode
        }
        
        return result
        
    except Exception as e:
        print(f"\033[1;31mError evaluating trajectory {task_id}:\033[0m")
        traceback.print_exc()
        raise


def parse_prediction(llm_output, eval_mode):
    """解析LLM输出得到预测结果
    
    Args:
        llm_output: LLM的原始输出
        eval_mode: 评估模式
        
    Returns:
        int or dict: 预测结果（0或1，或包含详细信息的字典）
    """
    try:
        if eval_mode == "zerogui":
            # 简单的0/1预测
            completion_pattern = r'(?:SCORE|[Ss]core)(?:\*\*)?[:]?\s*(?:\*\*)?(?:\[)?([0-9]+)(?:\])?'
            completion_matches = list(re.finditer(completion_pattern, llm_output, re.IGNORECASE))
            
            if completion_matches:
                last_match = completion_matches[-1]
                success_text = float(last_match.group(1))
                return 1 if success_text == 1.0 else 0
            else:
                return -2  # 解析失败
                
        elif 'sewsm' in eval_mode:
            # 解析sewsm格式的输出
            import ast
            
            res_dict = None
            
            if '<res_dict>' in llm_output:
                try:
                    res_dict_str = llm_output.split('<res_dict>')[1].split('</res_dict>')[0].strip()
                    res_dict_str = res_dict_str.replace('<|end_of_box|>', '')
                    if not res_dict_str.startswith('{'):
                        res_dict_str = '{' + res_dict_str
                    if not res_dict_str.endswith('}'):
                        res_dict_str = res_dict_str + '}'
                    res_dict_str = res_dict_str.replace("true", "True").replace("false", "False")
                    res_dict_str = res_dict_str.replace("null", "None")
                    res_dict = ast.literal_eval(res_dict_str)
                except Exception:
                    # C类容错：<res_dict>存在但JSON被截断，尝试用正则提取Correctness
                    raw = llm_output.split('<res_dict>')[1]
                    correctness_match = re.search(
                        r'["\']?Correctness["\']?\s*:\s*(True|False|true|false)',
                        raw
                    )
                    if correctness_match:
                        return 1 if correctness_match.group(1).lower() == 'true' else 0
                    return -2
            
            if res_dict is None and '```json' in llm_output and 'Correctness' in llm_output.split('```json')[-1].split('```')[0].strip():
                res_dict_str = llm_output.split('```json')[-1].split('```')[0].strip()
                res_dict_str = res_dict_str.replace("true", "True").replace("false", "False")
                res_dict_str = res_dict_str.replace("null", "None")
                try:
                    res_dict = ast.literal_eval(res_dict_str)
                except Exception:
                    pass
            
            if res_dict is None:
                # B类容错：增加多种Correctness格式的匹配
                # 1. 带引号的精确匹配（原逻辑）
                if '"Correctness": True' in llm_output or "'Correctness': True" in llm_output:
                    return 1
                elif '"Correctness": False' in llm_output or "'Correctness': False" in llm_output:
                    return 0
                
                # 2. 正则容错匹配：无引号、不同空格、大小写变体
                correctness_match = re.search(
                    r'["\']?Correctness["\']?\s*[:=]\s*["\']?(True|False|true|false)["\']?',
                    llm_output
                )
                if correctness_match:
                    return 1 if correctness_match.group(1).lower() == 'true' else 0
                
                # 3. 自然语言模式匹配：如 "the correctness is false", "correctness = false"
                nl_match = re.search(
                    r'(?:the\s+)?correctness\s+(?:is|should\s+be|=)\s*(true|false)',
                    llm_output,
                    re.IGNORECASE
                )
                if nl_match:
                    return 1 if nl_match.group(1).lower() == 'true' else 0
                
                return -2
            
            # 返回完整的res_dict作为预测结果
            if 'Correctness' in res_dict:
                return res_dict
            else:
                return -2
                
        else:
            # 其他模式暂不支持
            return -2
            
    except Exception as e:
        print(f"Error parsing prediction: {str(e)}")
        return -2


def save_trajectory_result(traj_dir, result, model_name, eval_mode):
    """保存单个轨迹的评估结果到其目录下
    
    Args:
        traj_dir: 轨迹目录路径
        result: 评估结果字典
        model_name: 模型名称
        eval_mode: 评估模式
    """
    result_file = os.path.join(traj_dir, f"result_{model_name}_{eval_mode}.json")
    
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved result to {result_file}")
    except Exception as e:
        print(f"Error saving result to {result_file}: {str(e)}")
        raise


def process_single_trajectory_wrapper(traj_item, total_tasks, current_index):
    """单个轨迹处理的包装函数，用于多线程执行"""
    task_id = traj_item['task_id']
    traj_dir = traj_item['traj_dir']
    
    # 记录开始时间
    start_time = time.time()
    
    # 检查是否需要跳过已有结果
    result_file = os.path.join(traj_dir, f"result_{args.model_name}_{args.eval_mode}.json")
    if args.skip_existing and os.path.exists(result_file):
        # 读取结果文件，检查prediction是否为-2（解析失败）
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                existing_result = json.load(f)
                prediction = existing_result.get('prediction', None)
                
                # 如果prediction为-2，说明之前解析失败，需要重新评估
                if prediction == -2:
                    print(f"\033[1;33m⚠ Re-evaluating trajectory {task_id} (previous prediction was -2: parse failed)\033[0m")
                else:
                    print(f"Skipping already evaluated trajectory: {task_id}")
                    return None
        except Exception as e:
            # 如果读取失败，重新评估
            print(f"\033[1;33m⚠ Re-evaluating trajectory {task_id} (failed to read existing result: {str(e)})\033[0m")
    
    # 使用黄色加粗文本显示进度
    print(f"\033[1;33m[Thread-{threading.current_thread().name}] Processing trajectory {current_index}/{total_tasks}: {task_id}\033[0m")
    
    # 为每个线程创建独立的evaluator实例
    evaluator = LLMEvaluator(
        **model_config,
        prompt_file=args.prompt_file,
        prompt_dir=PROMPT_DIR
    )
    
    try:
        # 评估轨迹
        result = evaluate_single_trajectory(evaluator, traj_item)
        
        # 保存结果到轨迹目录
        if result:
            with save_lock:
                save_trajectory_result(traj_dir, result, args.model_name, args.eval_mode)
        
        # 计算并打印耗时
        elapsed_time = time.time() - start_time
        print(f"\033[1;32m[Thread-{threading.current_thread().name}] Finished {task_id} in {elapsed_time:.2f}s\033[0m")
        
        return result
        
    except Exception as e:
        # 计算并打印耗时（即使失败也打印）
        elapsed_time = time.time() - start_time
        print(f"\033[1;31m{'='*80}\033[0m")
        print(f"\033[1;31mError processing trajectory {task_id} in thread {threading.current_thread().name} (elapsed: {elapsed_time:.2f}s)\033[0m")
        print(f"\033[1;31m{'='*80}\033[0m")
        traceback.print_exc()
        print(f"\033[1;31m{'='*80}\033[0m")
        raise


def process_all_trajectories(trajectory_items):
    """处理所有轨迹评估（多线程版本）"""
    results = []
    total_tasks = len(trajectory_items)
    
    print(f"\n\033[1;32m{'='*60}\033[0m")
    print(f"\033[1;32mStarting parallel evaluation with {args.num_workers} workers\033[0m")
    print(f"\033[1;32mTotal trajectories to process: {total_tasks}\033[0m")
    print(f"\033[1;32m{'='*60}\033[0m\n")
    
    # 进度统计
    progress_lock = threading.Lock()
    progress_stats = {
        "completed": 0,
        "success": 0,       # prediction != -2 且 result 不为 None
        "failed": 0,        # 异常
        "skipped": 0,       # skip_existing 跳过的（result 为 None）
        "parse_fail": 0,    # prediction == -2
        "start_time": time.time(),
    }
    
    def print_progress(task_id, status):
        """打印带进度条和统计信息的进度"""
        with progress_lock:
            stats = progress_stats
            completed = stats["completed"]
            elapsed = time.time() - stats["start_time"]
            
            # 计算进度百分比和进度条
            pct = completed / total_tasks * 100 if total_tasks > 0 else 0
            bar_len = 30
            filled = int(bar_len * completed / total_tasks) if total_tasks > 0 else 0
            bar = '█' * filled + '░' * (bar_len - filled)
            
            # 计算 ETA
            if completed > 0:
                avg_time = elapsed / completed
                eta_sec = avg_time * (total_tasks - completed)
                eta_min, eta_s = divmod(int(eta_sec), 60)
                eta_h, eta_min = divmod(eta_min, 60)
                eta_str = f"{eta_h}h{eta_min:02d}m{eta_s:02d}s" if eta_h > 0 else f"{eta_min}m{eta_s:02d}s"
            else:
                eta_str = "calculating..."
            
            elapsed_min, elapsed_s = divmod(int(elapsed), 60)
            elapsed_h, elapsed_min = divmod(elapsed_min, 60)
            elapsed_str = f"{elapsed_h}h{elapsed_min:02d}m{elapsed_s:02d}s" if elapsed_h > 0 else f"{elapsed_min}m{elapsed_s:02d}s"
            
            # 成功率（基于已评估的，不含跳过的）
            evaluated = stats["success"] + stats["parse_fail"] + stats["failed"]
            success_rate_str = f"{stats['success']}/{evaluated} ({stats['success']/evaluated*100:.1f}%)" if evaluated > 0 else "N/A"
            
            # 状态颜色
            if status == "success":
                status_color = "\033[1;32m"  # 绿色
            elif status == "skipped":
                status_color = "\033[1;33m"  # 黄色
            elif status == "parse_fail":
                status_color = "\033[1;35m"  # 紫色
            else:
                status_color = "\033[1;31m"  # 红色
            
            print(f"\n{status_color}[Progress] |{bar}| {completed}/{total_tasks} ({pct:.1f}%) "
                  f"| Elapsed: {elapsed_str} | ETA: {eta_str}\033[0m")
            print(f"{status_color}[Stats]   ✓ Success: {stats['success']} | ⚠ ParseFail: {stats['parse_fail']} "
                  f"| ✗ Error: {stats['failed']} | ⏭ Skipped: {stats['skipped']} "
                  f"| Success Rate: {success_rate_str}\033[0m")
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        # 提交所有任务
        future_to_traj = {}
        for idx, traj_item in enumerate(trajectory_items, 1):
            future = executor.submit(
                process_single_trajectory_wrapper,
                traj_item, total_tasks, idx
            )
            future_to_traj[future] = (traj_item, idx)
        
        # 收集结果
        for future in as_completed(future_to_traj):
            traj_item, idx = future_to_traj[future]
            task_id = traj_item.get("task_id", "unknown")
            try:
                result = future.result()
                with progress_lock:
                    progress_stats["completed"] += 1
                    if result is None:
                        progress_stats["skipped"] += 1
                        status = "skipped"
                    elif isinstance(result.get("prediction"), int) and result["prediction"] == -2:
                        progress_stats["parse_fail"] += 1
                        results.append(result)
                        status = "parse_fail"
                    else:
                        progress_stats["success"] += 1
                        results.append(result)
                        status = "success"
                print_progress(task_id, status)
            except Exception as e:
                with progress_lock:
                    progress_stats["completed"] += 1
                    progress_stats["failed"] += 1
                print(f"\033[1;31m{'='*80}\033[0m")
                print(f"\033[1;31m✗ Trajectory {task_id} generated an exception\033[0m")
                print(f"\033[1;31m{'='*80}\033[0m")
                traceback.print_exc()
                print(f"\033[1;31m{'='*80}\033[0m")
                print_progress(task_id, "error")
    
    # 最终汇总
    total_elapsed = time.time() - progress_stats["start_time"]
    elapsed_min, elapsed_s = divmod(int(total_elapsed), 60)
    elapsed_h, elapsed_min = divmod(elapsed_min, 60)
    elapsed_str = f"{elapsed_h}h{elapsed_min:02d}m{elapsed_s:02d}s" if elapsed_h > 0 else f"{elapsed_min}m{elapsed_s:02d}s"
    
    evaluated = progress_stats["success"] + progress_stats["parse_fail"] + progress_stats["failed"]
    success_rate_str = f"{progress_stats['success']}/{evaluated} ({progress_stats['success']/evaluated*100:.1f}%)" if evaluated > 0 else "N/A"
    
    print(f"\n\033[1;32m{'='*60}\033[0m")
    print(f"\033[1;32mAll trajectories completed! Total time: {elapsed_str}\033[0m")
    print(f"\033[1;32m  ✓ Success: {progress_stats['success']}  ⚠ ParseFail: {progress_stats['parse_fail']}  "
          f"✗ Error: {progress_stats['failed']}  ⏭ Skipped: {progress_stats['skipped']}\033[0m")
    print(f"\033[1;32m  Success Rate: {success_rate_str}\033[0m")
    print(f"\033[1;32m{'='*60}\033[0m\n")
    
    return results


def collect_and_save_summary(traj_root_dir, model_name, eval_mode):
    """从各个轨迹目录收集result_{model_name}_{eval_mode}.json并汇总
    
    Args:
        traj_root_dir: 轨迹根目录
        model_name: 模型名称
        eval_mode: 评估模式
    """
    print(f"\n\033[1;32mCollecting results from trajectory directories...\033[0m")
    
    all_results = []
    
    # 找到results目录的父目录作为基准
    # 从traj_root_dir向上查找，直到找到results目录
    current_path = os.path.abspath(traj_root_dir)
    results_parent = None
    
    # 向上遍历目录，找到results目录的父目录
    while current_path != os.path.dirname(current_path):  # 未到达根目录
        if os.path.basename(current_path) == "results":
            results_parent = os.path.dirname(current_path)
            break
        current_path = os.path.dirname(current_path)
    
    # 如果没找到results目录，使用项目根目录作为fallback
    if results_parent is None:
        results_parent = REPO_ROOT
        print(f"\033[1;33mWarning: Could not find 'results' directory in path, using project root as base\033[0m")
    
    # 遍历所有task_type目录
    for task_type in os.listdir(traj_root_dir):
        task_type_dir = os.path.join(traj_root_dir, task_type)
        
        if not os.path.isdir(task_type_dir):
            continue
        
        # 遍历所有轨迹目录
        for task_id in os.listdir(task_type_dir):
            traj_dir = os.path.join(task_type_dir, task_id)
            
            if not os.path.isdir(traj_dir):
                continue
            
            # 读取result文件
            result_file = os.path.join(traj_dir, f"result_{model_name}_{eval_mode}.json")
            if os.path.exists(result_file):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                        
                        # 添加path字段：存储result文件相对于results父目录的相对路径
                        # 这样路径会从results/开始
                        relative_path = os.path.relpath(result_file, results_parent)
                        result["path"] = relative_path
                        
                        all_results.append(result)
                except Exception as e:
                    print(f"Warning: Failed to read {result_file}: {str(e)}")
    
    # 保存汇总结果
    summary_file = os.path.join(traj_root_dir, f"predictions_summary_{model_name}_{eval_mode}.json")
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"\033[1;32m✓ Saved summary to {summary_file}\033[0m")
        print(f"\033[1;32mTotal results collected: {len(all_results)}\033[0m")
    except Exception as e:
        print(f"\033[1;31mError saving summary: {str(e)}\033[0m")


def main():
    """主函数"""
    # 参数验证
    if not args.traj_dir and not args.traj_dirs:
        print("\033[1;31mError: Must specify either --traj_dir or --traj_dirs\033[0m")
        sys.exit(1)
    
    # 确定要处理的目录列表
    if args.traj_dirs:
        # 多 trial 合并模式
        traj_dir_list = [d.strip() for d in args.traj_dirs.split(",") if d.strip()]
        print(f"\n{'='*60}")
        print(f"Trajectory Evaluation Script (Multi-Trial Merged Mode)")
        print(f"{'='*60}")
        print(f"Trajectory directories ({len(traj_dir_list)} trials):")
        for i, d in enumerate(traj_dir_list, 1):
            print(f"  {i}. {d}")
    else:
        # 单 trial 模式
        traj_dir_list = [args.traj_dir]
        print(f"\n{'='*60}")
        print(f"Trajectory Evaluation Script")
        print(f"{'='*60}")
        print(f"Trajectory directory: {args.traj_dir}")
    
    print(f"Model config: {args.model_config_name}")
    print(f"Model name: {args.model_name}")
    print(f"Eval mode: {args.eval_mode}")
    print(f"Skip existing: {args.skip_existing}")
    print(f"Num items: {args.num_items if args.num_items > 0 else 'all'}")
    print(f"{'='*60}\n")
    
    # 1. 扫描所有轨迹目录并合并
    all_trajectory_items = []
    for traj_dir in traj_dir_list:
        if not os.path.exists(traj_dir):
            print(f"\033[1;33mWarning: Directory does not exist: {traj_dir}, skipping...\033[0m")
            continue
        items = scan_trajectory_dirs(traj_dir)
        all_trajectory_items.extend(items)
        print(f"Found {len(items)} trajectories in {traj_dir}")
    
    print(f"\n\033[1;32mTotal trajectories from all trials: {len(all_trajectory_items)}\033[0m\n")
    
    # 打乱顺序，使不同 trial 的任务交错执行
    if len(traj_dir_list) > 1:
        import random
        random.shuffle(all_trajectory_items)
        print(f"\033[1;36mTasks shuffled for better distribution across trials\033[0m\n")
    
    # 2. 限制评估数量（如果指定了num_items）
    if args.num_items > 0:
        original_count = len(all_trajectory_items)
        all_trajectory_items = all_trajectory_items[:args.num_items]
        print(f"\033[1;33m⚠ Limiting evaluation to {args.num_items} trajectories (out of {original_count} total)\033[0m\n")
    
    # 3. 并行评估所有轨迹
    results = process_all_trajectories(all_trajectory_items)
    
    # 4. 收集并保存汇总结果（为每个 trial 目录单独保存）
    for traj_dir in traj_dir_list:
        if os.path.exists(traj_dir):
            collect_and_save_summary(traj_dir, args.model_name, args.eval_mode)
    
    print(f"\n\033[1;32m{'='*60}\033[0m")
    print(f"\033[1;32mEvaluation completed successfully!\033[0m")
    print(f"\033[1;32m{'='*60}\033[0m\n")


if __name__ == "__main__":
    main()
