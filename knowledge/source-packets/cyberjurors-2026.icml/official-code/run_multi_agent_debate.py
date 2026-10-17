"""
运行多智能体讨论系统
Run Multi-Agent Debate System

使用示例：
1. 处理所有案件：
   python run_multi_agent_debate.py

2. 处理指定数量案件：
   python run_multi_agent_debate.py --num_cases 10

3. 使用自定义配置：
   python run_multi_agent_debate.py --config custom_config.yaml

4. 从指定案件开始：
   python run_multi_agent_debate.py --start_idx 100 --num_cases 50
"""

import argparse
import json
from re import I
import yaml
import os
import time
from pathlib import Path
from typing import Optional
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from utils_syh import parse_case_to_standard_format
import re

from multi_agent_debate import MultiAgentDebateSystem
from Social_Consensus import preload_consensus_index


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_cases(dataset_path: str, start_idx: int = 0, num_cases: Optional[int] = None):
    """加载案件数据"""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        all_cases = json.load(f)
    
    if num_cases is not None:
        cases = all_cases[start_idx:start_idx + num_cases]
    else:
        cases = all_cases[start_idx:]
    
    return cases, len(all_cases)


def compute_accuracy(results: list, ground_truth_key: str = 'verdict') -> dict:
    """计算准确率"""
    if not results:
        return {'accuracy': 0.0, 'total': 0}
    
    correct = 0
    total = 0
    
    for result in results:
        # 检查是否有ground truth
        case_data = result.get('case_data')
        if case_data and ground_truth_key in case_data:
            gt = case_data[ground_truth_key].lower()
            pred = result['final_verdict']['verdict'].lower()
            
            if gt == pred:
                correct += 1
            total += 1
    
    accuracy = correct / total if total > 0 else 0.0
    
    return {
        'accuracy': accuracy,
        'correct': correct,
        'total': total
    }


def process_single_case(case: dict, config: dict, case_idx: int, total: int) -> tuple:
    """处理单个案件（在独立线程中）
    
    Args:
        case: 案件数据
        config: 配置字典（在线程内创建系统实例）
        case_idx: 案件索引
        total: 总案件数
    
    Returns:
        (success: bool, result: dict or None, error: str or None)
    """
    case_id = case.get('id', f'case_{case_idx}')
    
    try:
        print(f"\n[线程-{threading.current_thread().name}] 处理案件 {case_idx}/{total}: {case_id}")
        
        # 在执行时才创建系统实例，避免内存爆炸
        system = MultiAgentDebateSystem(config)
        result = system.deliberate(case)
        
        # 显式清理（帮助垃圾回收）
        del system
        
        return (True, result, None)
    except Exception as e:
        print(f"\n[线程-{threading.current_thread().name}] ❌ 案件 {case_id} 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return (False, None, str(e))


def main():
    parser = argparse.ArgumentParser(description='运行多智能体讨论系统')
    parser.add_argument('--config', type=str, default='multi_agent_config.yaml',
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    print(f"✅ 加载配置: {args.config}")
    
    # 加载案件
    dataset_path = config.get('dataset_path', './dataset/val_new_new.json')
    cases, total_cases = load_cases(dataset_path, start_idx=0, num_cases=3000)
    
    print(f"📁 数据集: {dataset_path}")
    print(f"📊 总案件数: {total_cases}")
    print(f"🎯 处理案件: {len(cases)}")
    print(f"🔀 案例级并行数: {config.get('parallel_cases', 1)}")
    
    # ==================== 预加载社会共识索引（避免多线程竞争）====================
    if config.get('use_social_consensus', False):
        print("\n" + "="*70)
        preload_consensus_index()
        print("="*70 + "\n")
    
    # 处理案件
    results = []
    base_output_dir = Path(config.get('output_dir', './results/multi_agent_debate'))
    experiment_name = config.get('experiment_name', 'default')
    output_dir = base_output_dir / experiment_name
    
    # 如果启用resume，检查已处理的案件
    processed_ids = set()
    if config.get('resume', False):
        # 匹配新格式：*_debate_correct.json 或 *_debate_wrong.json
        for file in output_dir.glob('*_debate_*.json'):
            # 从文件名中提取 case_id（移除 _debate_correct 或 _debate_wrong）
            case_id = file.stem.replace('_debate_True', '').replace('_debate_False', '')
            case_id = int(case_id.split('_')[-1])
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'final_verdict' in data.keys() and 'verdict' in data['final_verdict'].keys():
                        processed_ids.add(case_id)
                        print(f"已处理案件: {case_id}")
            except Exception as e:
                continue
            
        print(f"🔄 续传模式：已处理 {len(processed_ids)} 个案件")
    
    # 过滤掉已处理的案件
    cases_to_process = []
    for i, case in enumerate(cases, 1):
        case_id = case.get('id', f'case_{i}')
        if config.get('resume', False) and case_id in processed_ids:
            print(f"⏭️  跳过已处理案件: {case_id}")
        else:
            case = parse_case_to_standard_format(case)
            cases_to_process.append((i, case))
    
    print(f"\n待处理案件: {len(cases_to_process)} 个")
    
    # 开始处理
    start_time = time.time()
    failed_cases = []
    results_lock = threading.Lock()
    
    if config.get('parallel_cases') == 1:
        # 串行处理
        print("📝 使用串行模式处理案件\n")
        for case_idx, case in tqdm(cases_to_process, desc="处理案件"):
            case_id = case.get('case_id', f'case_{case_idx}')
            success, result, error = process_single_case(case, config, case_idx, len(cases))
            
            if success:
                results.append(result)
                # 每个案例已自动保存为 {case_id}_debate.json
                print(f"  ✅ 案例已保存: {case_id}_debate.json")
            else:
                failed_cases.append({'id': case_id, 'error': error})
    
    else:
        # 并行处理
        print(f"🚀 使用并行模式处理案件 (并行数: {config.get('parallel_cases', 1)})\n")
        print("⚠️  注意: 每个案件内部的17个智能体也会并行运行")
        print(f"   总线程数 ≈ {config.get('parallel_cases', 1)} (案件) × 17 (智能体) = {config.get('parallel_cases', 1) * 17}\n")
        print("💡 优化: 系统实例将在线程执行时才创建，避免内存占用过大\n")
        
        with ThreadPoolExecutor(max_workers=config.get('parallel_cases', 1)) as executor:
            # 提交任务，传递config而不是system实例
            futures = {}
            
            for case_idx, case in cases_to_process:
                # 传递config，让线程在执行时才创建系统实例
                future = executor.submit(
                    process_single_case,
                    case,
                    config,  # 传递config而非预先创建的system
                    case_idx,
                    len(cases)
                )
                futures[future] = (case_idx, case)
            
            # 收集结果
            completed_count = 0
            for future in as_completed(futures):
                case_idx, case = futures[future]
                case_id = case.get('case_id', f'case_{case_idx}')
                
                success, result, error = future.result()
                
                with results_lock:
                    if success:
                        results.append(result)
                        completed_count += 1
                        # 每个案例已自动保存为 {case_id}_debate.json
                        print(f"\n✅ 完成 {completed_count}/{len(cases_to_process)}: {case_id} (已保存)")
                    else:
                        failed_cases.append({'case_id': case_id, 'error': error})
                        print(f"\n❌ 失败: {case_id}")
    
    # 计算统计信息
    elapsed_time = time.time() - start_time
    avg_time = elapsed_time / len(results) if results else 0
    
    print(f"\n{'='*70}")
    print(f"✅ 处理完成！")
    print(f"{'='*70}")
    print(f"📊 统计信息:")
    print(f"  - 成功处理: {len(results)} 个案件")
    print(f"  - 失败案件: {len(failed_cases)} 个")
    print(f"  - 总耗时: {elapsed_time/60:.1f} 分钟")
    print(f"  - 平均耗时: {avg_time:.1f} 秒/案件")
    
    print(f"\n📁 案件保存位置:")
    print(f"  - 实验名称: {experiment_name}")
    print(f"  - 保存目录: {output_dir}/")
    print(f"  - 文件格式: {{case_id}}_debate_{{True/False}}.json")
    if len(results) > 0:
        # 统计正确和错误的数量
        correct_count = sum(1 for r in results if r.get('True', False))
        wrong_count = len(results) - correct_count
        accuracy = correct_count / len(results) * 100 if results else 0
        
        print(f"\n📊 准确率统计:")
        print(f"  - 正确: {correct_count}/{len(results)} (✅ {correct_count} 个)")
        print(f"  - 错误: {wrong_count}/{len(results)} (❌ {wrong_count} 个)")
        print(f"  - 准确率: {accuracy:.2f}%")
        
        # 显示前3个案件的文件名示例
        sample_count = min(3, len(results))
        print(f"\n  示例文件:")
        for i in range(sample_count):
            case_id = results[i]['case_id']
            result_label = "True" if results[i].get('True', False) else "False"
            icon = "✅" if results[i].get('True', False) else "❌"
            print(f"    {icon} {case_id}_debate_{result_label}.json")
    
    # 保存最终汇总结果
    # summary_file = output_dir / 'summary.json'
    # with open(summary_file, 'w', encoding='utf-8') as f:
    #     json.dump({
    #         'total_cases': len(results),
    #         'failed_cases': len(failed_cases),
    #         'elapsed_time': elapsed_time,
    #         'average_time_per_case': avg_time,
    #         'results': results,
    #         'failed': failed_cases,
    #         'config': config
    #     }, f, ensure_ascii=False, indent=2)
    
    # print(f"\n💾 汇总结果已保存: {summary_file}")
    # print(f"   (包含所有案件的统计信息和元数据)")
    
    # 计算准确率（如果有ground truth）
    # accuracy_stats = compute_accuracy(results)
    # if accuracy_stats['total'] > 0:
    #     print(f"\n📈 准确率: {accuracy_stats['accuracy']:.2%} ({accuracy_stats['correct']}/{accuracy_stats['total']})")


if __name__ == '__main__':
    main()

