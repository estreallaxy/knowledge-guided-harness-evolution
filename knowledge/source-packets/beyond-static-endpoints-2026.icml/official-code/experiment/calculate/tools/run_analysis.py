#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能分析工具使用示例
快速运行性能对比分析
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from performance_analyzer import PerformanceAnalyzer

def main():
    """主函数 - 使用示例"""
    print("DynamicWasm vs MCP 性能分析工具")
    print("="*50)
    
    # 获取当前脚本所在目录的父目录
    script_dir = Path(__file__).parent
    results_dir = script_dir.parent / "results"
    
    # 默认路径 - 使用9_24的测试结果
    dw_path = results_dir / "9_24_dw"
    mcp_path = results_dir / "9_24_mcp"
    
    print(f"DynamicWasm结果目录: {dw_path}")
    print(f"MCP结果目录: {mcp_path}")
    
    # 检查目录是否存在
    if not dw_path.exists():
        print(f"错误: DynamicWasm结果目录不存在: {dw_path}")
        print("请确保测试结果文件存在于正确的位置")
        return
    
    if not mcp_path.exists():
        print(f"错误: MCP结果目录不存在: {mcp_path}")
        print("请确保测试结果文件存在于正确的位置")
        return
    
    # 创建分析器
    analyzer = PerformanceAnalyzer()
    
    print("\n正在加载测试结果...")
    dw_data, mcp_data = analyzer.load_test_results(str(dw_path), str(mcp_path))
    
    if not dw_data or not mcp_data:
        print("错误: 无法加载测试数据")
        return
    
    print("正在调试数据提取...")
    analyzer.debug_data_extraction(dw_data)
    analyzer.debug_data_extraction(mcp_data)
    
    print("正在提取性能指标...")
    dw_metrics = analyzer.extract_metrics(dw_data)
    mcp_metrics = analyzer.extract_metrics(mcp_data)
    
    print("正在计算性能差值...")
    differences = analyzer.calculate_differences(dw_metrics, mcp_metrics)
    
    # 创建输出目录
    output_dir = script_dir / "analysis_output"
    output_dir.mkdir(exist_ok=True)
    
    print("正在生成对比图表...")
    analyzer.create_comparison_charts(dw_metrics, mcp_metrics, differences, str(output_dir))
    
    print("正在打印分析结果...")
    analyzer.print_differences(differences)
    
    print("正在生成摘要报告...")
    report_file = output_dir / "performance_summary.txt"
    analyzer.generate_summary_report(differences, str(report_file))
    
    print(f"\n分析完成！")
    print(f"图表保存在: {output_dir}/")
    print(f"摘要报告: {report_file}")

if __name__ == "__main__":
    main()
