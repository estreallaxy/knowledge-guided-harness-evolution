#!/usr/bin/env python3
"""
写入模式Debug功能测试脚本
专门测试ToolPro系统在写入模式下的各种错误处理机制：
1. 编译错误处理 - 测试语法错误、类型错误等编译失败情况
2. 代码执行错误处理 - 测试WASM逻辑错误、运行时错误等
3. API调用错误处理 - 测试MCP工具调用错误、参数错误等

参考test_memos_simple.py的设计，使用/compile-and-execute API进行测试
"""

import asyncio
import json
import time
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import logging

# 设置控制台编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WriteModeDebugTester:
    """写入模式Debug功能测试器"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.test_results = {}
        self.client = httpx.AsyncClient(timeout=120.0)  # 增加超时时间，因为debug可能需要更长时间
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_separator(self, title: str = ""):
        """打印分隔线"""
        print("=" * 80)
        if title:
            print(f" {title} ")
            print("=" * 80)
    
    def print_result(self, test_name: str, result: Dict[str, Any]):
        """打印测试结果"""
        print(f"\n📋 {test_name} 测试结果:")
        print("-" * 50)
        
        # 检查ToolPro API的响应结构
        if "result" in result and isinstance(result["result"], dict):
            inner_result = result["result"]
            if inner_result.get("success"):
                print("✅ 测试成功")
                if "message" in inner_result:
                    print(f"💬 {inner_result['message']}")
                if "test_result" in inner_result:
                    print(f"🎯 测试结果: {inner_result['test_result']}")
                if "debug_info" in inner_result:
                    debug_info = inner_result["debug_info"]
                    print(f"🔧 调试信息:")
                    print(f"  - 调试阶段: {debug_info.get('debug_phase', 'unknown')}")
                    print(f"  - 调试尝试次数: {debug_info.get('attempts', 0)}")
                    print(f"  - 最大重试次数: {debug_info.get('max_retries', 0)}")
            else:
                print("❌ 测试失败")
                print(f"🚨 错误信息: {inner_result.get('error', '未知错误')}")
                if "debug_info" in inner_result:
                    debug_info = inner_result["debug_info"]
                    print(f"🔧 调试信息:")
                    print(f"  - 调试阶段: {debug_info.get('debug_phase', 'unknown')}")
                    print(f"  - 调试尝试次数: {debug_info.get('attempts', 0)}")
                    print(f"  - 最大重试次数: {debug_info.get('max_retries', 0)}")
        elif result.get("success"):
            print("✅ 测试成功")
            if "message" in result:
                print(f"💬 {result['message']}")
        else:
            print("❌ 测试失败")
            print(f"🚨 错误信息: {result.get('error', '未知错误')}")
            
        # 显示调试信息
        if "debug_info" in result:
            debug_info = result["debug_info"]
            print(f"🔧 调试信息:")
            print(f"  - 执行模式: {debug_info.get('execution_mode', 'unknown')}")
            print(f"  - 策略: {debug_info.get('strategy', 'unknown')}")
            if "debug_phase" in debug_info:
                print(f"  - 调试阶段: {debug_info['debug_phase']}")
        
        # 显示执行时间
        if "duration" in result:
            print(f"⏱️ 执行时间: {result['duration']:.2f}秒")
        
        self.test_results[test_name] = result
    
    async def check_server_connection(self) -> bool:
        """检查ToolPro服务器连接"""
        try:
            api_response = await self.client.get(f"{self.server_url}/api")
            if api_response.status_code == 200:
                print("✅ ToolPro服务器API端点正常")
                return True
            else:
                print(f"❌ ToolPro服务器API端点异常: {api_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ToolPro服务器连接失败: {e}")
            return False
    
    async def test_compilation_error_syntax(self) -> Dict[str, Any]:
        """测试编译错误 - 语法错误"""
        print("\n🔍 测试编译错误 - 语法错误...")
        
        # 故意包含语法错误的Rust代码
        rust_code = """
        // 测试编译错误 - 语法错误
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        // 故意制造语法错误：缺少分号
        let memos_result = call_mcp_tool("memos_get_memos", &serde_json::Value::Object(serde_json::Map::new()))
        
        // 另一个语法错误：不匹配的括号
        match memos_result {
            Ok(response) => {
                println!("Memos API调用成功");
                result.insert("success".to_string(), serde_json::Value::Bool(true));
                result.insert("test_result".to_string(), serde_json::Value::String("编译错误测试通过".to_string()));
            },
            Err(e) => {
                println!("Memos API调用失败: {}", e);
                result.insert("success".to_string(), serde_json::Value::Bool(false));
                result.insert("error".to_string(), serde_json::Value::String(format!("API调用失败: {}", e)));
            }
        // 缺少闭合括号
        """
        
        return await self._send_debug_test_request(
            "compilation_error_syntax",
            rust_code,
            "测试编译错误处理 - 语法错误",
            "memos_get_memos",
            "compilation_error"
        )
    
    async def test_compilation_error_type(self) -> Dict[str, Any]:
        """测试编译错误 - 类型错误"""
        print("\n🔍 测试编译错误 - 类型错误...")
        
        # 故意包含类型错误的Rust代码
        rust_code = """
        // 测试编译错误 - 类型错误
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        // 故意制造类型错误：错误的参数类型
        let wrong_params = "invalid_string_params";  // 应该是Value类型
        let memos_result = call_mcp_tool("memos_get_memos", wrong_params);
        
        // 另一个类型错误：错误的变量类型
        let wrong_type: i32 = "string_value";  // 类型不匹配
        
        match memos_result {
            Ok(response) => {
                println!("Memos API调用成功");
                result.insert("success".to_string(), serde_json::Value::Bool(true));
                result.insert("test_result".to_string(), serde_json::Value::String("编译错误测试通过".to_string()));
            },
            Err(e) => {
                println!("Memos API调用失败: {}", e);
                result.insert("success".to_string(), serde_json::Value::Bool(false));
                result.insert("error".to_string(), serde_json::Value::String(format!("API调用失败: {}", e)));
            }
        }
        """
        
        return await self._send_debug_test_request(
            "compilation_error_type",
            rust_code,
            "测试编译错误处理 - 类型错误",
            "memos_get_memos",
            "compilation_error"
        )
    
    async def test_execution_error_logic(self) -> Dict[str, Any]:
        """测试代码执行错误 - 逻辑错误"""
        print("\n🔍 测试代码执行错误 - 逻辑错误...")
        
        # 故意包含逻辑错误的Rust代码（语法正确但逻辑有问题）
        rust_code = """
        // 测试代码执行错误 - 逻辑错误
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        // 故意制造逻辑错误：无限循环（但设置合理的退出条件避免真正无限）
        let mut counter = 0;
        loop {
            counter += 1;
            if counter > 1000000 {  // 设置一个很大的数字来模拟长时间循环
                break;
            }
        }
        
        // 另一个逻辑错误：除零错误（但使用变量避免编译时检测）
        let divisor = 1;
        let result = 100 / (divisor - 1);  // 这会导致除零错误，但编译时不会检测到
        
        // 调用MCP工具
        let memos_result = call_mcp_tool("memos_get_memos", &serde_json::Value::Object(serde_json::Map::new()));
        
        match memos_result {
            Ok(response) => {
                println!("Memos API调用成功");
                result.insert("success".to_string(), serde_json::Value::Bool(true));
                result.insert("test_result".to_string(), serde_json::Value::String("执行错误测试通过".to_string()));
            },
            Err(e) => {
                println!("Memos API调用失败: {}", e);
                result.insert("success".to_string(), serde_json::Value::Bool(false));
                result.insert("error".to_string(), serde_json::Value::String(format!("API调用失败: {}", e)));
            }
        }
        """
        
        return await self._send_debug_test_request(
            "execution_error_logic",
            rust_code,
            "测试代码执行错误处理 - 逻辑错误",
            "memos_get_memos",
            "execution_error"
        )
    
    async def test_execution_error_memory(self) -> Dict[str, Any]:
        """测试代码执行错误 - 内存错误"""
        print("\n🔍 测试代码执行错误 - 内存错误...")
        
        # 故意包含内存错误的Rust代码（语法正确但逻辑有问题）
        rust_code = """
        // 测试代码执行错误 - 内存错误
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        // 故意制造内存错误：栈溢出（但使用合理的递归深度避免真正栈溢出）
        fn recursive_function(n: i32) -> i32 {
            if n <= 0 {
                return 0;
            }
            // 使用较小的递归深度避免真正的栈溢出，但仍然会消耗大量时间
            return recursive_function(n - 1) + recursive_function(n - 1);
        }
        
        let result = recursive_function(20);  // 使用较小的深度，但仍然会消耗大量时间
        
        // 调用MCP工具
        let memos_result = call_mcp_tool("memos_get_memos", &serde_json::Value::Object(serde_json::Map::new()));
        
        match memos_result {
            Ok(response) => {
                println!("Memos API调用成功");
                result.insert("success".to_string(), serde_json::Value::Bool(true));
                result.insert("test_result".to_string(), serde_json::Value::String("执行错误测试通过".to_string()));
            },
            Err(e) => {
                println!("Memos API调用失败: {}", e);
                result.insert("success".to_string(), serde_json::Value::Bool(false));
                result.insert("error".to_string(), serde_json::Value::String(format!("API调用失败: {}", e)));
            }
        }
        """
        
        return await self._send_debug_test_request(
            "execution_error_memory",
            rust_code,
            "测试代码执行错误处理 - 内存错误",
            "memos_get_memos",
            "execution_error"
        )
    
    async def test_api_call_error_wrong_tool(self) -> Dict[str, Any]:
        """测试API调用错误 - 错误的工具名称"""
        print("\n🔍 测试API调用错误 - 错误的工具名称...")
        
        # 调用不存在的MCP工具
        rust_code = """
        // 测试API调用错误 - 错误的工具名称
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        // 故意调用不存在的MCP工具
        let error_result = call_mcp_tool("memos_nonexistent_tool", &serde_json::Value::Object(serde_json::Map::new()));
        
        match error_result {
            Ok(response) => {
                // 检查MCP工具的实际返回格式
                if let Some(success) = response.get("success") {
                    if success.as_bool() == Some(true) {
                        // 如果意外成功了，记录这个情况
                        println!("意外成功调用了错误的工具");
                        result.insert("success".to_string(), serde_json::Value::Bool(false));
                        result.insert("error".to_string(), serde_json::Value::String("意外成功调用了错误的工具".to_string()));
                    } else {
                        // 预期的错误情况 - MCP工具返回了失败状态
                        if let Some(error_msg) = response.get("error") {
                            println!("预期的错误: {}", error_msg);
                            result.insert("success".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_message".to_string(), serde_json::Value::String(format!("正确处理了错误: {}", error_msg)));
                            result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                        } else {
                            result.insert("success".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_message".to_string(), serde_json::Value::String("MCP工具正确返回了失败状态".to_string()));
                            result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                        }
                    }
                } else {
                    // 响应格式错误，但这也是预期的错误情况
                    println!("MCP工具响应格式错误，这是预期的错误情况");
                    result.insert("success".to_string(), serde_json::Value::Bool(true));
                    result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                    result.insert("error_message".to_string(), serde_json::Value::String("MCP工具响应格式错误，错误处理正常".to_string()));
                    result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                }
            },
            Err(e) => {
                // 预期的错误情况 - MCP工具调用异常
                println!("预期的错误: {}", e);
                result.insert("success".to_string(), serde_json::Value::Bool(true));
                result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                result.insert("error_message".to_string(), serde_json::Value::String(format!("正确处理了异常: {}", e)));
                result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
            }
        }
        """
        
        return await self._send_debug_test_request(
            "api_call_error_wrong_tool",
            rust_code,
            "测试API调用错误处理 - 错误的工具名称",
            "memos_nonexistent_tool",
            "api_call_error"
        )
    
    async def test_api_call_error_wrong_params(self) -> Dict[str, Any]:
        """测试API调用错误 - 错误的参数"""
        print("\n🔍 测试API调用错误 - 错误的参数...")
        
        # 调用正确的工具但使用错误的参数
        rust_code = """
        // 测试API调用错误 - 错误的参数
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        // 故意使用错误的参数调用正确的工具
        let mut wrong_params = serde_json::Map::new();
        wrong_params.insert("invalid_param".to_string(), serde_json::Value::String("invalid_value".to_string()));
        wrong_params.insert("another_wrong_param".to_string(), serde_json::Value::Number(serde_json::Number::from(999)));
        
        let error_result = call_mcp_tool("memos_get_memos", &serde_json::Value::Object(wrong_params));
        
        match error_result {
            Ok(response) => {
                // 检查MCP工具的实际返回格式
                if let Some(success) = response.get("success") {
                    if success.as_bool() == Some(true) {
                        // 如果意外成功了，记录这个情况
                        println!("意外成功调用了错误的参数");
                        result.insert("success".to_string(), serde_json::Value::Bool(false));
                        result.insert("error".to_string(), serde_json::Value::String("意外成功调用了错误的参数".to_string()));
                    } else {
                        // 预期的错误情况 - MCP工具返回了失败状态
                        if let Some(error_msg) = response.get("error") {
                            println!("预期的错误: {}", error_msg);
                            result.insert("success".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_message".to_string(), serde_json::Value::String(format!("正确处理了错误: {}", error_msg)));
                            result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                        } else {
                            result.insert("success".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_message".to_string(), serde_json::Value::String("MCP工具正确返回了失败状态".to_string()));
                            result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                        }
                    }
                } else {
                    // 响应格式错误，但这也是预期的错误情况
                    println!("MCP工具响应格式错误，这是预期的错误情况");
                    result.insert("success".to_string(), serde_json::Value::Bool(true));
                    result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                    result.insert("error_message".to_string(), serde_json::Value::String("MCP工具响应格式错误，错误处理正常".to_string()));
                    result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                }
            },
            Err(e) => {
                // 预期的错误情况 - MCP工具调用异常
                println!("预期的错误: {}", e);
                result.insert("success".to_string(), serde_json::Value::Bool(true));
                result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                result.insert("error_message".to_string(), serde_json::Value::String(format!("正确处理了异常: {}", e)));
                result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
            }
        }
        """
        
        return await self._send_debug_test_request(
            "api_call_error_wrong_params",
            rust_code,
            "测试API调用错误处理 - 错误的参数",
            "memos_get_memos",
            "api_call_error"
        )
    
    async def test_api_call_error_network(self) -> Dict[str, Any]:
        """测试API调用错误 - 网络错误"""
        print("\n🔍 测试API调用错误 - 网络错误...")
        
        # 调用一个可能网络超时的工具
        rust_code = """
        // 测试API调用错误 - 网络错误
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        // 调用一个可能网络超时的工具（假设这个工具会超时）
        let timeout_result = call_mcp_tool("memos_get_memos", &serde_json::Value::Object(serde_json::Map::new()));
        
        match timeout_result {
            Ok(response) => {
                // 检查MCP工具的实际返回格式
                if let Some(success) = response.get("success") {
                    if success.as_bool() == Some(true) {
                        // 如果意外成功了，记录这个情况
                        println!("意外成功调用了可能超时的工具");
                        result.insert("success".to_string(), serde_json::Value::Bool(false));
                        result.insert("error".to_string(), serde_json::Value::String("意外成功调用了可能超时的工具".to_string()));
                    } else {
                        // 预期的错误情况 - MCP工具返回了失败状态
                        if let Some(error_msg) = response.get("error") {
                            println!("预期的错误: {}", error_msg);
                            result.insert("success".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_message".to_string(), serde_json::Value::String(format!("正确处理了错误: {}", error_msg)));
                            result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                        } else {
                            result.insert("success".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                            result.insert("error_message".to_string(), serde_json::Value::String("MCP工具正确返回了失败状态".to_string()));
                            result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                        }
                    }
                } else {
                    // 响应格式错误，但这也是预期的错误情况
                    println!("MCP工具响应格式错误，这是预期的错误情况");
                    result.insert("success".to_string(), serde_json::Value::Bool(true));
                    result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                    result.insert("error_message".to_string(), serde_json::Value::String("MCP工具响应格式错误，错误处理正常".to_string()));
                    result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
                }
            },
            Err(e) => {
                // 预期的错误情况 - MCP工具调用异常
                println!("预期的错误: {}", e);
                result.insert("success".to_string(), serde_json::Value::Bool(true));
                result.insert("error_handled".to_string(), serde_json::Value::Bool(true));
                result.insert("error_message".to_string(), serde_json::Value::String(format!("正确处理了异常: {}", e)));
                result.insert("test_result".to_string(), serde_json::Value::String("API调用错误处理测试通过".to_string()));
            }
        }
        """
        
        return await self._send_debug_test_request(
            "api_call_error_network",
            rust_code,
            "测试API调用错误处理 - 网络错误",
            "memos_get_memos",
            "api_call_error"
        )
    
    async def _send_debug_test_request(self, test_name: str, rust_code: str, description: str, 
                                     api_endpoint: str, operation_type: str) -> Dict[str, Any]:
        """发送debug测试请求的通用方法"""
        try:
            start_time = time.time()
            
            print(f"📤 发送请求到: {self.server_url}/compile-and-execute")
            print(f"📝 Rust代码: {description}")
            print(f"🎯 测试类型: {operation_type}")
            
            response = await self.client.post(
                f"{self.server_url}/compile-and-execute",
                json={
                    "source_code": rust_code,
                    "semantic_info": {
                        "description": description,
                        "api_endpoint": api_endpoint,
                        "operation_type": operation_type,
                        "expected_result": "测试debug功能是否正确处理错误"
                    },
                    "input_data": json.dumps({
                        "test_type": f"write_mode_{operation_type}",
                        "timestamp": datetime.now().isoformat()
                    }),
                    "api_spec_url": None,
                    "user_query": f"测试写入模式下的{operation_type}处理",
                    "force_read_mode": False,  # 不强制读取模式
                }
            )
            
            duration = time.time() - start_time
            
            print(f"📥 收到响应，状态码: {response.status_code}")
            print(f"⏱️ 请求耗时: {duration:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                result["duration"] = duration
                print(f"✅ API调用成功")
                print(f"📄 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                error_result = {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "duration": duration
                }
                print(f"❌ API调用失败")
                print(f"📄 错误响应: {response.text}")
                return error_result
                
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "duration": 0
            }
            print(f"❌ 请求异常: {e}")
            return error_result
    
    def print_summary(self):
        """打印测试总结"""
        self.print_separator("写入模式Debug功能测试总结")
        
        total_tests = len(self.test_results)
        successful_tests = 0
        failed_tests = 0
        
        # 统计各种错误类型的测试结果
        compilation_tests = 0
        execution_tests = 0
        api_call_tests = 0
        
        compilation_success = 0
        execution_success = 0
        api_call_success = 0
        
        # 正确统计测试结果
        for test_name, result in self.test_results.items():
            # 检查ToolPro API的响应结构
            if "result" in result and isinstance(result["result"], dict):
                inner_result = result["result"]
                if inner_result.get("success"):
                    successful_tests += 1
                else:
                    failed_tests += 1
                
                # 分类统计
                if "compilation_error" in test_name:
                    compilation_tests += 1
                    if inner_result.get("success"):
                        compilation_success += 1
                elif "execution_error" in test_name:
                    execution_tests += 1
                    if inner_result.get("success"):
                        execution_success += 1
                elif "api_call_error" in test_name:
                    api_call_tests += 1
                    if inner_result.get("success"):
                        api_call_success += 1
            elif result.get("success"):
                successful_tests += 1
            else:
                failed_tests += 1
        
        print(f"📊 总体测试统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  成功: {successful_tests}")
        print(f"  失败: {failed_tests}")
        print(f"  成功率: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "  成功率: 0%")
        
        # 分类统计
        print(f"\n📊 分类测试统计:")
        if compilation_tests > 0:
            print(f"  编译错误测试: {compilation_success}/{compilation_tests} ({(compilation_success/compilation_tests*100):.1f}%)")
        if execution_tests > 0:
            print(f"  执行错误测试: {execution_success}/{execution_tests} ({(execution_success/execution_tests*100):.1f}%)")
        if api_call_tests > 0:
            print(f"  API调用错误测试: {api_call_success}/{api_call_tests} ({(api_call_success/api_call_tests*100):.1f}%)")
        
        # 显示各测试的持续时间
        if total_tests > 0:
            print(f"\n⏱️ 测试持续时间:")
            for test_name, result in self.test_results.items():
                duration = result.get("duration", 0)
                print(f"  - {test_name}: {duration:.2f}秒")
        
        # 分析debug功能是否正常工作
        print(f"\n🔧 Debug功能分析:")
        debug_enabled_tests = 0
        debug_phases = set()
        
        for test_name, result in self.test_results.items():
            if "result" in result and isinstance(result["result"], dict):
                inner_result = result["result"]
                if "debug_info" in inner_result:
                    debug_enabled_tests += 1
                    debug_info = inner_result["debug_info"]
                    debug_phase = debug_info.get('debug_phase', 'unknown')
                    debug_phases.add(debug_phase)
                    print(f"  - {test_name}: 调试信息可用")
                    print(f"    调试阶段: {debug_phase}")
                    print(f"    调试尝试次数: {debug_info.get('attempts', 0)}")
                    print(f"    最大重试次数: {debug_info.get('max_retries', 0)}")
        
        if debug_enabled_tests > 0:
            print(f"  ✅ Debug功能正常工作 ({debug_enabled_tests}/{total_tests} 个测试)")
            print(f"  📋 检测到的调试阶段: {', '.join(debug_phases)}")
        else:
            print(f"  ⚠️ Debug功能可能未正常工作")
        
        # 显示失败的测试详情
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for test_name, result in self.test_results.items():
                if "result" in result and isinstance(result["result"], dict):
                    inner_result = result["result"]
                    if not inner_result.get("success"):
                        print(f"  - {test_name}: {inner_result.get('error', '未知错误')}")
                elif not result.get("success"):
                    print(f"  - {test_name}: {result.get('error', '未知错误')}")
    
    async def run_all_tests(self):
        """运行所有debug测试"""
        self.print_separator("写入模式Debug功能测试")
        
        # 检查服务器连接
        if not await self.check_server_connection():
            print("❌ 无法连接到ToolPro服务器，请确保服务器正在运行")
            return
        
        print("\n🚀 开始运行写入模式Debug测试...")
        print("📋 测试说明：")
        print("  - 直接使用 /compile-and-execute API 进行测试")
        print("  - 使用预编写的Rust代码触发各种错误")
        print("  - 测试写入模式下的debug功能是否正确实现")
        print("  - 包括编译错误、执行错误、API调用错误三种类型")
        
        # 运行各种debug测试
        print("\n🔧 开始编译错误测试...")
        await self.test_compilation_error_syntax()
        await self.test_compilation_error_type()
        
        print("\n🔧 开始执行错误测试...")
        await self.test_execution_error_logic()
        await self.test_execution_error_memory()
        
        print("\n🔧 开始API调用错误测试...")
        await self.test_api_call_error_wrong_tool()
        await self.test_api_call_error_wrong_params()
        await self.test_api_call_error_network()
        
        # 打印总结
        self.print_summary()
    
    async def run_specific_test(self, test_type: str):
        """运行特定类型的debug测试"""
        self.print_separator(f"写入模式Debug功能测试 - {test_type}")
        
        # 检查服务器连接
        if not await self.check_server_connection():
            print("❌ 无法连接到ToolPro服务器，请确保服务器正在运行")
            return
        
        print(f"\n🚀 开始运行 {test_type} 测试...")
        print("📋 测试说明：")
        print("  - 直接使用 /compile-and-execute API 进行测试")
        print("  - 使用预编写的Rust代码触发特定错误")
        print("  - 测试写入模式下的debug功能是否正确实现")
        
        if test_type == "compilation_error":
            await self.test_compilation_error_syntax()
            await self.test_compilation_error_type()
        elif test_type == "execution_error":
            await self.test_execution_error_logic()
            await self.test_execution_error_memory()
        elif test_type == "api_call_error":
            await self.test_api_call_error_wrong_tool()
            await self.test_api_call_error_wrong_params()
            await self.test_api_call_error_network()
        elif test_type == "syntax_error":
            await self.test_compilation_error_syntax()
        elif test_type == "type_error":
            await self.test_compilation_error_type()
        elif test_type == "logic_error":
            await self.test_execution_error_logic()
        elif test_type == "memory_error":
            await self.test_execution_error_memory()
        elif test_type == "wrong_tool":
            await self.test_api_call_error_wrong_tool()
        elif test_type == "wrong_params":
            await self.test_api_call_error_wrong_params()
        elif test_type == "network_error":
            await self.test_api_call_error_network()
        else:
            print(f"❌ 未知的测试类型: {test_type}")
            return
        
        # 打印总结
        self.print_summary()


def interactive_test_selection():
    """交互式测试选择"""
    print("\n" + "="*80)
    print("  ToolPro 写入模式Debug功能测试工具 ")
    print("="*80)
    print("\n请选择要测试的错误类型：")
    print()
    
    test_options = [
        ("1", "all", "所有测试", "运行所有类型的错误测试"),
        ("2", "compilation_error", "编译错误测试", "测试语法错误和类型错误"),
        ("3", "execution_error", "执行错误测试", "测试逻辑错误和内存错误"),
        ("4", "api_call_error", "API调用错误测试", "测试工具名称、参数和网络错误"),
        ("5", "syntax_error", "语法错误测试", "测试Rust语法错误"),
        ("6", "type_error", "类型错误测试", "测试Rust类型错误"),
        ("7", "logic_error", "逻辑错误测试", "测试除零等逻辑错误"),
        ("8", "memory_error", "内存错误测试", "测试栈溢出等内存错误"),
        ("9", "wrong_tool", "错误工具测试", "测试调用不存在的MCP工具"),
        ("10", "wrong_params", "错误参数测试", "测试MCP工具参数错误"),
        ("11", "network_error", "网络错误测试", "测试网络超时等错误"),
        ("0", "exit", "退出", "退出测试程序")
    ]
    
    for option, test_type, name, description in test_options:
        print(f"  {option:2}. {name:20} - {description}")
    
    print()
    
    while True:
        try:
            choice = input("请输入选择 (0-11): ").strip()
            
            if choice == "0":
                print("退出测试程序")
                return None
            elif choice in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]:
                selected_option = next(opt for opt in test_options if opt[0] == choice)
                test_type = selected_option[1]
                print(f"\n已选择: {selected_option[2]} - {selected_option[3]}")
                return test_type
            else:
                print("❌ 无效选择，请输入 0-11 之间的数字")
        except KeyboardInterrupt:
            print("\n\n用户取消操作")
            return None
        except Exception as e:
            print(f"❌ 输入错误: {e}")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="写入模式Debug功能测试工具")
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="ToolPro服务器地址 (默认: http://localhost:8000)"
    )
    parser.add_argument(
        "--test",
        choices=[
            "all", "compilation_error", "execution_error", "api_call_error",
            "syntax_error", "type_error", "logic_error", "memory_error",
            "wrong_tool", "wrong_params", "network_error", "interactive"
        ],
        default="interactive",
        help="测试类型: all=所有测试, compilation_error=编译错误, execution_error=执行错误, api_call_error=API调用错误, 或具体错误类型, interactive=交互式选择"
    )
    
    args = parser.parse_args()
    
    # 确定要运行的测试类型
    if args.test == "interactive":
        test_type = interactive_test_selection()
        if test_type is None:
            return
    else:
        test_type = args.test
    
    async with WriteModeDebugTester(args.server) as tester:
        if test_type == "all":
            await tester.run_all_tests()
        else:
            await tester.run_specific_test(test_type)


if __name__ == "__main__":
    asyncio.run(main())
