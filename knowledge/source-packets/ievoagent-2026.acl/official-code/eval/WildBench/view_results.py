#!/usr/bin/env python3
"""
WildBench 评估结果查看工具
"""
import json
import sys
from collections import defaultdict
from datasets import load_dataset

def main():
    if len(sys.argv) < 2:
        print("用法: python view_results.py <模型名称>")
        print("示例: python view_results.py YourModel-7B")
        sys.exit(1)
    
    model_name = sys.argv[1]
    eval_file = f"evaluation/eval_results/v2.0625/score.v2/eval=gpt-4o/{model_name}.json"
    
    try:
        with open(eval_file, 'r') as f:
            eval_data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到评估文件 {eval_file}")
        print(f"请先运行: bash run_evaluation_example.sh {model_name}")
        sys.exit(1)
    
    # 加载benchmark数据获取任务标签
    print("加载WildBench数据集...")
    bench_data = load_dataset('allenai/WildBench', 'v2', split='test')
    
    # 创建session_id到任务标签的映射
    session_to_task = {}
    for item in bench_data:
        session_to_task[item['session_id']] = item['primary_tag']
    
    # 按任务类型统计分数
    task_scores = defaultdict(list)
    for item in eval_data:
        if 'parsed_result' in item and item['parsed_result'] is not None:
            if 'score' in item['parsed_result']:
                score = float(item['parsed_result']['score'])
                session_id = item.get('session_id', '')
                task = session_to_task.get(session_id, 'Unknown')
                task_scores[task].append(score)
    
    all_scores = [s for scores in task_scores.values() for s in scores]
    
    print('=' * 70)
    print(f'{model_name} WildBench 评估结果')
    print('=' * 70)
    
    print(f'\n总样本数: {len(eval_data)}')
    print(f'有效评估: {len(all_scores)}')
    print(f'\n【总体表现】')
    print(f'WB-Score: {sum(all_scores)/len(all_scores):.2f}/10.0')
    print(f'最高分: {max(all_scores):.2f}')
    print(f'最低分: {min(all_scores):.2f}')
    
    # 分数分布
    print(f'\n【分数分布】')
    bins = [0, 3, 5, 7, 9, 10]
    bin_labels = ['0-3分', '3-5分', '5-7分', '7-9分', '9-10分']
    for i in range(len(bins)-1):
        count = sum(1 for s in all_scores if bins[i] < s <= bins[i+1])
        pct = count / len(all_scores) * 100
        bar = '█' * int(pct / 2)
        print(f'{bin_labels[i]:8s}: {count:4d} 样本 ({pct:5.1f}%) {bar}')
    
    # 按任务类型统计
    print(f'\n【各任务类型表现】')
    sorted_tasks = sorted(task_scores.keys(), 
                         key=lambda x: sum(task_scores[x])/len(task_scores[x]), 
                         reverse=True)
    for task in sorted_tasks:
        scores = task_scores[task]
        avg = sum(scores) / len(scores)
        bar = '█' * int(avg)
        print(f'{task:25s}: {avg:.2f}/10.0  (n={len(scores):3d}) {bar}')
    
    print('=' * 70)

if __name__ == '__main__':
    main()
