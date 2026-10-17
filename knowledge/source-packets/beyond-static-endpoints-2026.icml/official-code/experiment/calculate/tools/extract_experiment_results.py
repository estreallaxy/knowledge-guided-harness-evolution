#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验结果数据提取脚本
用于统一提取和统计DynamicWasm和Baseline实验结果的相关字段
"""

import json
import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ExperimentDataExtractor:
    def __init__(self, results_dir):
        """
        初始化数据提取器
        
        Args:
            results_dir: 实验结果根目录路径
        """
        self.results_dir = Path(results_dir)
        self.dw_data = {}
        self.baseline_data = {}
        
    def extract_dw_data(self):
        """提取DynamicWasm实验数据"""
        print("正在提取DynamicWasm实验数据...")
        
        dw_dir = self.results_dir / "dw"
        if not dw_dir.exists():
            print(f"警告: DW目录不存在: {dw_dir}")
            return
            
        # 遍历批次目录 (5, 15, 25, 35)
        for batch_dir in dw_dir.iterdir():
            if batch_dir.is_dir():
                batch_size = batch_dir.name
                self.dw_data[batch_size] = {}
                
                # 遍历每个JSON文件
                for json_file in batch_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 提取应用名称和工作流类型
                        app_name = data.get('application', 'Unknown')
                        workflow = data.get('workflow', 'Unknown')
                        
                        # 提取统计信息
                        stats = data.get('summary_statistics', {})
                        
                        # 提取所需字段（使用平均值）
                        extracted_data = {
                            'avg_total_traffic': stats.get('avg_total_traffic', 0),
                            'avg_llm_traffic': stats.get('avg_llm_traffic', 0),
                            'avg_communication_traffic': stats.get('avg_communication_traffic', 0),
                            'avg_total_time': stats.get('avg_total_time', 0),
                            'avg_llm_time': stats.get('avg_llm_time', 0),
                            'avg_communication_time': stats.get('avg_communication_time', 0),
                            'success_rate': stats.get('success_rate', 0),
                            'successful_rounds': stats.get('successful_rounds', 0)
                        }
                        
                        # 生成唯一键
                        key = f"{app_name}_{workflow}"
                        self.dw_data[batch_size][key] = extracted_data
                        
                        print(f"  - 提取 {batch_size}批次 {key}: 成功")
                        
                    except Exception as e:
                        print(f"  - 处理文件 {json_file} 时出错: {e}")
    
    def extract_baseline_data(self):
        """提取Baseline实验数据"""
        print("正在提取Baseline实验数据...")
        
        baseline_dir = self.results_dir / "baseline"
        if not baseline_dir.exists():
            print(f"警告: Baseline目录不存在: {baseline_dir}")
            return
            
        # 遍历批次目录 (5, 15, 25, 35)
        for batch_dir in baseline_dir.iterdir():
            if batch_dir.is_dir():
                batch_size = batch_dir.name
                self.baseline_data[batch_size] = {}
                
                # 遍历每个JSON文件
                for json_file in batch_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 提取应用名称和测试类型
                        test_info = data.get('test_info', {})
                        app_name = test_info.get('application', 'Unknown')
                        test_type = test_info.get('test_type', 'Unknown')
                        
                        # 提取流量统计信息
                        traffic_summary = data.get('traffic_summary', {})
                        
                        # 提取所需字段（使用平均值）
                        extracted_data = {
                            'llm_avg_traffic_bytes': traffic_summary.get('llm', {}).get('average_traffic_per_batch', 0),
                            'llm_avg_time_seconds': traffic_summary.get('llm', {}).get('average_time_per_batch', 0),
                            'mcp_avg_traffic_bytes': traffic_summary.get('mcp', {}).get('average_traffic_per_batch', 0),
                            'mcp_avg_time_seconds': traffic_summary.get('mcp', {}).get('average_time_per_batch', 0),
                            'total_avg_traffic_bytes': traffic_summary.get('total', {}).get('average_traffic_per_batch', 0),
                            'total_avg_time_seconds': traffic_summary.get('total', {}).get('average_time_per_batch', 0)
                        }
                        
                        # 生成唯一键
                        key = f"{app_name}_{test_type}"
                        self.baseline_data[batch_size][key] = extracted_data
                        
                        print(f"  - 提取 {batch_size}批次 {key}: 成功")
                        
                    except Exception as e:
                        print(f"  - 处理文件 {json_file} 时出错: {e}")
    
    def generate_summary_report(self):
        """生成汇总报告"""
        print("正在生成汇总报告...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"experiment_summary_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("DynamicWasm vs Baseline 实验结果汇总报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # DW数据汇总
            f.write("DynamicWasm 实验结果\n")
            f.write("-" * 30 + "\n")
            for batch_size, workflows in self.dw_data.items():
                f.write(f"\n{batch_size}批次测试:\n")
                for workflow, data in workflows.items():
                    f.write(f"  {workflow}:\n")
                    f.write(f"    平均总流量: {data['avg_total_traffic']:.0f} bytes\n")
                    f.write(f"    平均LLM流量: {data['avg_llm_traffic']:.0f} bytes\n")
                    f.write(f"    平均通信流量: {data['avg_communication_traffic']:.0f} bytes\n")
                    f.write(f"    平均总时间: {data['avg_total_time']:.2f} 秒\n")
                    f.write(f"    平均LLM时间: {data['avg_llm_time']:.2f} 秒\n")
                    f.write(f"    平均通信时间: {data['avg_communication_time']:.2f} 秒\n")
                    f.write(f"    成功率: {data['success_rate']:.1f}%\n")
                    f.write(f"    成功轮次: {data['successful_rounds']}\n")
            
            # Baseline数据汇总
            f.write("\n\nBaseline 实验结果\n")
            f.write("-" * 30 + "\n")
            for batch_size, workflows in self.baseline_data.items():
                f.write(f"\n{batch_size}批次测试:\n")
                for workflow, data in workflows.items():
                    f.write(f"  {workflow}:\n")
                    f.write(f"    平均LLM流量: {data['llm_avg_traffic_bytes']:.0f} bytes\n")
                    f.write(f"    平均LLM时间: {data['llm_avg_time_seconds']:.2f} 秒\n")
                    f.write(f"    平均MCP流量: {data['mcp_avg_traffic_bytes']:.0f} bytes\n")
                    f.write(f"    平均MCP时间: {data['mcp_avg_time_seconds']:.2f} 秒\n")
                    f.write(f"    平均总流量: {data['total_avg_traffic_bytes']:.0f} bytes\n")
                    f.write(f"    平均总时间: {data['total_avg_time_seconds']:.2f} 秒\n")
        
        print(f"汇总报告已保存至: {report_file}")
        return report_file
    
    def create_comparison_tables(self):
        """创建按应用分组的对比表格"""
        print("正在创建按应用分组的对比表格...")
        
        # 定义应用映射
        app_mapping = {
            'Directus': {
                'dw_read': 'Directus_只读阶段',
                'dw_write': 'Directus_读写阶段', 
                'baseline_read': 'directus_read_only',
                'baseline_write': 'directus_read_write'
            },
            'Memos': {
                'dw_read': 'Memos_只读阶段',
                'dw_write': 'Memos_读写阶段',
                'baseline_read': 'memos_read_only', 
                'baseline_write': 'memos_read_write'
            },
            'MinIO': {
                'dw_read': 'MinIO_只读阶段',
                'dw_write': 'MinIO_读写阶段',
                'baseline_read': 'minio_download',
                'baseline_write': 'minio_upload'
            }
        }
        
        app_tables = {}
        
        # 为每个应用创建对比表格
        for app_name, workflows in app_mapping.items():
            print(f"正在创建 {app_name} 应用对比表格...")
            
            # 准备表格数据
            table_data = []
            batch_sizes = ['5', '15', '25', '35']
            
            for batch_size in batch_sizes:
                # DW只读数据
                dw_read_data = self._get_workflow_data(self.dw_data, batch_size, workflows['dw_read'])
                # DW读写数据  
                dw_write_data = self._get_workflow_data(self.dw_data, batch_size, workflows['dw_write'])
                # Baseline只读数据
                baseline_read_data = self._get_workflow_data(self.baseline_data, batch_size, workflows['baseline_read'])
                # Baseline读写数据
                baseline_write_data = self._get_workflow_data(self.baseline_data, batch_size, workflows['baseline_write'])
                
                # 添加DW只读行
                table_data.append({
                    '批次': f'{batch_size}批次',
                    '工作流类型': 'DW-只读',
                    '平均LLM流量(bytes)': round(dw_read_data['avg_llm_traffic'], 0),
                    '平均LLM时间(秒)': round(dw_read_data['avg_llm_time'], 2),
                    '平均通信流量(bytes)': round(dw_read_data['avg_communication_traffic'], 0),
                    '平均通信时间(秒)': round(dw_read_data['avg_communication_time'], 2),
                    '平均总流量(bytes)': round(dw_read_data['avg_total_traffic'], 0),
                    '平均总时间(秒)': round(dw_read_data['avg_total_time'], 2),
                    '成功率(%)': round(dw_read_data['success_rate'], 1),
                    '成功轮次': dw_read_data['successful_rounds']
                })
                
                # 添加DW读写行
                table_data.append({
                    '批次': f'{batch_size}批次',
                    '工作流类型': 'DW-读写',
                    '平均LLM流量(bytes)': round(dw_write_data['avg_llm_traffic'], 0),
                    '平均LLM时间(秒)': round(dw_write_data['avg_llm_time'], 2),
                    '平均通信流量(bytes)': round(dw_write_data['avg_communication_traffic'], 0),
                    '平均通信时间(秒)': round(dw_write_data['avg_communication_time'], 2),
                    '平均总流量(bytes)': round(dw_write_data['avg_total_traffic'], 0),
                    '平均总时间(秒)': round(dw_write_data['avg_total_time'], 2),
                    '成功率(%)': round(dw_write_data['success_rate'], 1),
                    '成功轮次': dw_write_data['successful_rounds']
                })
                
                # 添加Baseline只读行
                table_data.append({
                    '批次': f'{batch_size}批次',
                    '工作流类型': 'Baseline-只读',
                    '平均LLM流量(bytes)': round(baseline_read_data['llm_avg_traffic_bytes'], 0),
                    '平均LLM时间(秒)': round(baseline_read_data['llm_avg_time_seconds'], 2),
                    '平均通信流量(bytes)': round(baseline_read_data['mcp_avg_traffic_bytes'], 0),
                    '平均通信时间(秒)': round(baseline_read_data['mcp_avg_time_seconds'], 2),
                    '平均总流量(bytes)': round(baseline_read_data['total_avg_traffic_bytes'], 0),
                    '平均总时间(秒)': round(baseline_read_data['total_avg_time_seconds'], 2),
                    '成功率(%)': '-',
                    '成功轮次': '-'
                })
                
                # 添加Baseline读写行
                table_data.append({
                    '批次': f'{batch_size}批次',
                    '工作流类型': 'Baseline-读写',
                    '平均LLM流量(bytes)': round(baseline_write_data['llm_avg_traffic_bytes'], 0),
                    '平均LLM时间(秒)': round(baseline_write_data['llm_avg_time_seconds'], 2),
                    '平均通信流量(bytes)': round(baseline_write_data['mcp_avg_traffic_bytes'], 0),
                    '平均通信时间(秒)': round(baseline_write_data['mcp_avg_time_seconds'], 2),
                    '平均总流量(bytes)': round(baseline_write_data['total_avg_traffic_bytes'], 0),
                    '平均总时间(秒)': round(baseline_write_data['total_avg_time_seconds'], 2),
                    '成功率(%)': '-',
                    '成功轮次': '-'
                })
            
            # 创建DataFrame
            df = pd.DataFrame(table_data)
            app_tables[app_name] = df
            
            # 保存为CSV
            csv_file = f"{app_name}_应用对比结果.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"{app_name} 应用对比表格已保存至: {csv_file}")
        
        return app_tables
    
    def _get_workflow_data(self, data_dict, batch_size, workflow_name):
        """获取指定工作流的数据，如果不存在则返回默认值"""
        if batch_size in data_dict and workflow_name in data_dict[batch_size]:
            return data_dict[batch_size][workflow_name]
        else:
            # 返回默认值
            if 'avg_' in str(data_dict):  # DW数据
                return {
                    'avg_total_traffic': 0,
                    'avg_llm_traffic': 0,
                    'avg_communication_traffic': 0,
                    'avg_total_time': 0,
                    'avg_llm_time': 0,
                    'avg_communication_time': 0,
                    'success_rate': 0,
                    'successful_rounds': 0
                }
            else:  # Baseline数据
                return {
                    'llm_avg_traffic_bytes': 0,
                    'llm_avg_time_seconds': 0,
                    'mcp_avg_traffic_bytes': 0,
                    'mcp_avg_time_seconds': 0,
                    'total_avg_traffic_bytes': 0,
                    'total_avg_time_seconds': 0
                }
    
    def create_comparison_charts(self, app_tables):
        """创建按应用分组的对比图表"""
        print("正在创建按应用分组的对比图表...")
        
        # 创建图表输出目录
        charts_dir = Path("comparison_charts")
        charts_dir.mkdir(exist_ok=True)
        
        # 为每个应用创建对比图
        for app_name, df in app_tables.items():
            print(f"正在创建 {app_name} 应用对比图...")
            
            # 创建子图 (2行3列)
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle(f'{app_name} 应用 - DynamicWasm vs Baseline 对比', fontsize=16, fontweight='bold')
            
            # 准备数据
            batch_sizes = ['5', '15', '25', '35']
            dw_read_data = {'traffic': [], 'time': [], 'llm_traffic': [], 'llm_time': [], 'comm_traffic': [], 'comm_time': []}
            dw_write_data = {'traffic': [], 'time': [], 'llm_traffic': [], 'llm_time': [], 'comm_traffic': [], 'comm_time': []}
            baseline_read_data = {'traffic': [], 'time': [], 'llm_traffic': [], 'llm_time': [], 'mcp_traffic': [], 'mcp_time': []}
            baseline_write_data = {'traffic': [], 'time': [], 'llm_traffic': [], 'llm_time': [], 'mcp_traffic': [], 'mcp_time': []}
            
            for batch_size in batch_sizes:
                # 从表格中提取数据
                batch_df = df[df['批次'] == f'{batch_size}批次']
                
                # DW只读数据
                dw_read_row = batch_df[batch_df['工作流类型'] == 'DW-只读']
                if not dw_read_row.empty:
                    row = dw_read_row.iloc[0]
                    dw_read_data['traffic'].append(row['平均总流量(bytes)'])
                    dw_read_data['time'].append(row['平均总时间(秒)'])
                    dw_read_data['llm_traffic'].append(row['平均LLM流量(bytes)'])
                    dw_read_data['llm_time'].append(row['平均LLM时间(秒)'])
                    dw_read_data['comm_traffic'].append(row['平均通信流量(bytes)'])
                    dw_read_data['comm_time'].append(row['平均通信时间(秒)'])
                else:
                    dw_read_data['traffic'].append(0)
                    dw_read_data['time'].append(0)
                    dw_read_data['llm_traffic'].append(0)
                    dw_read_data['llm_time'].append(0)
                    dw_read_data['comm_traffic'].append(0)
                    dw_read_data['comm_time'].append(0)
                
                # DW读写数据
                dw_write_row = batch_df[batch_df['工作流类型'] == 'DW-读写']
                if not dw_write_row.empty:
                    row = dw_write_row.iloc[0]
                    dw_write_data['traffic'].append(row['平均总流量(bytes)'])
                    dw_write_data['time'].append(row['平均总时间(秒)'])
                    dw_write_data['llm_traffic'].append(row['平均LLM流量(bytes)'])
                    dw_write_data['llm_time'].append(row['平均LLM时间(秒)'])
                    dw_write_data['comm_traffic'].append(row['平均通信流量(bytes)'])
                    dw_write_data['comm_time'].append(row['平均通信时间(秒)'])
                else:
                    dw_write_data['traffic'].append(0)
                    dw_write_data['time'].append(0)
                    dw_write_data['llm_traffic'].append(0)
                    dw_write_data['llm_time'].append(0)
                    dw_write_data['comm_traffic'].append(0)
                    dw_write_data['comm_time'].append(0)
                
                # Baseline只读数据
                baseline_read_row = batch_df[batch_df['工作流类型'] == 'Baseline-只读']
                if not baseline_read_row.empty:
                    row = baseline_read_row.iloc[0]
                    baseline_read_data['traffic'].append(row['平均总流量(bytes)'])
                    baseline_read_data['time'].append(row['平均总时间(秒)'])
                    baseline_read_data['llm_traffic'].append(row['平均LLM流量(bytes)'])
                    baseline_read_data['llm_time'].append(row['平均LLM时间(秒)'])
                    baseline_read_data['mcp_traffic'].append(row['平均通信流量(bytes)'])
                    baseline_read_data['mcp_time'].append(row['平均通信时间(秒)'])
                else:
                    baseline_read_data['traffic'].append(0)
                    baseline_read_data['time'].append(0)
                    baseline_read_data['llm_traffic'].append(0)
                    baseline_read_data['llm_time'].append(0)
                    baseline_read_data['mcp_traffic'].append(0)
                    baseline_read_data['mcp_time'].append(0)
                
                # Baseline读写数据
                baseline_write_row = batch_df[batch_df['工作流类型'] == 'Baseline-读写']
                if not baseline_write_row.empty:
                    row = baseline_write_row.iloc[0]
                    baseline_write_data['traffic'].append(row['平均总流量(bytes)'])
                    baseline_write_data['time'].append(row['平均总时间(秒)'])
                    baseline_write_data['llm_traffic'].append(row['平均LLM流量(bytes)'])
                    baseline_write_data['llm_time'].append(row['平均LLM时间(秒)'])
                    baseline_write_data['mcp_traffic'].append(row['平均通信流量(bytes)'])
                    baseline_write_data['mcp_time'].append(row['平均通信时间(秒)'])
                else:
                    baseline_write_data['traffic'].append(0)
                    baseline_write_data['time'].append(0)
                    baseline_write_data['llm_traffic'].append(0)
                    baseline_write_data['llm_time'].append(0)
                    baseline_write_data['mcp_traffic'].append(0)
                    baseline_write_data['mcp_time'].append(0)
            
            x = range(len(batch_sizes))
            width = 0.15
            
            # 1. 总流量对比 (只读 vs 读写)
            ax1 = axes[0, 0]
            ax1.bar([i - width*1.5 for i in x], dw_read_data['traffic'], width, label='DW-只读', alpha=0.8, color='skyblue')
            ax1.bar([i - width*0.5 for i in x], dw_write_data['traffic'], width, label='DW-读写', alpha=0.8, color='lightblue')
            ax1.bar([i + width*0.5 for i in x], baseline_read_data['traffic'], width, label='Baseline-只读', alpha=0.8, color='lightcoral')
            ax1.bar([i + width*1.5 for i in x], baseline_write_data['traffic'], width, label='Baseline-读写', alpha=0.8, color='salmon')
            ax1.set_title('平均总流量对比')
            ax1.set_ylabel('流量 (bytes)')
            ax1.set_xticks(x)
            ax1.set_xticklabels([f'{size}批次' for size in batch_sizes])
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 2. 总时间对比
            ax2 = axes[0, 1]
            ax2.bar([i - width*1.5 for i in x], dw_read_data['time'], width, label='DW-只读', alpha=0.8, color='skyblue')
            ax2.bar([i - width*0.5 for i in x], dw_write_data['time'], width, label='DW-读写', alpha=0.8, color='lightblue')
            ax2.bar([i + width*0.5 for i in x], baseline_read_data['time'], width, label='Baseline-只读', alpha=0.8, color='lightcoral')
            ax2.bar([i + width*1.5 for i in x], baseline_write_data['time'], width, label='Baseline-读写', alpha=0.8, color='salmon')
            ax2.set_title('平均总时间对比')
            ax2.set_ylabel('时间 (秒)')
            ax2.set_xticks(x)
            ax2.set_xticklabels([f'{size}批次' for size in batch_sizes])
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 3. LLM流量对比
            ax3 = axes[0, 2]
            ax3.bar([i - width*1.5 for i in x], dw_read_data['llm_traffic'], width, label='DW-只读', alpha=0.8, color='skyblue')
            ax3.bar([i - width*0.5 for i in x], dw_write_data['llm_traffic'], width, label='DW-读写', alpha=0.8, color='lightblue')
            ax3.bar([i + width*0.5 for i in x], baseline_read_data['llm_traffic'], width, label='Baseline-只读', alpha=0.8, color='lightcoral')
            ax3.bar([i + width*1.5 for i in x], baseline_write_data['llm_traffic'], width, label='Baseline-读写', alpha=0.8, color='salmon')
            ax3.set_title('平均LLM流量对比')
            ax3.set_ylabel('流量 (bytes)')
            ax3.set_xticks(x)
            ax3.set_xticklabels([f'{size}批次' for size in batch_sizes])
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # 4. LLM时间对比
            ax4 = axes[1, 0]
            ax4.bar([i - width*1.5 for i in x], dw_read_data['llm_time'], width, label='DW-只读', alpha=0.8, color='skyblue')
            ax4.bar([i - width*0.5 for i in x], dw_write_data['llm_time'], width, label='DW-读写', alpha=0.8, color='lightblue')
            ax4.bar([i + width*0.5 for i in x], baseline_read_data['llm_time'], width, label='Baseline-只读', alpha=0.8, color='lightcoral')
            ax4.bar([i + width*1.5 for i in x], baseline_write_data['llm_time'], width, label='Baseline-读写', alpha=0.8, color='salmon')
            ax4.set_title('平均LLM时间对比')
            ax4.set_ylabel('时间 (秒)')
            ax4.set_xticks(x)
            ax4.set_xticklabels([f'{size}批次' for size in batch_sizes])
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # 5. 通信流量对比 (DW通信 vs Baseline MCP)
            ax5 = axes[1, 1]
            ax5.bar([i - width*1.5 for i in x], dw_read_data['comm_traffic'], width, label='DW-只读', alpha=0.8, color='skyblue')
            ax5.bar([i - width*0.5 for i in x], dw_write_data['comm_traffic'], width, label='DW-读写', alpha=0.8, color='lightblue')
            ax5.bar([i + width*0.5 for i in x], baseline_read_data['mcp_traffic'], width, label='Baseline-只读', alpha=0.8, color='lightcoral')
            ax5.bar([i + width*1.5 for i in x], baseline_write_data['mcp_traffic'], width, label='Baseline-读写', alpha=0.8, color='salmon')
            ax5.set_title('平均通信流量对比')
            ax5.set_ylabel('流量 (bytes)')
            ax5.set_xticks(x)
            ax5.set_xticklabels([f'{size}批次' for size in batch_sizes])
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            
            # 6. 通信时间对比
            ax6 = axes[1, 2]
            ax6.bar([i - width*1.5 for i in x], dw_read_data['comm_time'], width, label='DW-只读', alpha=0.8, color='skyblue')
            ax6.bar([i - width*0.5 for i in x], dw_write_data['comm_time'], width, label='DW-读写', alpha=0.8, color='lightblue')
            ax6.bar([i + width*0.5 for i in x], baseline_read_data['mcp_time'], width, label='Baseline-只读', alpha=0.8, color='lightcoral')
            ax6.bar([i + width*1.5 for i in x], baseline_write_data['mcp_time'], width, label='Baseline-读写', alpha=0.8, color='salmon')
            ax6.set_title('平均通信时间对比')
            ax6.set_ylabel('时间 (秒)')
            ax6.set_xticks(x)
            ax6.set_xticklabels([f'{size}批次' for size in batch_sizes])
            ax6.legend()
            ax6.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 保存图表
            chart_file = charts_dir / f"{app_name}_应用对比图.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"{app_name} 应用对比图已保存至: {chart_file}")
    
    def run_extraction(self):
        """运行完整的数据提取流程"""
        print("开始提取实验结果数据...")
        print("=" * 50)
        
        # 提取数据
        self.extract_dw_data()
        self.extract_baseline_data()
        
        # 生成报告
        report_file = self.generate_summary_report()
        
        # 创建按应用分组的对比表格
        app_tables = self.create_comparison_tables()
        
        # 创建图表
        self.create_comparison_charts(app_tables)
        
        print("\n" + "=" * 50)
        print("数据提取完成!")
        print(f"汇总报告: {report_file}")
        print("按应用分组的CSV表格文件已生成:")
        for app_name in app_tables.keys():
            print(f"  - {app_name}_应用对比结果.csv")
        print("对比图表已保存至 comparison_charts/ 目录")
        
        return {
            'report_file': report_file,
            'app_tables': app_tables
        }

def main():
    """主函数"""
    # 设置实验结果目录路径
    results_dir = "../results/10_6/application_test"
    
    # 创建提取器并运行
    extractor = ExperimentDataExtractor(results_dir)
    results = extractor.run_extraction()
    
    return results

if __name__ == "__main__":
    main()
