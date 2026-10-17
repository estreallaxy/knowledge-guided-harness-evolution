# 向后兼容的导入文件
# 为了保持现有代码的兼容性，重新导出所有函数

from .data_io import get_instruction, load_data_items, prepare_result_filenames, load_existing_results
from .result_parser import (
    parse_llm_output, 
    parse_from_response,
    parse_from_response_sewsm, 
    parse_from_response_opencua,
    parse_action_reward, 
    parse_action_reward_by_task_type
)
from .metrics_calculator import (
    compute_binary_classification_metrics,
    analyze_group_performance,
    update_group_stats,
    compute_metrics,
    compute_step_num_metrics,
    collect_statistics,
    compute_and_save_metrics
)

# 保持向后兼容性
__all__ = [
    # 数据I/O
    'get_instruction',
    'load_data_items',
    'prepare_result_filenames',
    'load_existing_results',
    
    # 结果解析
    'parse_llm_output',
    'parse_from_response',
    'parse_from_response_sewsm',
    'parse_from_response_opencua',
    'parse_action_reward',
    'parse_action_reward_by_task_type',
    
    # 指标计算
    'compute_binary_classification_metrics',
    'analyze_group_performance',
    'update_group_stats',
    'compute_metrics',
    'compute_step_num_metrics',
    'collect_statistics',
    'compute_and_save_metrics'
]
