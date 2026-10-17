"""
Debug配置管理
控制DW系统中的debug输出，减少网络流量
"""

import os
from typing import Dict, Any

class DebugConfig:
    """Debug配置管理器"""
    
    def __init__(self):
        # 使用默认配置，不再依赖环境变量
        self.enable_debug = False  # 默认关闭debug
        self.enable_verbose_logging = False  # 默认关闭详细日志
        self.enable_debug_in_response = False  # 默认不在响应中包含debug信息
        
        # 网络流量优化配置
        self.minimize_network_data = True  # 默认最小化网络数据
        self.include_debug_info = False  # 默认不包含debug信息
        
    def should_log_debug(self) -> bool:
        """是否应该记录debug日志"""
        return self.enable_debug or self.enable_verbose_logging
    
    def should_include_debug_in_response(self) -> bool:
        """是否应该在响应中包含debug信息"""
        return self.enable_debug_in_response and not self.minimize_network_data
    
    def should_minimize_network_data(self) -> bool:
        """是否应该最小化网络数据"""
        return self.minimize_network_data
    
    def get_debug_level(self) -> str:
        """获取debug级别"""
        if self.enable_verbose_logging:
            return 'verbose'
        elif self.enable_debug:
            return 'debug'
        else:
            return 'production'
    
    def filter_response_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤响应数据，移除不必要的debug信息"""
        if not self.should_minimize_network_data():
            return data
        
        # 创建过滤后的数据副本
        filtered_data = {}
        
        # 保留核心字段
        core_fields = [
            'success', 'error', 'data', 'result', 'execution_mode', 
            'strategy', 'network_operations', 'execution_stats', 'api_traffic_stats',
            'wasm_compile_stats', 'wasm_api_stats',
            'projection_rejected', 'projection_errors', 'projection_diagnostics',
        ]
        
        for field in core_fields:
            if field in data:
                filtered_data[field] = data[field]
        
        # 如果启用debug信息，则包含debug字段
        if self.should_include_debug_in_response():
            debug_fields = [
                'debug_input', 'debug_before_user_code', 'debug_after_user_code',
                'debug_parsed', 'debug_user_code_executed', 'debug_info'
            ]
            for field in debug_fields:
                if field in data:
                    filtered_data[field] = data[field]
        
        return filtered_data
    
    def get_optimized_result_template(self) -> str:
        """获取优化的结果模板（不包含debug信息）"""
        if self.should_minimize_network_data():
            return """
    // 用户代码
    {user_code}
    
    // 确保result包含必要的字段
    if !result.contains_key("done") {{
        result.insert("done".to_string(), serde_json::Value::Bool(true));
    }}
    if !result.contains_key("success") {{
        result.insert("success".to_string(), serde_json::Value::Bool(true));
    }}
    
    Ok(result)
"""
        else:
            return """
    // 用户代码
    result.insert("debug_before_user_code".to_string(), serde_json::Value::String("Before user code".to_string()));
    
    {user_code}
    
    // 添加调试信息
    result.insert("debug_user_code_executed".to_string(), serde_json::Value::Bool(true));
    result.insert("debug_after_user_code".to_string(), serde_json::Value::String("After user code".to_string()));
    
    // 确保result包含必要的字段
    if !result.contains_key("done") {{
        result.insert("done".to_string(), serde_json::Value::Bool(true));
    }}
    if !result.contains_key("success") {{
        result.insert("success".to_string(), serde_json::Value::Bool(true));
    }}
    
    Ok(result)
"""

# 全局debug配置实例
debug_config = DebugConfig()
