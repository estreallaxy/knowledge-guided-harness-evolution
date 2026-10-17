#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能分析工具
用于分析DynamicWasm和MCP的测试结果，绘制对比图表并计算差值
"""

import json
import os
import sys
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.apps = ['MinIO', 'Directus', 'Memos']
        self.metrics = {
            'duration_mean': '执行时间 (秒)',
            'llm_traffic_mean': 'LLM交互阶段流量 (字节)',
            'communication_traffic_mean': '通信阶段流量 (字节)',
            'api_traffic_mean': 'API交互阶段流量 (字节)',
            'total_traffic_mean': '总流量开销 (字节)'
        }
        
    def load_test_results(self, dw_path: str, mcp_path: str) -> Tuple[Dict, Dict]:
        """
        加载测试结果数据
        
        Args:
            dw_path: DynamicWasm结果目录路径
            mcp_path: MCP结果目录路径
            
        Returns:
            (dw_data, mcp_data): 两个字典，包含各应用的统计数据
        """
        dw_data = {}
        mcp_data = {}
        
        # 加载DynamicWasm数据
        for app in self.apps:
            dw_file = self._find_json_file(dw_path, app)
            if dw_file:
                dw_data[app] = self._load_json_file(dw_file)
            else:
                print(f"警告: 在 {dw_path} 中未找到 {app} 的测试结果文件")
                
        # 加载MCP数据
        for app in self.apps:
            mcp_file = self._find_json_file(mcp_path, app)
            if mcp_file:
                mcp_data[app] = self._load_json_file(mcp_file)
            else:
                print(f"警告: 在 {mcp_path} 中未找到 {app} 的测试结果文件")
                
        return dw_data, mcp_data
    
    def _find_json_file(self, directory: str, app_name: str) -> str:
        """在目录中查找指定应用的JSON文件"""
        if not os.path.exists(directory):
            return None
            
        for file in os.listdir(directory):
            if file.startswith(app_name) and file.endswith('.json'):
                return os.path.join(directory, file)
        return None
    
    def _load_json_file(self, file_path: str) -> Dict:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"错误: 无法加载文件 {file_path}: {e}")
            return {}
    
    def extract_metrics(self, data: Dict[str, Dict], is_dw: bool = True) -> Dict[str, Dict[str, float]]:
        """
        从测试数据中提取关键指标
        
        Args:
            data: 测试数据字典
            is_dw: 是否为DynamicWasm数据 (True) 或MCP数据 (False)
            
        Returns:
            提取的指标字典
        """
        metrics_data = {}
        
        for app, app_data in data.items():
            if not app_data:
                continue
                
            stats = app_data.get('statistics', {})
            
            # 提取执行时间
            duration_mean = stats.get('duration', {}).get('mean', 0)
            
            # 提取LLM交互阶段流量
            llm_traffic_mean = stats.get('llm_network_traffic', {}).get('total_bytes_mean', 0)
            
            # 提取API交互阶段流量
            api_traffic_mean = stats.get('api_network_traffic', {}).get('total_bytes_mean', 0)
            
            # 提取总流量开销
            total_traffic_mean = stats.get('network_traffic', {}).get('total_bytes_mean', 0)
            
            # 提取通信阶段流量 - 根据数据类型选择不同字段
            if is_dw:
                # DynamicWasm使用wasm_network_traffic
                communication_traffic_mean = stats.get('wasm_network_traffic', {}).get('total_bytes_mean', 0)
            else:
                # MCP使用mcp_network_traffic
                communication_traffic_mean = stats.get('mcp_network_traffic', {}).get('total_bytes_mean', 0)
            
            metrics_data[app] = {
                'duration_mean': duration_mean,
                'llm_traffic_mean': llm_traffic_mean,
                'communication_traffic_mean': communication_traffic_mean,
                'api_traffic_mean': api_traffic_mean,
                'total_traffic_mean': total_traffic_mean
            }
            
        return metrics_data
    
    def debug_data_extraction(self, data: Dict[str, Dict], is_dw: bool = True):
        """调试数据提取过程，打印详细的字段信息"""
        print("\n" + "="*80)
        print(f"数据提取调试信息 - {'DynamicWasm' if is_dw else 'MCP'}")
        print("="*80)
        
        for app, app_data in data.items():
            if not app_data:
                continue
                
            print(f"\n【{app} 应用】")
            print("-" * 50)
            
            stats = app_data.get('statistics', {})
            
            # 打印所有可用的流量统计字段
            print("可用的流量统计字段:")
            for key, value in stats.items():
                if 'traffic' in key.lower() or 'duration' in key.lower():
                    if isinstance(value, dict) and 'total_bytes_mean' in value:
                        print(f"  {key}.total_bytes_mean: {value['total_bytes_mean']}")
                    elif isinstance(value, dict) and 'mean' in value:
                        print(f"  {key}.mean: {value['mean']}")
            
            # 特别检查通信阶段流量字段
            if is_dw:
                wasm_traffic = stats.get('wasm_network_traffic', {})
                print(f"\nWASM通信流量: {wasm_traffic.get('total_bytes_mean', 'N/A')}")
            else:
                mcp_traffic = stats.get('mcp_network_traffic', {})
                print(f"\nMCP通信流量: {mcp_traffic.get('total_bytes_mean', 'N/A')}")
    
    def calculate_differences(self, dw_metrics: Dict, mcp_metrics: Dict) -> Dict[str, Dict[str, float]]:
        """
        计算DynamicWasm和MCP之间的性能差值
        
        Args:
            dw_metrics: DynamicWasm指标数据
            mcp_metrics: MCP指标数据
            
        Returns:
            差值计算结果
        """
        differences = {}
        
        for app in self.apps:
            if app not in dw_metrics or app not in mcp_metrics:
                continue
                
            differences[app] = {}
            dw_data = dw_metrics[app]
            mcp_data = mcp_metrics[app]
            
            for metric in self.metrics.keys():
                dw_value = dw_data.get(metric, 0)
                mcp_value = mcp_data.get(metric, 0)
                
                if mcp_value != 0:
                    # 计算相对差值百分比
                    diff_percent = ((dw_value - mcp_value) / mcp_value) * 100
                else:
                    diff_percent = 0
                    
                differences[app][metric] = {
                    'dw_value': dw_value,
                    'mcp_value': mcp_value,
                    'absolute_diff': dw_value - mcp_value,
                    'relative_diff_percent': diff_percent
                }
                
        return differences
    
    def create_comparison_charts(self, dw_metrics: Dict, mcp_metrics: Dict, 
                               differences: Dict, output_dir: str = "charts"):
        """
        创建对比图表
        
        Args:
            dw_metrics: DynamicWasm指标数据
            mcp_metrics: MCP指标数据
            differences: 差值计算结果
            output_dir: 输出目录
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 为每个指标创建对比图
        for metric_key, metric_name in self.metrics.items():
            self._create_metric_chart(metric_key, metric_name, dw_metrics, mcp_metrics, 
                                    differences, output_dir)
    
    def _create_metric_chart(self, metric_key: str, metric_name: str, 
                           dw_metrics: Dict, mcp_metrics: Dict, 
                           differences: Dict, output_dir: str):
        """为单个指标创建对比图"""
        apps = []
        dw_values = []
        mcp_values = []
        
        for app in self.apps:
            if app in dw_metrics and app in mcp_metrics:
                apps.append(app)
                dw_values.append(dw_metrics[app].get(metric_key, 0))
                mcp_values.append(mcp_metrics[app].get(metric_key, 0))
        
        if not apps:
            return
            
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(apps))
        width = 0.35
        
        # 绘制条形图
        bars1 = ax.bar(x - width/2, dw_values, width, label='DynamicWasm', 
                      color='#2E86AB', alpha=0.8)
        bars2 = ax.bar(x + width/2, mcp_values, width, label='MCP', 
                      color='#A23B72', alpha=0.8)
        
        # 添加数值标签
        self._add_value_labels(ax, bars1, dw_values, metric_key)
        self._add_value_labels(ax, bars2, mcp_values, metric_key)
        
        # 设置图表属性
        ax.set_xlabel('应用', fontsize=12)
        ax.set_ylabel(metric_name, fontsize=12)
        ax.set_title(f'{metric_name} 对比', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(apps)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join(output_dir, f'{metric_key}_comparison.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"已生成图表: {chart_path}")
    
    def _add_value_labels(self, ax, bars, values, metric_key):
        """在条形图上添加数值标签"""
        for bar, value in zip(bars, values):
            height = bar.get_height()
            
            # 根据指标类型格式化数值
            if metric_key == 'duration_mean':
                formatted_value = f'{value:.3f}s'
            elif metric_key in ['llm_traffic_mean', 'communication_traffic_mean', 
                               'api_traffic_mean', 'total_traffic_mean']:
                if value >= 1024*1024:
                    formatted_value = f'{value/1024/1024:.2f} MB'
                elif value >= 1024:
                    formatted_value = f'{value/1024:.2f} KB'
                else:
                    formatted_value = f'{value:.0f} B'
            else:
                formatted_value = f'{value:.2f}' if isinstance(value, float) else f'{value}'
            
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   formatted_value,
                   ha='center', va='bottom', fontsize=9)
    
    def print_differences(self, differences: Dict):
        """打印性能差值分析结果"""
        print("\n" + "="*80)
        print("性能对比分析结果")
        print("="*80)
        
        for app in self.apps:
            if app not in differences:
                continue
                
            print(f"\n【{app} 应用】")
            print("-" * 50)
            
            app_diffs = differences[app]
            for metric_key, metric_name in self.metrics.items():
                if metric_key not in app_diffs:
                    continue
                    
                diff_data = app_diffs[metric_key]
                dw_val = diff_data['dw_value']
                mcp_val = diff_data['mcp_value']
                abs_diff = diff_data['absolute_diff']
                rel_diff = diff_data['relative_diff_percent']
                
                print(f"{metric_name}:")
                print(f"  DynamicWasm: {dw_val:.4f}")
                print(f"  MCP:         {mcp_val:.4f}")
                print(f"  绝对差值:    {abs_diff:.4f}")
                print(f"  相对差值:    {rel_diff:+.2f}%")
                
                # 性能评价
                if metric_key == 'duration_mean':
                    # 执行时间越短越好
                    if rel_diff < 0:
                        print(f"  → DynamicWasm 比 MCP 快 {abs(rel_diff):.2f}%")
                    else:
                        print(f"  → DynamicWasm 比 MCP 慢 {rel_diff:.2f}%")
                elif metric_key in ['llm_traffic_mean', 'communication_traffic_mean', 
                                  'api_traffic_mean', 'total_traffic_mean']:
                    # 网络流量越少越好
                    if rel_diff < 0:
                        print(f"  → DynamicWasm 比 MCP 少 {abs(rel_diff):.2f}%")
                    else:
                        print(f"  → DynamicWasm 比 MCP 多 {rel_diff:.2f}%")
                
                print()
    
    def generate_summary_report(self, differences: Dict, output_file: str = "performance_summary.txt"):
        """生成性能对比摘要报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("DynamicWasm vs MCP 性能对比摘要报告\n")
            f.write("="*50 + "\n\n")
            
            for app in self.apps:
                if app not in differences:
                    continue
                    
                f.write(f"{app} 应用性能对比:\n")
                f.write("-" * 30 + "\n")
                
                app_diffs = differences[app]
                for metric_key, metric_name in self.metrics.items():
                    if metric_key not in app_diffs:
                        continue
                        
                    diff_data = app_diffs[metric_key]
                    rel_diff = diff_data['relative_diff_percent']
                    
                    f.write(f"{metric_name}: {rel_diff:+.2f}%\n")
                
                f.write("\n")
        
        print(f"已生成摘要报告: {output_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='性能分析工具 - 对比DynamicWasm和MCP测试结果')
    parser.add_argument('dw_path', help='DynamicWasm测试结果目录路径')
    parser.add_argument('mcp_path', help='MCP测试结果目录路径')
    parser.add_argument('--output', '-o', default='charts', help='图表输出目录 (默认: charts)')
    parser.add_argument('--report', '-r', default='performance_summary.txt', 
                       help='摘要报告文件名 (默认: performance_summary.txt)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式，打印详细的数据提取信息')
    
    args = parser.parse_args()
    
    # 检查输入目录是否存在
    if not os.path.exists(args.dw_path):
        print(f"错误: DynamicWasm结果目录不存在: {args.dw_path}")
        sys.exit(1)
        
    if not os.path.exists(args.mcp_path):
        print(f"错误: MCP结果目录不存在: {args.mcp_path}")
        sys.exit(1)
    
    # 创建分析器
    analyzer = PerformanceAnalyzer()
    
    print("正在加载测试结果...")
    dw_data, mcp_data = analyzer.load_test_results(args.dw_path, args.mcp_path)
    
    if not dw_data or not mcp_data:
        print("错误: 无法加载测试数据")
        sys.exit(1)
    
    # 调试模式
    if args.debug:
        print("调试模式: 打印数据提取信息...")
        analyzer.debug_data_extraction(dw_data, is_dw=True)
        analyzer.debug_data_extraction(mcp_data, is_dw=False)
    
    print("正在提取性能指标...")
    dw_metrics = analyzer.extract_metrics(dw_data, is_dw=True)
    mcp_metrics = analyzer.extract_metrics(mcp_data, is_dw=False)
    
    print("正在计算性能差值...")
    differences = analyzer.calculate_differences(dw_metrics, mcp_metrics)
    
    print("正在生成对比图表...")
    analyzer.create_comparison_charts(dw_metrics, mcp_metrics, differences, args.output)
    
    print("正在打印分析结果...")
    analyzer.print_differences(differences)
    
    print("正在生成摘要报告...")
    analyzer.generate_summary_report(differences, args.report)
    
    print(f"\n分析完成！")
    print(f"图表保存在: {args.output}/")
    print(f"摘要报告: {args.report}")

if __name__ == "__main__":
    main()