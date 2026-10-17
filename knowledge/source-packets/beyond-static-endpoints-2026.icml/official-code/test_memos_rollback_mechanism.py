#!/usr/bin/env python3
"""
测试Memos回退机制和历史队列功能
分别修改7Z9HPRwM45PKbxNE4YAm8D、ctFuDaBvYvAn3KzvZLMAwy这两条备忘录的可见性
错误设置在第一个备忘录可见性更改之后，第二个更改之前
以此来测试当前项目中设计的回退机制和历史队列是否可用

注意事项：
1. 错误要求是能够通过编译的代码层次的执行错误，不要在编译阶段就进入debug
2. 注意添加写入标记，可参考test_write_mode_debug.py
3. 在Rust代码中通过MCP工具调用memos功能
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

class MemosRollbackTester:
    """Memos回退机制测试器"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.test_results = {}
        self.client = httpx.AsyncClient(timeout=120.0)  # 增加超时时间，因为可能需要回退操作
        
        # 测试的备忘录ID
        self.memo_ids = ["7Z9HPRwM45PKbxNE4YAm8D", "ctFuDaBvYvAn3KzvZLMAwy"]
        
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
                if "rollback_info" in inner_result:
                    rollback_info = inner_result["rollback_info"]
                    print(f"🔄 回退信息:")
                    print(f"  - 回退操作数: {rollback_info.get('rollback_count', 0)}")
                    print(f"  - 回退成功数: {rollback_info.get('rollback_success_count', 0)}")
                    print(f"  - 回退失败数: {rollback_info.get('rollback_failure_count', 0)}")
                    if "rollback_details" in rollback_info:
                        print(f"  - 回退详情: {rollback_info['rollback_details']}")
                if "history_info" in inner_result:
                    history_info = inner_result["history_info"]
                    print(f"📚 历史队列信息:")
                    print(f"  - 历史记录数: {history_info.get('history_count', 0)}")
                    print(f"  - 历史详情: {history_info.get('history_details', [])}")
            else:
                print("❌ 测试失败")
                print(f"🚨 错误信息: {inner_result.get('error', '未知错误')}")
                if "rollback_info" in inner_result:
                    rollback_info = inner_result["rollback_info"]
                    print(f"🔄 回退信息:")
                    print(f"  - 回退操作数: {rollback_info.get('rollback_count', 0)}")
                    print(f"  - 回退成功数: {rollback_info.get('rollback_success_count', 0)}")
                    print(f"  - 回退失败数: {rollback_info.get('rollback_failure_count', 0)}")
        elif result.get("success"):
            print("✅ 测试成功")
            if "message" in result:
                print(f"💬 {result['message']}")
        else:
            print("❌ 测试失败")
            print(f"🚨 错误信息: {result.get('error', '未知错误')}")
            
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
    
    async def test_rollback_mechanism(self) -> Dict[str, Any]:
        """测试回退机制 - 在第一个备忘录修改成功后，第二个修改前引入执行错误"""
        print("\n🔍 测试回退机制...")
        
        # 构造Rust代码，包含两个备忘录的可见性修改，在第二个修改前引入执行错误
        rust_code = f"""
        // 测试Memos回退机制和历史队列功能
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        let mut result = HashMap::new();
        let mut success_count = 0;
        let mut failure_count = 0;
        let mut rollback_count = 0;
        let mut rollback_success_count = 0;
        let mut rollback_failure_count = 0;
        
        println!("开始测试Memos回退机制和历史队列功能");
        
        // 修改第一个备忘录的可见性
        let first_memo_id = "{self.memo_ids[0]}";
        println!("正在修改第一个备忘录: {{}}", first_memo_id);
        
         let first_update_result = call_mcp_tool("memos_update_visibility", &serde_json::json!({{
             "memo_name": first_memo_id,
             "visibility": "PUBLIC"
         }}));
        
        match first_update_result {{
            Ok(response) => {{
                println!("第一个备忘录修改成功: {{}}", first_memo_id);
                success_count += 1;
                
                // 检查MCP工具的实际返回格式
                if let Some(success) = response.get("success") {{
                    if success.as_bool() == Some(true) {{
                        println!("第一个备忘录可见性已成功更改为PUBLIC");
                    }} else {{
                        println!("第一个备忘录修改可能失败");
                        failure_count += 1;
                    }}
                }} else {{
                    println!("第一个备忘录修改响应格式异常");
                    failure_count += 1;
                }}
            }},
            Err(e) => {{
                println!("第一个备忘录修改失败: {{}}", e);
                failure_count += 1;
            }}
        }}
         
         // 制造运行时错误（使用运行时才能确定的值避免编译期检测,该错误需要被修复,这一段需要被完全删除）
         let mut error_triggered = false;
         let mut counter = 0;
         
         // 使用循环制造运行时错误
         for i in 0..1000 {{
             counter += 1;
             if counter == 500 {{
                 // 在循环中间制造数组越界错误（运行时才能确定）
                 let test_array = vec![1, 2, 3];
                 let error_index = counter + 10;  // 使用运行时变量避免编译期检测
                 let _error_value = test_array[error_index];  // 这会导致panic，但编译时不会检测到
                 error_triggered = true;
                 break;
             }}
         }}
         
         if error_triggered {{
             println!("执行错误已触发，程序应该崩溃");
         }}
         
        
        // 修改第二个备忘录的可见性
        let second_memo_id = "{self.memo_ids[1]}";
        println!("正在修改第二个备忘录: {{}}", second_memo_id);
        
         let second_update_result = call_mcp_tool("memos_update_visibility", &serde_json::json!({{
             "memo_name": second_memo_id,
             "visibility": "PUBLIC"
         }}));
        
        match second_update_result {{
            Ok(response) => {{
                println!("第二个备忘录修改成功: {{}}", second_memo_id);
                success_count += 1;
            }},
            Err(e) => {{
                println!("第二个备忘录修改失败: {{}}", e);
                failure_count += 1;
            }}
        }}
        
        // 记录测试结果
        result.insert("success".to_string(), serde_json::Value::Bool(success_count > 0));
        result.insert("test_result".to_string(), serde_json::Value::String("回退机制测试".to_string()));
        result.insert("success_count".to_string(), serde_json::Value::Number(serde_json::Number::from(success_count)));
        result.insert("failure_count".to_string(), serde_json::Value::Number(serde_json::Number::from(failure_count)));
        result.insert("rollback_count".to_string(), serde_json::Value::Number(serde_json::Number::from(rollback_count)));
        result.insert("rollback_success_count".to_string(), serde_json::Value::Number(serde_json::Number::from(rollback_success_count)));
        result.insert("rollback_failure_count".to_string(), serde_json::Value::Number(serde_json::Number::from(rollback_failure_count)));
        
        println!("测试完成，成功: {{}}, 失败: {{}}, 回退: {{}}", success_count, failure_count, rollback_count);
        """
        
        return await self._send_rollback_test_request(
            "rollback_mechanism",
            rust_code,
            "测试回退机制和历史队列功能",
             "memos_update_visibility",
            "rollback_test"
        )
    
    async def test_history_queue_mechanism(self) -> Dict[str, Any]:
        """测试历史队列机制 - 模拟多个操作的历史记录"""
        print("\n🔍 测试历史队列机制...")
        
        # 构造Rust代码，包含多个操作和错误处理
        rust_code = f"""
        // 测试历史队列机制
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        let mut result = HashMap::new();
        let mut operation_count = 0;
        let mut success_count = 0;
        let mut failure_count = 0;
        let mut history_operations = Vec::new();
        
        println!("开始测试历史队列机制");
        
        // 操作1：获取所有备忘录
        operation_count += 1;
        println!("操作{{}}: 获取所有备忘录", operation_count);
        
        let get_memos_result = call_mcp_tool("memos_get_memos", &serde_json::Value::Object(serde_json::Map::new()));
        
        match get_memos_result {{
            Ok(response) => {{
                println!("获取备忘录成功");
                success_count += 1;
                history_operations.push(format!("操作{{}}: 获取备忘录 - 成功", operation_count));
            }},
            Err(e) => {{
                println!("获取备忘录失败: {{}}", e);
                failure_count += 1;
                history_operations.push(format!("操作{{}}: 获取备忘录 - 失败: {{}}", operation_count, e));
            }}
        }}
        
        // 操作2：修改第一个备忘录
        operation_count += 1;
        println!("操作{{}}: 修改第一个备忘录", operation_count);
        
         let first_update_result = call_mcp_tool("memos_update_visibility", &serde_json::json!({{
             "memo_name": "{self.memo_ids[0]}",
             "visibility": "PUBLIC"
         }}));
        
        match first_update_result {{
            Ok(response) => {{
                println!("第一个备忘录修改成功");
                success_count += 1;
                history_operations.push(format!("操作{{}}: 修改第一个备忘录 - 成功", operation_count));
            }},
            Err(e) => {{
                println!("第一个备忘录修改失败: {{}}", e);
                failure_count += 1;
                history_operations.push(format!("操作{{}}: 修改第一个备忘录 - 失败: {{}}", operation_count, e));
            }}
        }}
        
         // 操作3：故意引入执行错误
         operation_count += 1;
         println!("操作{{}}: 故意引入执行错误", operation_count);
         
         // 制造运行时错误（使用运行时才能确定的值避免编译期检测）
         let mut error_triggered = false;
         let mut counter = 0;
         
         // 使用循环制造运行时错误
         for i in 0..1000 {{
             counter += 1;
             if counter == 500 {{
                 // 在循环中间制造数组越界错误（运行时才能确定）
                 let test_array = vec![1, 2, 3];
                 let error_index = counter + 10;  // 使用运行时变量避免编译期检测
                 let _error_value = test_array[error_index];  // 这会导致panic，但编译时不会检测到
                 error_triggered = true;
                 break;
             }}
         }}
         
         if error_triggered {{
             println!("执行错误已触发，程序应该崩溃");
             history_operations.push(format!("操作{{}}: 执行错误 - 已触发", operation_count));
         }}
         
         // 这行代码不会被执行
         println!("这行代码不应该被执行到");
        
        // 操作4：修改第二个备忘录（不会被执行）
        operation_count += 1;
        println!("操作{{}}: 修改第二个备忘录", operation_count);
        
         let second_update_result = call_mcp_tool("memos_update_visibility", &serde_json::json!({{
             "memo_name": "{self.memo_ids[1]}",
             "visibility": "PUBLIC"
         }}));
        
        match second_update_result {{
            Ok(response) => {{
                println!("第二个备忘录修改成功");
                success_count += 1;
                history_operations.push(format!("操作{{}}: 修改第二个备忘录 - 成功", operation_count));
            }},
            Err(e) => {{
                println!("第二个备忘录修改失败: {{}}", e);
                failure_count += 1;
                history_operations.push(format!("操作{{}}: 修改第二个备忘录 - 失败: {{}}", operation_count, e));
            }}
        }}
        
        // 记录测试结果
        result.insert("success".to_string(), serde_json::Value::Bool(success_count > 0));
        result.insert("test_result".to_string(), serde_json::Value::String("历史队列机制测试".to_string()));
        result.insert("operation_count".to_string(), serde_json::Value::Number(serde_json::Number::from(operation_count)));
        result.insert("success_count".to_string(), serde_json::Value::Number(serde_json::Number::from(success_count)));
        result.insert("failure_count".to_string(), serde_json::Value::Number(serde_json::Number::from(failure_count)));
        result.insert("history_operations".to_string(), serde_json::Value::Array(
            history_operations.into_iter().map(|op| serde_json::Value::String(op)).collect()
        ));
        
        println!("历史队列测试完成，总操作: {{}}, 成功: {{}}, 失败: {{}}", operation_count, success_count, failure_count);
        """
        
        return await self._send_rollback_test_request(
            "history_queue_mechanism",
            rust_code,
            "测试历史队列机制",
            "memos_history_test",
            "history_test"
        )
    
    async def test_comprehensive_rollback(self) -> Dict[str, Any]:
        """测试综合回退机制 - 包含多个操作和复杂的错误处理"""
        print("\n🔍 测试综合回退机制...")
        
        # 构造更复杂的Rust代码
        rust_code = f"""
        // 测试综合回退机制
        use serde_json::Value;
        use std::collections::HashMap;
        
        // @WRITE_OPERATION 标记，触发写入模式
        let mut result = HashMap::new();
        let mut operations = Vec::new();
        let mut rollback_operations = Vec::new();
        
        println!("开始综合回退机制测试");
        
        // 定义要测试的备忘录ID
        let memo_ids = vec!["{self.memo_ids[0]}", "{self.memo_ids[1]}"];
        
        // 操作1：获取备忘录列表
        println!("步骤1: 获取备忘录列表");
        let get_result = call_mcp_tool("memos_get_memos", &serde_json::Value::Object(serde_json::Map::new()));
        
        match get_result {{
            Ok(response) => {{
                println!("获取备忘录列表成功");
                operations.push("获取备忘录列表 - 成功".to_string());
            }},
            Err(e) => {{
                println!("获取备忘录列表失败: {{}}", e);
                operations.push(format!("获取备忘录列表 - 失败: {{}}", e));
            }}
        }}
        
        // 操作2：修改第一个备忘录
        println!("步骤2: 修改第一个备忘录可见性");
        let first_memo_id = memo_ids[0];
         let first_update_result = call_mcp_tool("memos_update_visibility", &serde_json::json!({{
             "memo_name": first_memo_id,
             "visibility": "PUBLIC"
         }}));
        
        match first_update_result {{
            Ok(response) => {{
                println!("第一个备忘录修改成功: {{}}", first_memo_id);
                operations.push(format!("修改第一个备忘录({{}}) - 成功", first_memo_id));
                
                // 记录回退操作
                rollback_operations.push(format!("回退第一个备忘录({{}}) - 设置为PRIVATE", first_memo_id));
            }},
            Err(e) => {{
                println!("第一个备忘录修改失败: {{}}", e);
                operations.push(format!("修改第一个备忘录({{}}) - 失败: {{}}", first_memo_id, e));
            }}
        }}
        
         // 操作3：故意引入执行错误
         println!("步骤3: 故意引入执行错误");
         
         // 制造运行时错误（使用运行时才能确定的值避免编译期检测）
         let mut error_triggered = false;
         let mut counter = 0;
         
         // 使用循环制造运行时错误
         for i in 0..1000 {{
             counter += 1;
             if counter == 500 {{
                 // 在循环中间制造数组越界错误（运行时才能确定）
                 let test_array = vec![1, 2, 3];
                 let error_index = counter + 10;  // 使用运行时变量避免编译期检测
                 let _error_value = test_array[error_index];  // 这会导致panic，但编译时不会检测到
                 error_triggered = true;
                 break;
             }}
         }}
         
         if error_triggered {{
             println!("执行错误已触发，程序应该崩溃");
             operations.push("执行错误 - 已触发".to_string());
         }}
        
        // 操作4：修改第二个备忘录（不会被执行）
        println!("步骤4: 修改第二个备忘录可见性");
        let second_memo_id = memo_ids[1];
         let second_update_result = call_mcp_tool("memos_update_visibility", &serde_json::json!({{
             "memo_name": second_memo_id,
             "visibility": "PUBLIC"
         }}));
        
        match second_update_result {{
            Ok(response) => {{
                println!("第二个备忘录修改成功: {{}}", second_memo_id);
                operations.push(format!("修改第二个备忘录({{}}) - 成功", second_memo_id));
            }},
            Err(e) => {{
                println!("第二个备忘录修改失败: {{}}", e);
                operations.push(format!("修改第二个备忘录({{}}) - 失败: {{}}", second_memo_id, e));
            }}
        }}
        
        // 记录测试结果
        result.insert("success".to_string(), serde_json::Value::Bool(true));
        result.insert("test_result".to_string(), serde_json::Value::String("综合回退机制测试".to_string()));
        result.insert("operations".to_string(), serde_json::Value::Array(
            operations.into_iter().map(|op| serde_json::Value::String(op)).collect()
        ));
        result.insert("rollback_operations".to_string(), serde_json::Value::Array(
            rollback_operations.into_iter().map(|op| serde_json::Value::String(op)).collect()
        ));
        
        println!("综合回退机制测试完成");
        """
        
        return await self._send_rollback_test_request(
            "comprehensive_rollback",
            rust_code,
            "测试综合回退机制",
            "memos_comprehensive_test",
            "comprehensive_test"
        )
    
    async def _send_rollback_test_request(self, test_name: str, rust_code: str, description: str, 
                                         api_endpoint: str, operation_type: str) -> Dict[str, Any]:
        """发送回退测试请求的通用方法"""
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
                        "expected_result": "测试回退机制和历史队列功能"
                    },
                    "input_data": json.dumps({
                        "test_type": f"rollback_{operation_type}",
                        "memo_ids": self.memo_ids,
                        "timestamp": datetime.now().isoformat()
                    }),
                    "api_spec_url": None,
                    "user_query": f"测试回退机制和历史队列功能 - {description}",
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
        self.print_separator("Memos回退机制和历史队列测试总结")
        
        total_tests = len(self.test_results)
        successful_tests = 0
        failed_tests = 0
        
        # 统计回退机制相关信息
        rollback_tests = 0
        history_tests = 0
        comprehensive_tests = 0
        
        rollback_success = 0
        history_success = 0
        comprehensive_success = 0
        
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
                if "rollback_mechanism" in test_name:
                    rollback_tests += 1
                    if inner_result.get("success"):
                        rollback_success += 1
                elif "history_queue" in test_name:
                    history_tests += 1
                    if inner_result.get("success"):
                        history_success += 1
                elif "comprehensive" in test_name:
                    comprehensive_tests += 1
                    if inner_result.get("success"):
                        comprehensive_success += 1
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
        if rollback_tests > 0:
            print(f"  回退机制测试: {rollback_success}/{rollback_tests} ({(rollback_success/rollback_tests*100):.1f}%)")
        if history_tests > 0:
            print(f"  历史队列测试: {history_success}/{history_tests} ({(history_success/history_tests*100):.1f}%)")
        if comprehensive_tests > 0:
            print(f"  综合回退测试: {comprehensive_success}/{comprehensive_tests} ({(comprehensive_success/comprehensive_tests*100):.1f}%)")
        
        # 显示各测试的持续时间
        if total_tests > 0:
            print(f"\n⏱️ 测试持续时间:")
            for test_name, result in self.test_results.items():
                duration = result.get("duration", 0)
                print(f"  - {test_name}: {duration:.2f}秒")
        
        # 分析回退机制是否正常工作
        print(f"\n🔄 回退机制分析:")
        rollback_enabled_tests = 0
        rollback_details = []
        
        for test_name, result in self.test_results.items():
            if "result" in result and isinstance(result["result"], dict):
                inner_result = result["result"]
                if "rollback_info" in inner_result:
                    rollback_enabled_tests += 1
                    rollback_info = inner_result["rollback_info"]
                    rollback_count = rollback_info.get('rollback_count', 0)
                    rollback_success_count = rollback_info.get('rollback_success_count', 0)
                    rollback_failure_count = rollback_info.get('rollback_failure_count', 0)
                    
                    print(f"  - {test_name}: 回退信息可用")
                    print(f"    回退操作数: {rollback_count}")
                    print(f"    回退成功数: {rollback_success_count}")
                    print(f"    回退失败数: {rollback_failure_count}")
                    
                    rollback_details.append({
                        "test": test_name,
                        "rollback_count": rollback_count,
                        "rollback_success": rollback_success_count,
                        "rollback_failure": rollback_failure_count
                    })
        
        if rollback_enabled_tests > 0:
            print(f"  ✅ 回退机制正常工作 ({rollback_enabled_tests}/{total_tests} 个测试)")
        else:
            print(f"  ⚠️ 回退机制可能未正常工作")
        
        # 分析历史队列是否正常工作
        print(f"\n📚 历史队列分析:")
        history_enabled_tests = 0
        
        for test_name, result in self.test_results.items():
            if "result" in result and isinstance(result["result"], dict):
                inner_result = result["result"]
                if "history_info" in inner_result:
                    history_enabled_tests += 1
                    history_info = inner_result["history_info"]
                    history_count = history_info.get('history_count', 0)
                    
                    print(f"  - {test_name}: 历史队列信息可用")
                    print(f"    历史记录数: {history_count}")
        
        if history_enabled_tests > 0:
            print(f"  ✅ 历史队列正常工作 ({history_enabled_tests}/{total_tests} 个测试)")
        else:
            print(f"  ⚠️ 历史队列可能未正常工作")
        
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
        """运行所有回退机制测试"""
        self.print_separator("Memos回退机制和历史队列测试")
        
        # 检查服务器连接
        if not await self.check_server_connection():
            print("❌ 无法连接到ToolPro服务器，请确保服务器正在运行")
            return
        
        print("\n🚀 开始运行回退机制和历史队列测试...")
        print("📋 测试说明：")
        print("  - 直接使用 /compile-and-execute API 进行测试")
        print("  - 使用预编写的Rust代码测试回退机制")
        print("  - 测试写入模式下的回退和历史队列功能")
        print("  - 包括回退机制、历史队列、综合测试三种类型")
        print(f"  - 测试的备忘录ID: {self.memo_ids}")
        
        # 运行各种回退测试
        print("\n🔄 开始回退机制测试...")
        await self.test_rollback_mechanism()
        
        print("\n📚 开始历史队列机制测试...")
        await self.test_history_queue_mechanism()
        
        print("\n🔧 开始综合回退机制测试...")
        await self.test_comprehensive_rollback()
        
        # 打印总结
        self.print_summary()
    
    async def run_specific_test(self, test_type: str):
        """运行特定类型的回退测试"""
        self.print_separator(f"Memos回退机制测试 - {test_type}")
        
        # 检查服务器连接
        if not await self.check_server_connection():
            print("❌ 无法连接到ToolPro服务器，请确保服务器正在运行")
            return
        
        print(f"\n🚀 开始运行 {test_type} 测试...")
        print("📋 测试说明：")
        print("  - 直接使用 /compile-and-execute API 进行测试")
        print("  - 使用预编写的Rust代码测试特定回退功能")
        print("  - 测试写入模式下的回退和历史队列功能")
        print(f"  - 测试的备忘录ID: {self.memo_ids}")
        
        if test_type == "rollback_mechanism":
            await self.test_rollback_mechanism()
        elif test_type == "history_queue":
            await self.test_history_queue_mechanism()
        elif test_type == "comprehensive":
            await self.test_comprehensive_rollback()
        else:
            print(f"❌ 未知的测试类型: {test_type}")
            return
        
        # 打印总结
        self.print_summary()


def interactive_test_selection():
    """交互式测试选择"""
    print("\n" + "="*80)
    print("  ToolPro Memos回退机制和历史队列测试工具 ")
    print("="*80)
    print("\n请选择要测试的回退机制类型：")
    print()
    
    test_options = [
        ("1", "all", "所有测试", "运行所有类型的回退机制测试"),
        ("2", "rollback_mechanism", "回退机制测试", "测试基本的回退机制功能"),
        ("3", "history_queue", "历史队列测试", "测试历史队列记录功能"),
        ("4", "comprehensive", "综合回退测试", "测试综合的回退机制"),
        ("0", "exit", "退出", "退出测试程序")
    ]
    
    for option, test_type, name, description in test_options:
        print(f"  {option:2}. {name:20} - {description}")
    
    print()
    
    while True:
        try:
            choice = input("请输入选择 (0-4): ").strip()
            
            if choice == "0":
                print("退出测试程序")
                return None
            elif choice in ["1", "2", "3", "4"]:
                selected_option = next(opt for opt in test_options if opt[0] == choice)
                test_type = selected_option[1]
                print(f"\n已选择: {selected_option[2]} - {selected_option[3]}")
                return test_type
            else:
                print("❌ 无效选择，请输入 0-4 之间的数字")
        except KeyboardInterrupt:
            print("\n\n用户取消操作")
            return None
        except Exception as e:
            print(f"❌ 输入错误: {e}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Memos回退机制和历史队列测试工具")
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="ToolPro服务器地址 (默认: http://localhost:8000)"
    )
    parser.add_argument(
        "--test",
        choices=[
            "all", "rollback_mechanism", "history_queue", "comprehensive", "interactive"
        ],
        default="interactive",
        help="测试类型: all=所有测试, rollback_mechanism=回退机制, history_queue=历史队列, comprehensive=综合测试, interactive=交互式选择"
    )
    
    args = parser.parse_args()
    
    # 确定要运行的测试类型
    if args.test == "interactive":
        test_type = interactive_test_selection()
        if test_type is None:
            return
    else:
        test_type = args.test
    
    async with MemosRollbackTester(args.server) as tester:
        if test_type == "all":
            await tester.run_all_tests()
        else:
            await tester.run_specific_test(test_type)


if __name__ == "__main__":
    asyncio.run(main())
