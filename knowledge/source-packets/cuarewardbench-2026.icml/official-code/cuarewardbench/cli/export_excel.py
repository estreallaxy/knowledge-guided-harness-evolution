import json
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
import os
import glob

def extract_metrics_from_json(json_file_path):
    """从JSON文件中提取指标数据"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
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
    if 'trajectory_reward_metrics' in data:
        traj_metrics = data['trajectory_reward_metrics']
        overall_metrics = traj_metrics.get('overall', {})
        by_task_type = traj_metrics.get('by_task_type', {})
        
        traj_result = {}
        
        # Overall数据
        traj_result['overall'] = {
            'P': round(overall_metrics.get('precision', 0) * 100, 1),
            'NPV': round(overall_metrics.get('npv', 0) * 100, 1),
            'R': round(overall_metrics.get('recall', 0) * 100, 1),
            'OA': round(overall_metrics.get('accuracy', 0) * 100, 1)  # trajectory用accuracy
        }
        
        # 各任务类型数据
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
    if 'action_reward_metrics' in data:
        action_metrics = data['action_reward_metrics']
        overall_metrics = action_metrics.get('overall', {})
        by_task_type = action_metrics.get('by_task_type', {})
        
        action_result = {}
        
        # Overall数据
        action_result['overall'] = {
            'P': round(overall_metrics.get('precision', 0) * 100, 1),
            'NPV': round(overall_metrics.get('npv', 0) * 100, 1),
            'R': round(overall_metrics.get('recall', 0) * 100, 1),
            'OA': round(overall_metrics.get('oa', 0) * 100, 1)  # action用oa
        }
        
        # 各任务类型数据
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

def create_combined_excel_table(all_files_data, output_file):
    """创建包含所有文件数据的Excel表格"""
    
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
    for col_name in columns:
        # 合并4列作为一个任务类型的标题
        start_col = col_start
        end_col = col_start + 3
        ws.merge_cells(start_row=1, start_column=start_col, end_row=1, end_column=end_col)
        cell = ws.cell(row=1, column=start_col)
        cell.value = col_name.replace('_', ' ').title()
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # 第二行：P, NPV, R, OA
        for i, metric in enumerate(['P', 'NPV', 'R', 'OA']):
            cell = ws.cell(row=2, column=start_col + i)
            cell.value = metric
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        col_start += 4
    
    # 添加数据行
    current_row = 3
    
    # 遍历所有文件的数据
    for file_data in all_files_data:
        model_name = file_data['model_name']
        metrics_data = file_data['metrics_data']
        
        # 添加trajectory数据行（如果存在）
        if 'trajectory' in metrics_data:
            ws.cell(row=current_row, column=1).value = f"{model_name}_trajectory"
            ws.cell(row=current_row, column=1).font = Font(bold=True)
            
            col = 2
            traj_metrics = metrics_data['trajectory']
            for col_name in columns:
                if col_name in traj_metrics:
                    data = traj_metrics[col_name]
                    ws.cell(row=current_row, column=col).value = data['P']
                    ws.cell(row=current_row, column=col+1).value = data['NPV']
                    ws.cell(row=current_row, column=col+2).value = data['R']
                    ws.cell(row=current_row, column=col+3).value = data['OA']
                col += 4
            current_row += 1
        
        # 添加action数据行（如果存在）
        if 'action' in metrics_data:
            ws.cell(row=current_row, column=1).value = f"{model_name}_action"
            ws.cell(row=current_row, column=1).font = Font(bold=True)
            
            col = 2
            action_metrics = metrics_data['action']
            for col_name in columns:
                if col_name in action_metrics:
                    data = action_metrics[col_name]
                    ws.cell(row=current_row, column=col).value = data['P']
                    ws.cell(row=current_row, column=col+1).value = data['NPV']
                    ws.cell(row=current_row, column=col+2).value = data['R']
                    ws.cell(row=current_row, column=col+3).value = data['OA']
                col += 4
            current_row += 1
    
    # 设置边框
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # 应用边框到所有使用的单元格
    max_row = current_row - 1
    max_col = 2 + len(columns) * 4 - 1
    
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
    print(f"合并的Excel文件已保存到: {output_file}")

def process_single_file_data(json_file):
    """处理单个JSON文件并返回数据（不直接保存Excel）"""
    # 检查文件是否存在
    if not os.path.exists(json_file):
        print(f"错误: 找不到文件 {json_file}")
        return None
    
    try:
        # 提取数据
        print(f"正在处理文件: {json_file}")
        all_metrics_data = extract_metrics_from_json(json_file)
        
        # 从文件名中提取模型名称 - 保持原始文件名格式
        filename = os.path.basename(json_file)
        # 直接使用文件名（去掉.json扩展名）作为模型名称
        model_name = filename.replace('.json', '').replace('metrics_', '').replace('cuarewardbench-v0.4_', '')
        
        # 打印提取的数据供验证
        print(f"模型: {model_name}")
        for metric_type, metrics_data in all_metrics_data.items():
            print(f"  {metric_type.upper()} 指标已提取")
        
        return {
            'model_name': model_name,
            'metrics_data': all_metrics_data
        }
        
    except Exception as e:
        print(f"处理文件 {json_file} 时出错: {str(e)}")
        return None

def process_file_list(file_list, output_file="combined_metrics.xlsx"):
    """处理文件列表并生成合并的Excel文件"""
    print(f"文件列表批量处理模式")
    print(f"待处理文件数量: {len(file_list)}")
    
    all_files_data = []
    success_count = 0
    
    for json_file in file_list:
        file_data = process_single_file_data(json_file)
        if file_data:
            all_files_data.append(file_data)
            success_count += 1
        print("-" * 30)
    
    if all_files_data:
        # 创建合并的Excel文件
        create_combined_excel_table(all_files_data, output_file)
        print(f"批量处理完成! 成功处理: {success_count}/{len(file_list)} 个文件")
        print(f"所有结果已合并到: {output_file}")
    else:
        print("没有成功处理任何文件，未生成Excel文件")
    
    return success_count

def find_files_by_keyword(keyword, search_dir="results"):
    """根据关键字在指定目录中查找JSON文件"""
    if not os.path.exists(search_dir):
        print(f"错误: 目录 {search_dir} 不存在")
        return []
    
    # 使用glob查找包含关键字的JSON文件
    pattern = os.path.join(search_dir, f"*{keyword}*.json")
    files = glob.glob(pattern)
    
    # 过滤出metrics文件
    metrics_files = [f for f in files if 'metrics_' in os.path.basename(f)]
    
    return sorted(metrics_files)

def process_keyword_search(keyword, search_directory="results", output_file="combined_metrics.xlsx"):
    """关键字匹配批量处理"""
    print(f"关键字匹配批量处理模式")
    print(f"搜索关键字: '{keyword}'")
    print(f"搜索目录: '{search_directory}'")
    
    # 查找匹配的文件
    matched_files = find_files_by_keyword(keyword, search_directory)
    
    if not matched_files:
        print(f"未找到包含关键字 '{keyword}' 的metrics文件")
        return 0
    
    print(f"找到 {len(matched_files)} 个匹配的文件:")
    for f in matched_files:
        print(f"  - {f}")
    print("-" * 30)
    
    # 批量处理匹配的文件并生成合并的Excel
    success_count = process_file_list(matched_files, output_file)
    
    return success_count

def detect_input_type(input_data):
    """自动检测输入数据类型"""
    if isinstance(input_data, str):
        return 'keyword', input_data
    elif isinstance(input_data, list):
        # 列表类型，文件列表处理
        return 'file_list', input_data
    else:
        raise ValueError(f"不支持的输入类型: {type(input_data)}")

def main():
    """主函数"""
    print("JSON到Excel转换工具 - 合并版本")
    print("=" * 50)
    print("支持自动识别输入类型:")
    print("- 字符串文件路径: 单文件处理")
    print("- 文件路径列表: 批量文件处理")
    print("- 关键字字符串: 关键字匹配批量处理")
    print("所有结果将合并到同一个Excel文件中")
    print("=" * 50)
    
    # 配置区域 - 用户只需要修改这里的input_data
    
    # 示例1: 文件列表批量处理（列表）
    input_data = [
        "results/voted_majority_sewsm_Qwen2.5-VL-32B-Instruct_sewsm_Qwen2.5-VL-32B-Instruct_run1_sewsm_Qwen2.5-VL-32B-Instruct_run3.json",
        "results/voted_majority_sewsm_glm-4.5v_sewsm_glm-4.5v_run2.json"
    ]
    
    # 示例2: 关键字匹配批量处理（关键字字符串）
    # input_data = "Qwen2.5-VL-7B-Instruct"
    
    # 可选：指定搜索目录（仅对关键字模式有效）
    search_directory = "results"
    
    # 输出文件名配置
    output_file = "combined_metrics.xlsx"
    
    try:
        # 自动检测输入类型
        input_type, processed_data = detect_input_type(input_data)
        
        print(f"检测到输入类型: {input_type}")
        print(f"输出文件: {output_file}")
        print("-" * 30)
        
        # 根据检测到的类型执行相应处理
        if input_type == 'file_list':
            success_count = process_file_list(processed_data, output_file)
        elif input_type == 'keyword':
            success_count = process_keyword_search(processed_data, search_directory, output_file)
        else:
            print(f"错误: 未知的输入类型 {input_type}")
            return
        
        print("=" * 50)
        if success_count > 0:
            print(f"处理完成! 共成功处理 {success_count} 个文件")
            print(f"所有结果已合并保存到: {output_file}")
        else:
            print("处理完成，但没有成功处理任何文件")
            
    except Exception as e:
        print(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()