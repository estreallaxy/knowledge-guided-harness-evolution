from __future__ import annotations

import json
import os
from pathlib import Path


def _find_osworld_examples_root() -> Optional[Path]:
    env_root = os.environ.get("OSWORLD_EXAMPLES_ROOT")
    if env_root:
        path = Path(env_root).expanduser().resolve()
        if path.exists():
            return path

    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "evaluation_examples" / "examples"
        if candidate.exists():
            return candidate
    return None


# ==================== 数据加载相关 ====================

def get_instruction(task_type, task_id, examples_root=None):
    """根据任务类型和ID获取 OSWorld instruction。"""
    base_path = Path(examples_root).expanduser().resolve() if examples_root else _find_osworld_examples_root()
    if base_path is None:
        raise FileNotFoundError(
            "未找到 OSWorld evaluation_examples/examples；可设置 OSWORLD_EXAMPLES_ROOT 或直接使用标注文件中的 instruction。"
        )

    json_path = base_path / task_type / f"{task_id}.json"
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            instruction = data.get("instruction", "")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"未找到JSON文件: {json_path}") from e
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON文件解析失败: {json_path}", e.doc, e.pos) from e

    return instruction


def load_data_items(json_path, args):
    """加载数据项。"""
    data_items = []
    json_path = str(json_path)
    if json_path.endswith('.jsonl'):
        with open(json_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data_items.append(json.loads(line))
    elif json_path.endswith('.json'):
        with open(json_path, 'r', encoding='utf-8') as f:
            data_items = json.load(f)
            if not isinstance(data_items, list):
                raise ValueError(f"JSON file should contain a list, got {type(data_items)}")
    else:
        raise ValueError(f"Unsupported file format: {json_path}")

    return data_items if args.num_items <= 0 else data_items[:args.num_items]


# ==================== 文件操作相关 ====================

def prepare_result_filenames(json_path, args):
    """准备结果文件路径。"""
    jsonl_basename = os.path.splitext(os.path.basename(str(json_path)))[0]
    model_name = args.model_config["model"].replace('/', '_')

    exp_name = f"evalmode_{args.eval_mode}_{jsonl_basename}_{model_name}"
    if args.max_screenshots != 20:
        exp_name = f"{exp_name}_maxS{args.max_screenshots}"
    if args.exp_suffix:
        exp_name = f"{exp_name}_{args.exp_suffix}"
    detailed_filename = f"detailed_results_{exp_name}.json"

    results_dir = getattr(args, 'output_dir', None) or "outputs"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    detailed_filepath = os.path.join(results_dir, detailed_filename)
    metrics_filename = f"metrics_{exp_name}.json"

    return detailed_filepath, metrics_filename


def load_existing_results(detailed_filepath):
    """加载已有的详细结果。"""
    existing_results = []
    evaluated_tasks = set()

    if os.path.exists(detailed_filepath):
        with open(detailed_filepath, 'r', encoding='utf-8') as f:
            all_loaded = json.load(f)
        print(f"Loaded existing results from {os.path.basename(detailed_filepath)}")

        failed_count = 0
        for res in all_loaded:
            if isinstance(res, dict) and 'model_setting' in res and 'task_id' in res:
                llm_output = res.get('llm_output', '')
                is_failed = (
                    llm_output == "failed in response"
                    or (isinstance(llm_output, str) and llm_output.strip() == "")
                )
                if is_failed:
                    failed_count += 1
                    continue

                existing_results.append(res)
                key = (res['model_setting'], res['task_id'])
                evaluated_tasks.add(key)
            else:
                existing_results.append(res)

        if failed_count > 0:
            print(f"Found {failed_count} failed tasks that will be re-evaluated")
            try:
                with open(detailed_filepath, 'w', encoding='utf-8') as f:
                    json.dump(existing_results, f, indent=2, ensure_ascii=False)
                print(f"Cleaned results saved (removed {failed_count} failed entries)")
            except Exception as e:
                print(f"Warning: failed to save cleaned results: {e}")

    return existing_results, evaluated_tasks
