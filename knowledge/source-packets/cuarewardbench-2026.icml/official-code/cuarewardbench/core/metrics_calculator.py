import json
import os
from collections import defaultdict
from .result_parser import parse_action_reward_by_task_type
# 添加Excel导出相关的导入
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:  # optional unless Excel export is required
    Workbook = Font = Alignment = Border = Side = get_column_letter = None


def compute_binary_classification_metrics(true_labels, pred_labels):
    """计算二分类指标：精确率、召回率、F1、总体准确率、NPV、特异性等"""
    tp = fp = fn = tn = 0
    for true, pred in zip(true_labels, pred_labels):
        if true == 1 and pred == 1:
            tp += 1
        elif true == 0 and pred == 1:
            fp += 1
        elif true == 1 and pred == 0:
            fn += 1
        else:
            tn += 1
    
    total_samples = len(true_labels)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    oa = (tp + tn) / total_samples
    
    # 添加NPV和specificity计算
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0  # Negative Predictive Value
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # True Negative Rate
    
    # 调整返回字典的顺序为 P、NPV、R、OA
    return {
        'precision': precision,
        'npv': npv,
        'recall': recall,
        'oa': oa,
        'f1': f1,
        'specificity': specificity,
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': tn,
        'total_samples': total_samples
    }


def analyze_group_performance(all_results):
    """分析每个子类别的性能（准确率、错误率、比例）"""
    # 初始化子类别统计
    group_stats = {
        'key_good_before_bad_in_fail': {'correct': 0, 'total': 0},
        'key_good_in_success': {'correct': 0, 'total': 0},
        'key_good_after_bad_in_success': {'correct': 0, 'total': 0},
        'key_bad_in_fail': {'correct': 0, 'total': 0},
        'key_bad_in_success': {'correct': 0, 'total': 0}
    }
    
    for task in all_results:
        action_annos = task.get('action_annos', {})
        action_reward_list = task.get('action_reward_list', [])
        step_num = task.get('step_num', 0)
        
        # 处理每个子类别
        for group in group_stats.keys():
            steps = action_annos.get(group, [])
            for step in steps:
                if 1 <= step <= step_num:
                    group_stats[group]['total'] += 1
                    # 确定预期标签（good子类别为1，bad子类别为0）
                    expected = 1 if 'key_good' in group else 0
                    predicted = action_reward_list[step - 1]
                    if predicted == expected:
                        group_stats[group]['correct'] += 1
    
    # 计算每个子类别的准确率和错误率
    for group, stats in group_stats.items():
        if stats['total'] > 0:
            stats['accuracy'] = stats['correct'] / stats['total']
            stats['error_rate'] = 1 - stats['accuracy']
        else:
            stats['accuracy'] = 0
            stats['error_rate'] = 0
    
    # 计算总步数（用于计算比例）
    total_steps = sum(stats['total'] for stats in group_stats.values())
    for stats in group_stats.values():
        if total_steps > 0:
            stats['proportion'] = stats['total'] / total_steps
        else:
            stats['proportion'] = 0
    
    return group_stats


def update_group_stats(group, task):
    """更新分组统计"""
    pred = task.get('pred', -1)
    gt = task.get('gt', -1)
    
    if pred == -1:
        group['fail'] += 1
    elif gt == 1 and pred == 1:
        group['tp'] += 1
    elif gt == 0 and pred == 1:
        group['fp'] += 1
    elif gt == 1 and pred == 0:
        group['fn'] += 1


def compute_metrics(stats_dict):
    """计算评估指标（准确率、精确率、召回率、F1、NPV、特异性）"""
    tp = stats_dict.get('tp', 0)
    fp = stats_dict.get('fp', 0)
    fn = stats_dict.get('fn', 0)
    total = stats_dict.get('total', 0)
    
    # 正确预测的负样本数 = 总样本数 - (TP + FP + FN) - 失败数
    tn = total - (tp + fp + fn + stats_dict.get('fail', 0))
    
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # 添加NPV和specificity计算
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0  # Negative Predictive Value
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # True Negative Rate
    
    # 调整返回字典的顺序为 P、NPV、R、Accuracy（对于trajectory metrics）
    return {
        'precision': precision,
        'npv': npv,
        'recall': recall,
        'accuracy': accuracy,
        'f1': f1,
        'specificity': specificity,
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': tn,
        'fail': stats_dict.get('fail', 0),
        'total': total
    }


def compute_step_num_metrics(all_results):
    """计算按步数分组的指标"""
    sorted_tasks = sorted(all_results, key=lambda x: x['step_num'])
    total_tasks = len(sorted_tasks)
    split_index = total_tasks // 2
    
    # 初始化分组统计
    groups = {
        'less_half': {'tp': 0, 'fp': 0, 'fn': 0, 'fail': 0, 'total': split_index},
        'more_half': {'tp': 0, 'fp': 0, 'fn': 0, 'fail': 0, 'total': total_tasks - split_index}
    }
    
    # 统计前50%的任务
    for task in sorted_tasks[:split_index]:
        update_group_stats(groups['less_half'], task)
    
    # 统计后50%的任务
    for task in sorted_tasks[split_index:]:
        update_group_stats(groups['more_half'], task)
    
    # 计算每组指标（现在包含NPV和specificity）
    for group in groups.values():
        metrics = compute_metrics(group)
        group.update(metrics)
    
    return groups


def collect_statistics(all_results, stats, task_type_stats):
    """从所有结果中收集统计信息
    
    Args:
        all_results: 包含所有评估结果的列表
        stats: 统计信息字典
        task_type_stats: 任务类型统计信息字典
    """
    for res in all_results:
        model_setting = res['model_setting']
        task_type = res['task_type']
        pred_result = res['pred']
        gt_result = res['gt']
        
        if pred_result is None or pred_result == -2:  # 评估失败
            stats[model_setting]['fail'] += 1
            stats['overall']['fail'] += 1
            task_type_stats[task_type]['fail'] += 1
        else:
            if gt_result == 1 and pred_result == 1:
                stats[model_setting]['tp'] += 1
                stats['overall']['tp'] += 1
                task_type_stats[task_type]['tp'] += 1
            elif gt_result == 0 and pred_result == 1:
                stats[model_setting]['fp'] += 1
                stats['overall']['fp'] += 1
                task_type_stats[task_type]['fp'] += 1
            elif gt_result == 1 and pred_result == 0:
                stats[model_setting]['fn'] += 1
                stats['overall']['fn'] += 1
                task_type_stats[task_type]['fn'] += 1
        
        stats[model_setting]['total'] += 1
        stats['overall']['total'] += 1
        task_type_stats[task_type]['total'] += 1


def extract_metrics_for_excel(metrics_data):
    """从指标数据中提取Excel所需的格式化数据"""
    # 定义任务类型映射（JSON中的键名到表格列名的映射）
    task_mapping = {
        'vs_code': 'vscode',
        'gimp': 'gimp', 
        'libreoffice_writer': 'writer',
        'chrome': 'chrome',
        'multi_apps': 'multi_apps',
        'vlc': 'vlc',
        'os': 'os',
        'thunderbird': 'thunderbird',
        'libreoffice_impress': 'impress',
        'libreoffice_calc': 'calc'
    }
    
    result = {}
    
    # 处理 trajectory_reward_metrics
    if 'trajectory_reward_metrics' in metrics_data:
        traj_metrics = metrics_data['trajectory_reward_metrics']
        overall_metrics = traj_metrics.get('overall', {})
        by_task_type = traj_metrics.get('by_task_type', {})
        
        traj_result = {}
        
        # Overall数据 - 添加S列
        traj_result['overall'] = {
            'P': round(overall_metrics.get('precision', 0) * 100, 1),
            'NPV': round(overall_metrics.get('npv', 0) * 100, 1),
            'R': round(overall_metrics.get('recall', 0) * 100, 1),
            'S': round(overall_metrics.get('specificity', 0) * 100, 1),  # 新增S列
            'OA': round(overall_metrics.get('accuracy', 0) * 100, 1)  # trajectory用accuracy
        }
        
        # 各任务类型数据 - 保持原有的P、NPV、R、OA
        for json_key, table_key in task_mapping.items():
            if json_key in by_task_type:
                metrics = by_task_type[json_key]
                traj_result[table_key] = {
                    'P': round(metrics.get('precision', 0) * 100, 1),
                    'NPV': round(metrics.get('npv', 0) * 100, 1),
                    'R': round(metrics.get('recall', 0) * 100, 1),
                    'OA': round(metrics.get('accuracy', 0) * 100, 1)  # trajectory用accuracy
                }
            else:
                # 如果没有数据，填充空值
                traj_result[table_key] = {'P': '', 'NPV': '', 'R': '', 'OA': ''}
        
        result['trajectory'] = traj_result
    
    # 处理 action_reward_metrics
    if 'action_reward_metrics' in metrics_data:
        action_metrics = metrics_data['action_reward_metrics']
        overall_metrics = action_metrics.get('overall', {})
        by_task_type = action_metrics.get('by_task_type', {})
        
        action_result = {}
        
        # Overall数据 - 添加S列
        action_result['overall'] = {
            'P': round(overall_metrics.get('precision', 0) * 100, 1),
            'NPV': round(overall_metrics.get('npv', 0) * 100, 1),
            'R': round(overall_metrics.get('recall', 0) * 100, 1),
            'S': round(overall_metrics.get('specificity', 0) * 100, 1),  # 新增S列
            'OA': round(overall_metrics.get('oa', 0) * 100, 1)  # action用oa
        }
        
        # 各任务类型数据 - 保持原有的P、NPV、R、OA
        for json_key, table_key in task_mapping.items():
            if json_key in by_task_type:
                metrics = by_task_type[json_key].get('metrics', {})
                action_result[table_key] = {
                    'P': round(metrics.get('precision', 0) * 100, 1),
                    'NPV': round(metrics.get('npv', 0) * 100, 1),
                    'R': round(metrics.get('recall', 0) * 100, 1),
                    'OA': round(metrics.get('oa', 0) * 100, 1)  # action用oa
                }
            else:
                # 如果没有数据，填充空值
                action_result[table_key] = {'P': '', 'NPV': '', 'R': '', 'OA': ''}
        
        result['action'] = action_result
    
    return result


def create_excel_from_metrics(metrics_data, model_name, output_file):
    """根据指标数据创建Excel文件"""
    if Workbook is None:
        print("openpyxl is not installed; skip Excel export.")
        return
    
    # 提取Excel格式的数据
    excel_data = extract_metrics_for_excel(metrics_data)
    
    # 创建工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "Reward Model Metrics"
    
    # 定义列标题
    columns = ['overall', 'vscode', 'gimp', 'writer', 'chrome', 'multi_apps', 
               'vlc', 'os', 'thunderbird', 'impress', 'calc']
    
    # 设置表头
    # 第一行：主标题
    ws.merge_cells('A1:A2')
    ws['A1'] = 'Reward Model'
    ws['A1'].font = Font(bold=True)
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    
    # 第二行：各任务类型标题
    col_start = 2
    for i, col_name in enumerate(columns):
        if i == 0:  # overall列有5列（P, NPV, R, S, OA）
            col_count = 5
            metrics = ['P', 'NPV', 'R', 'S', 'OA']
        else:  # 其他列有4列（P, NPV, R, OA）
            col_count = 4
            metrics = ['P', 'NPV', 'R', 'OA']
        
        # 合并列作为一个任务类型的标题
        start_col = col_start
        end_col = col_start + col_count - 1
        ws.merge_cells(start_row=1, start_column=start_col, end_row=1, end_column=end_col)
        cell = ws.cell(row=1, column=start_col)
        cell.value = col_name.replace('_', ' ').title()
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 第二行：指标名称
        for j, metric in enumerate(metrics):
            cell = ws.cell(row=2, column=start_col + j)
            cell.value = metric
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        col_start += col_count
    
    # 添加数据行
    current_row = 3
    
    # 添加trajectory数据行（如果存在）
    if 'trajectory' in excel_data:
        ws.cell(row=current_row, column=1).value = f"{model_name}_trajectory"
        ws.cell(row=current_row, column=1).font = Font(bold=True)
        
        col = 2
        traj_metrics = excel_data['trajectory']
        for i, col_name in enumerate(columns):
            if col_name in traj_metrics:
                data = traj_metrics[col_name]
                if i == 0:  # overall列
                    ws.cell(row=current_row, column=col).value = data['P']
                    ws.cell(row=current_row, column=col+1).value = data['NPV']
                    ws.cell(row=current_row, column=col+2).value = data['R']
                    ws.cell(row=current_row, column=col+3).value = data['S']
                    ws.cell(row=current_row, column=col+4).value = data['OA']
                    col += 5
                else:  # 其他列
                    ws.cell(row=current_row, column=col).value = data['P']
                    ws.cell(row=current_row, column=col+1).value = data['NPV']
                    ws.cell(row=current_row, column=col+2).value = data['R']
                    ws.cell(row=current_row, column=col+3).value = data['OA']
                    col += 4
            else:
                # 根据列类型跳过相应的列数
                col += 5 if i == 0 else 4
        current_row += 1
    
    # 添加action数据行（如果存在）
    if 'action' in excel_data:
        ws.cell(row=current_row, column=1).value = f"{model_name}_action"
        ws.cell(row=current_row, column=1).font = Font(bold=True)
        
        col = 2
        action_metrics = excel_data['action']
        for i, col_name in enumerate(columns):
            if col_name in action_metrics:
                data = action_metrics[col_name]
                if i == 0:  # overall列
                    ws.cell(row=current_row, column=col).value = data['P']
                    ws.cell(row=current_row, column=col+1).value = data['NPV']
                    ws.cell(row=current_row, column=col+2).value = data['R']
                    ws.cell(row=current_row, column=col+3).value = data['S']
                    ws.cell(row=current_row, column=col+4).value = data['OA']
                    col += 5
                else:  # 其他列
                    ws.cell(row=current_row, column=col).value = data['P']
                    ws.cell(row=current_row, column=col+1).value = data['NPV']
                    ws.cell(row=current_row, column=col+2).value = data['R']
                    ws.cell(row=current_row, column=col+3).value = data['OA']
                    col += 4
            else:
                # 根据列类型跳过相应的列数
                col += 5 if i == 0 else 4
        current_row += 1
    
    # 设置边框
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # 计算最大列数：overall(5列) + 其他10个任务类型(4列*10) = 45列
    max_row = current_row - 1
    max_col = 2 + 5 + 10 * 4 - 1  # A列(1) + overall(5) + 其他10个任务类型(40) = 46列
    
    # 应用边框到所有使用的单元格
    for row in range(1, max_row + 1):
        for col in range(1, max_col + 1):
            ws.cell(row=row, column=col).border = thin_border
    
    # 调整列宽
    ws.column_dimensions['A'].width = 25  # 增加第一列宽度以容纳更长的名称
    for col in range(2, max_col + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = 8
    
    # 保存文件
    wb.save(output_file)
    print(f"Excel文件已保存到: {output_file}")


def compute_and_save_metrics(all_results, detailed_filepath, metrics_filename, args):
    """计算并保存所有评估指标"""
    # 收集统计信息
    stats = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0, 'fail': 0, 'total': 0})
    task_type_stats = defaultdict(lambda: {'tp': 0, 'fp': 0, 'fn': 0, 'fail': 0, 'total': 0})

    if "or" in args.reward_type:
        collect_statistics(all_results, stats, task_type_stats)
    # 1. 计算traj-level指标
    for key in list(stats.keys()):
        if stats[key]['total'] > 0:
            stats[key] = compute_metrics(stats[key])
    
    # 2. 计算task_type-wise traj-level指标
    for task_type in list(task_type_stats.keys()):
        task_type_stats[task_type] = compute_metrics(task_type_stats[task_type])
    
    # 3. 解析action reward并收集标签数据（包括按task_type分组）
    if 'ar' in args.reward_type:
        all_results, all_true_labels, all_pred_labels, task_type_labels = parse_action_reward_by_task_type(all_results)
    
    # 4. 保存详细结果（最终完整保存）
    try:
        with open(detailed_filepath, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving final detailed results: {str(e)}")
    
    # 5. 重构统计结构
    new_stats = {}
    
    # 构建trajectory_reward_metrics
    if "or" in args.reward_type:
        new_stats['trajectory_reward_metrics'] = {
            'overall': stats.get('overall', {}),
            'by_task_type': task_type_stats,
            'by_model_setting': {
                k: v for k, v in stats.items() if k != 'overall'
            },
            'by_step_num': compute_step_num_metrics(all_results)
        }
    
    # 构建action_reward_metrics
    if 'ar' in args.reward_type:
        # 计算按task_type的action reward指标
        task_type_action_metrics = {}
        for task_type, labels in task_type_labels.items():
            if labels['true_labels']:  # 确保有数据
                # 为每个task_type单独筛选结果数据
                task_type_results = [task for task in all_results if task['task_type'] == task_type]
                
                task_type_action_metrics[task_type] = {
                    'metrics': compute_binary_classification_metrics(
                        labels['true_labels'], 
                        labels['pred_labels']
                    ),
                    # 为每个task_type单独计算group metrics
                    'group_metrics': analyze_group_performance(task_type_results)
                }
        
        new_stats['action_reward_metrics'] = {
            'overall': compute_binary_classification_metrics(all_true_labels, all_pred_labels),
            'by_task_type': task_type_action_metrics,
            'by_reward_type': analyze_group_performance(all_results)
        }
    
    # 6. 保存指标结果
    # 使用与 detailed_filepath 相同的目录
    results_dir = os.path.dirname(detailed_filepath)
    if results_dir and not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # 将metrics文件保存到同一目录下
    metrics_filepath = os.path.join(results_dir, metrics_filename) if results_dir else metrics_filename
    try:
        with open(metrics_filepath, 'w') as f:
            json.dump(new_stats, f, indent=2,ensure_ascii=False)
    except Exception as e:
        print(f"Error saving metrics: {str(e)}")
    
    # 7. 生成Excel文件
    try:
        # 从metrics文件名生成Excel文件名
        excel_filename = metrics_filename.replace('.json', '.xlsx')
        excel_filepath = os.path.join(results_dir, excel_filename)
        
        # 从模型配置中提取模型名称
        model_name = args.model_config["model"].replace('/', '_')
        
        # 创建Excel文件
        create_excel_from_metrics(new_stats, model_name, excel_filepath)
        
    except Exception as e:
        print(f"Error creating Excel file: {str(e)}")
    
    # 8. 打印总体结果 - 调整顺序为 P、NPV、R、OA
    if 'trajectory_reward_metrics' in new_stats:
        overall = new_stats['trajectory_reward_metrics']['overall']
        print("\nTrajectory Reward Prediction Metrics:")
        print(f"Precision: {overall['precision']:.4f}")
        print(f"NPV (Negative Predictive Value): {overall['npv']:.4f}")
        print(f"Recall: {overall['recall']:.4f}")
        print(f"Accuracy: {overall['accuracy']:.4f}")
        print(f"F1-score: {overall['f1']:.4f}")
        print(f"Specificity: {overall['specificity']:.4f}")
        print(f"TP: {overall['tp']}, FP: {overall['fp']}, FN: {overall['fn']}, TN: {overall['tn']}")
        print(f"Fail: {overall['fail']}, Total: {overall['total']}")
        
    # 打印action reward指标 - 调整顺序为 P、NPV、R、OA
    if 'action_reward_metrics' in new_stats:
        ar_metrics = new_stats['action_reward_metrics']['overall']
        print("\nAction Reward Prediction Metrics:")
        print(f"Precision: {ar_metrics['precision']:.4f}")
        print(f"NPV (Negative Predictive Value): {ar_metrics['npv']:.4f}")
        print(f"Recall: {ar_metrics['recall']:.4f}")
        print(f"Overall Accuracy: {ar_metrics['oa']:.4f}")
        print(f"F1-score: {ar_metrics['f1']:.4f}")
        print(f"Specificity: {ar_metrics['specificity']:.4f}")
        print(f"TP: {ar_metrics['tp']}, FP: {ar_metrics['fp']}, FN: {ar_metrics['fn']}, TN: {ar_metrics['tn']}")
        print(f"Total Samples: {ar_metrics['total_samples']}")
    
    # 打印子类别指标
    if 'action_reward_metrics' in new_stats and 'by_reward_type' in new_stats['action_reward_metrics']:
        group_metrics = new_stats['action_reward_metrics']['by_reward_type']
        print("\nAction Reward Prediction Group Metrics:")
        for group, metrics in group_metrics.items():
            print(f"\n{group.replace('_', ' ').title()}:")
            print(f"  Accuracy: {metrics['accuracy']:.4f}")
            print(f"  Proportion: {metrics['proportion']:.4f}")
            print(f"  Correct: {metrics['correct']}/{metrics['total']}")
    
    # 打印按task_type的action reward指标 - 调整顺序为 P、NPV、R、OA
    if 'action_reward_metrics' in new_stats and 'by_task_type' in new_stats['action_reward_metrics']:
        task_type_ar_metrics = new_stats['action_reward_metrics']['by_task_type']
        print("\nAction Reward Prediction Metrics by Task Type:")
        for task_type, task_metrics in task_type_ar_metrics.items():
            metrics = task_metrics['metrics']
            print(f"\n{task_type.upper()}:")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  NPV (Negative Predictive Value): {metrics['npv']:.4f}")
            print(f"  Recall: {metrics['recall']:.4f}")
            print(f"  Overall Accuracy: {metrics['oa']:.4f}")
            print(f"  F1-score: {metrics['f1']:.4f}")
            print(f"  Specificity: {metrics['specificity']:.4f}")
            print(f"  Total Samples: {metrics['total_samples']}")
            
            # 打印该task_type的子类别指标
            group_metrics = task_metrics['group_metrics']
            print(f"  Group Metrics:")
            for group, group_stats in group_metrics.items():
                if group_stats['total'] > 0:
                    print(f"    {group.replace('_', ' ').title()}: {group_stats['accuracy']:.4f} ({group_stats['correct']}/{group_stats['total']})")

    print(f"详细结果保存在: {detailed_filepath}")
    print(f"指标结果保存在: {metrics_filepath}")
    print(f"Excel文件保存在: {excel_filepath}")