"""
智能代理脚本 - Agent
根据用户输入的自然语言提取关键信息，基于已有规范总结API Access Tasks发送给invocation scheduler层
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import httpx
from core.path_utils import PathUtils

# 导入全局开销统计器
sys.path.insert(0, str(PathUtils.get_project_root()))
from core.global_cost_tracker import get_global_cost_tracker, start_stage_tracking, end_stage_tracking

# 添加项目根目录到Python路径
project_root = PathUtils.get_project_root()
sys.path.insert(0, str(project_root))

# 导入配置
from config import Config

# 添加MCP客户端路径
mcp_client_path = PathUtils.get_mcp_client_dir()
if str(mcp_client_path) not in sys.path:
    sys.path.insert(0, str(mcp_client_path))

try:
    from session_manager import SessionManager
except ImportError:
    SessionManager = None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('agent.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


@dataclass
class APIAccessTask:
    """API访问任务数据结构"""
    user_input: str  # 用户输入的自然语言
    api_interface: str  # API接口名称
    mcp_tool_name: str  # MCP工具名称
    parameters: List[Dict[str, Any]]  # 参数列表（可以包含多个列表）
    expected_calls: int  # 预计调用次数
    has_dependency: bool  # 是否与其他API有依赖关系
    dependency_api: Optional[str] = None  # 依赖的API接口
    examples: Optional[List[Dict[str, Any]]] = None  # API响应示例


class IntelligentAgent:
    """智能代理类"""
    
    def __init__(self, mcp_config_path: str = None):
        """
        初始化智能代理
        
        Args:
            mcp_config_path: MCP客户端配置文件路径
        """
        self.config = Config()
        self.llm_config = self.config.get_llm_config()
        
        # 使用独立的SessionManager实例
        self.session_manager = None
        self.available_tools: Dict[str, List[Dict[str, Any]]] = {}
        self.mcp_initialized = False
        
        # 设置MCP配置文件路径
        if mcp_config_path is None:
            mcp_client_dir = PathUtils.get_mcp_client_dir()
            self.mcp_config_path = str(mcp_client_dir / "client_config.toml")
        else:
            self.mcp_config_path = mcp_config_path
    
    async def initialize(self) -> bool:
        """初始化代理"""
        try:
            logger.info("正在初始化智能代理...")
            
            # 检查SessionManager是否可用
            if SessionManager is None:
                logger.error("SessionManager模块不可用")
                return False
            
            # 创建独立的SessionManager实例
            logger.info("正在创建SessionManager实例...")
            self.session_manager = SessionManager(self.mcp_config_path)
            
            # 启动MCP服务器
            logger.info("正在启动MCP服务器...")
            if not await self.session_manager.start_all_servers():
                logger.error("启动MCP服务器失败")
                self.session_manager = None
                return False
            
            # 初始化连接
            logger.info("正在初始化MCP连接...")
            if not await self.session_manager.initialize_connections():
                logger.error("初始化MCP连接失败")
                self.session_manager = None
                return False
            
            # 获取可用工具
            self.available_tools = self.session_manager.get_all_tools_by_server()
            logger.info(f"获取到 {len(self.available_tools)} 个服务器的工具")
            
            self.mcp_initialized = True
            logger.info("智能代理初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化代理失败: {e}")
            return False
    
    async def call_llm(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """调用LLM API"""
        # 开始agent-llm阶段统计
        # start_time = start_stage_tracking("agent_llm")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.llm_config.get('api_key')}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.llm_config.get("model"),
                "messages": messages,
                "temperature": 0.3,  # 降低温度以获得更一致的结果
                "max_tokens": 3000
            }
            
            # 计算请求字节数
            request_bytes = len(json.dumps(data).encode('utf-8'))
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.llm_config.get('base_url')}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                # 计算响应字节数
                response_bytes = len(response.content)
                
                if response.status_code == 200:
                    result = response.json()
                    response_data = {
                        "success": True,
                        "content": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "usage": result.get("usage", {})
                    }
                else:
                    response_data = {
                        "success": False,
                        "error": f"LLM API调用失败: {response.status_code} - {response.text}"
                    }
                
                # 结束agent-llm阶段统计
                # end_stage_tracking("agent_llm", start_time, request_bytes, response_bytes)
                
                return response_data
                    
        except Exception as e:
            logger.error(f"调用LLM失败: {e}")
            # 即使出错也要结束统计
            # end_stage_tracking("agent_llm", start_time, 0, 0)
            return {
                "success": False,
                "error": f"LLM调用失败: {str(e)}"
            }
    
    
    async def generate_api_access_tasks(self, user_input: str) -> List[APIAccessTask]:
        """基于用户输入生成API访问任务"""
        try:
            # 获取MCP工具信息
            tools_info = self.session_manager.list_available_tools()
            
            # 获取所有工具的详细信息
            all_tools = self.session_manager.get_all_tools_by_server()
            tools_details = {}
            for server_name, tools in all_tools.items():
                for tool in tools:
                    tools_details[tool.get("name", "")] = {
                        "description": tool.get("description", ""),
                        "inputSchema": tool.get("inputSchema", {}),
                        "examples": tool.get("examples", []),
                        "server": server_name
                    }
            
            system_prompt = f"""你是一个智能API任务规划助手。根据用户输入的自然语言查询，生成结构化的API访问任务。

可用工具信息：
{tools_info}

工具详细信息：
{json.dumps(tools_details, ensure_ascii=False, indent=2)}

请根据用户输入，分析需要调用哪些MCP工具，并生成API访问任务列表。每个任务应该包含：
1. user_input: 用户输入的自然语言
2. api_interface: API接口名称（对应的MCP工具名称）
3. mcp_tool_name: MCP工具名称（与api_interface相同）
4. parameters: 参数列表（可以包含多个参数集合，用于批量操作）
5. expected_calls: 预计调用次数（根据用户需求判断需要调用几次）
6. has_dependency: 是否与其他API有依赖关系
7. dependency_api: 依赖的API接口（如果有）
8. examples: API响应示例（从工具详细信息中获取）

其中如获取多次列表，只需要在expected_calls中体现次数，parameters只需要提供一个空字典

请以JSON格式返回，格式如下：
```json
[
    {{
        "user_input": "用户输入的自然语言",
        "api_interface": "API接口名称",
        "mcp_tool_name": "MCP工具名称",
        "parameters": [
            {{"param1": "value1", "param2": "value2"}},
            {{"param1": "value3", "param2": "value4"}}
        ],
        "expected_calls": 1,
        "has_dependency": false,
        "dependency_api": null,
        "examples": [
            {{
                "...": "..."
            }}
        ]
    }}
]
```

重要提示：
- 仔细分析用户需求，判断是否需要先查询再更新，如果需要请生成多个任务并设置依赖关系
- 参数列表可以包含多个参数集合，用于批量操作
- 确保API接口名称与MCP工具名称一致
- 根据用户需求合理判断expected_calls的值
- 考虑任务的执行顺序和依赖关系
- examples字段必须从工具详细信息中获取，不能为空"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请为以下任务生成API访问任务：{user_input}"}
            ]
            
            # 调用LLM
            llm_result = await self.call_llm(messages)
            
            if not llm_result.get("success"):
                logger.error(f"LLM调用失败: {llm_result.get('error')}")
                return []
            
            content = llm_result.get("content", "")
            logger.info(f"LLM响应: {content}")
            
            # 解析JSON响应
            try:
                # 提取JSON部分
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    if json_end > json_start:
                        json_str = content[json_start:json_end].strip()
                    else:
                        json_str = content[json_start:].strip()
                else:
                    json_str = content.strip()
                
                tasks_data = json.loads(json_str)
                
                # 转换为APIAccessTask对象
                api_tasks = []
                for task_data in tasks_data:
                    # 获取工具示例
                    tool_name = task_data.get("mcp_tool_name", "")
                    tool_examples = tools_details.get(tool_name, {}).get("examples", [])
                    
                    api_task = APIAccessTask(
                        user_input=task_data.get("user_input", user_input),
                        api_interface=task_data.get("api_interface", ""),
                        mcp_tool_name=task_data.get("mcp_tool_name", ""),
                        parameters=task_data.get("parameters", []),
                        expected_calls=task_data.get("expected_calls", 1),
                        has_dependency=task_data.get("has_dependency", False),
                        dependency_api=task_data.get("dependency_api"),
                        examples=tool_examples
                    )
                    api_tasks.append(api_task)
                
                logger.info(f"生成了 {len(api_tasks)} 个API访问任务")
                return api_tasks
                
            except json.JSONDecodeError as e:
                logger.error(f"解析LLM响应JSON失败: {e}")
                logger.error(f"原始响应: {content}")
                return []
                
        except Exception as e:
            logger.error(f"生成API访问任务失败: {e}")
            return []
    
    def format_tasks_for_scheduler(self, api_tasks: List[APIAccessTask]) -> Dict[str, Any]:
        """格式化任务为调度器可用的格式"""
        formatted_tasks = []
        
        for task in api_tasks:
            formatted_task = {
                "task_id": f"task_{len(formatted_tasks) + 1}",
                "user_input": task.user_input,
                "api_interface": task.api_interface,
                "mcp_tool_name": task.mcp_tool_name,
                "parameters": task.parameters,
                "expected_calls": task.expected_calls,
                "has_dependency": task.has_dependency,
                "dependency_api": task.dependency_api,
                "examples": task.examples,
                "status": "pending",
                "created_at": asyncio.get_event_loop().time()
            }
            formatted_tasks.append(formatted_task)
        
        return {
            "tasks": formatted_tasks,
            "total_tasks": len(formatted_tasks),
            "summary": {
                "query_tasks": len([t for t in api_tasks if t.api_interface.startswith("get")]),
                "update_tasks": len([t for t in api_tasks if t.api_interface.startswith("update")]),
                "upload_tasks": len([t for t in api_tasks if t.api_interface.startswith("upload")]),
                "download_tasks": len([t for t in api_tasks if t.api_interface.startswith("download")])
            }
        }
    
    async def process_user_query(self, user_input: str, debug_mode: bool = False, route_selection: str = "dynamic_select", geo_delay: float = 0, extra_rtt_ms: int = 0) -> Dict[str, Any]:
        """处理用户查询的主入口"""
        try:
            logger.info(f"处理用户查询: {user_input}")
            
            # 生成API访问任务
            api_tasks = await self.generate_api_access_tasks(user_input)
            
            if not api_tasks:
                return {
                    "success": False,
                    "error": "无法生成API访问任务"
                }
            
            # 格式化任务为调度器格式
            formatted_tasks = self.format_tasks_for_scheduler(api_tasks)
            
            logger.info(f"成功生成 {len(api_tasks)} 个API访问任务")
            
            # 发送任务给invocation scheduler处理
            scheduler_result = await self._send_tasks_to_scheduler(formatted_tasks, debug_mode, route_selection, geo_delay, extra_rtt_ms)
            
            return {
                "success": scheduler_result.get("success", False),
                "api_tasks": [asdict(task) for task in api_tasks],
                "formatted_tasks": formatted_tasks,
                "scheduler_result": scheduler_result,
                "scheduler_response": scheduler_result,  # 添加scheduler响应
                "message": f"成功为查询 '{user_input}' 生成了 {len(api_tasks)} 个API访问任务并发送给调度器处理"
            }
            
        except Exception as e:
            logger.error(f"处理用户查询失败: {e}")
            return {
                "success": False,
                "error": f"处理查询时出错: {str(e)}"
            }
    
    async def _send_tasks_to_scheduler(self, formatted_tasks: Dict[str, Any], debug_mode: bool = False, route_selection: str = "dynamic_select", geo_delay: float = 0, extra_rtt_ms: int = 0) -> Dict[str, Any]:
        """发送任务给invocation scheduler处理"""
        try:
            logger.info("发送API访问任务给调度器...")
            
            # 构建请求数据
            request_data = {
                "api_tasks": formatted_tasks["tasks"],
                "force_read_mode": debug_mode,
                "route_selection": route_selection,
                "geo_delay": geo_delay,
                "extra_rtt_ms": int(extra_rtt_ms or 0),
            }
            
            # 打印参数详情
            print(f"[Agent] force_read_mode: {debug_mode}, route_selection: {route_selection}, geo_delay: {geo_delay}, extra_rtt_ms: {extra_rtt_ms}")
            
            # 发送到client service的invocation scheduler端点
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "http://localhost:8000/invocation-scheduler/process-tasks",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"调度器处理成功: {result.get('success', False)}")
                    return result
                else:
                    error_msg = f"调度器处理失败: HTTP {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except Exception as e:
            error_msg = f"发送任务给调度器失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def check_mcp_tool_calls(self, rust_code: str, query: str) -> Dict[str, Any]:
        """检查生成的Rust代码中的MCP工具调用是否规范"""
        try:
            logger.info("开始检查MCP工具调用规范性...")
            
            # 获取MCP工具信息
            tools_info = self.session_manager.list_available_tools()
            all_tools = self.session_manager.get_all_tools_by_server()
            
            # 构建工具详细信息
            tools_details = {}
            for server_name, tools in all_tools.items():
                for tool in tools:
                    tools_details[tool.get("name", "")] = {
                        "description": tool.get("description", ""),
                        "inputSchema": tool.get("inputSchema", {}),
                        "examples": tool.get("examples", []),
                        "server": server_name
                    }
            
            system_prompt = f"""你是一个MCP工具调用检查助手。请根据工具调用详情，检查生成的Rust代码是否在工具名称和参数上符合规范。

可用工具信息：
{tools_info}

工具详细信息：
{json.dumps(tools_details, ensure_ascii=False, indent=2)}

检查要点：
1. 工具名称是否正确（必须与available_tools中的名称完全一致）
2. 参数格式是否正确（必须符合工具的inputSchema）
3. 参数类型是否正确
4. 是否缺少必需参数
5. 是否有多余参数

原用户查询：{query}

需要检查的Rust代码：
```rust
{rust_code}
```

请仔细检查代码中的call_mcp_tool调用，如果所有工具调用都符合规范，仅返回"yes"；否则返回具体的错误详情，包括：
- 错误的具体位置
- 工具名称是否正确
- 参数是否正确
- 具体的修改建议"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请检查以下Rust代码中的MCP工具调用是否规范：\n\n```rust\n{rust_code}\n```"}
            ]
            
            # 调用LLM进行检查
            llm_result = await self.call_llm(messages)
            
            if not llm_result.get("success"):
                logger.error(f"MCP工具调用检查失败: {llm_result.get('error')}")
                return {
                    "success": False,
                    "error": f"LLM检查失败: {llm_result.get('error')}",
                    "is_valid": False
                }
            
            content = llm_result.get("content", "").strip().lower()
            logger.info(f"MCP工具调用检查响应: {content}")
            
            # 判断检查结果
            if content == "yes":
                logger.info("MCP工具调用检查通过")
                return {
                    "success": True,
                    "is_valid": True,
                    "message": "所有MCP工具调用都符合规范"
                }
            else:
                logger.warning("MCP工具调用检查未通过")
                return {
                    "success": True,
                    "is_valid": False,
                    "error_details": content,
                    "message": "MCP工具调用存在问题"
                }
                
        except Exception as e:
            logger.error(f"检查MCP工具调用失败: {e}")
            return {
                "success": False,
                "error": f"检查过程中出错: {str(e)}",
                "is_valid": False
            }
    
    async def validate_mcp_response(self, tool_name: str, parameters: Dict[str, Any], response: Any) -> str:
        """验证MCP工具响应是否正常
        
        Args:
            tool_name: MCP工具名称
            parameters: 调用参数
            response: MCP工具响应结果
            
        Returns:
            "ok" 如果响应正常，否则返回 "error"
        """
        try:
            logger.info(f"开始验证MCP工具响应: {tool_name}")
            
            # 构建验证提示词
            system_prompt = """你是一个MCP工具响应验证助手。请根据工具名称、调用参数和响应结果，判断响应是否正常。

判断标准：
1. 响应格式是否正确（JSON格式）
2. 是否包含预期的数据结构
3. 是否有明显的错误信息
4. 响应内容是否合理

请只返回 "ok" 或 "error"，不要返回其他内容。"""

            # 准备响应数据（确保可以序列化）
            try:
                response_str = json.dumps(response, ensure_ascii=False, indent=2)
            except (TypeError, ValueError):
                response_str = str(response)
            
            user_prompt = f"""工具名称: {tool_name}
调用参数: {json.dumps(parameters, ensure_ascii=False, indent=2)}
响应结果: {response_str}

请判断这个响应是否正常，只返回 "ok" 或 "error"。"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 调用LLM进行验证
            llm_result = await self.call_llm(messages)
            
            if not llm_result.get("success"):
                logger.error(f"MCP响应验证失败: {llm_result.get('error')}")
                return "error"
            
            content = llm_result.get("content", "").strip().lower()
            logger.info(f"MCP响应验证结果: {content}")
            
            # 返回验证结果
            if content == "ok":
                logger.info(f"MCP工具 {tool_name} 响应验证通过")
                return "ok"
            else:
                logger.warning(f"MCP工具 {tool_name} 响应验证失败")
                return "error"
                
        except Exception as e:
            logger.error(f"验证MCP响应失败: {e}")
            return "error"
    
    async def shutdown(self):
        """关闭代理"""
        try:
            logger.info("正在关闭智能代理...")
            
            # 关闭SessionManager
            if self.session_manager:
                await self.session_manager.shutdown()
                logger.info("SessionManager已关闭")
            
            # 重置本地状态
            self.session_manager = None
            self.mcp_initialized = False
            self.available_tools = {}
            
            logger.info("智能代理已关闭")

        except Exception as e:
            logger.error(f"关闭代理失败: {e}")


async def main():
    """主函数 - 演示用法"""
    agent = IntelligentAgent()
    
    try:
        # 初始化代理
        if not await agent.initialize():
            logger.error("代理初始化失败")
            return
        
        # 示例查询
        test_queries = [
            "查询当前用户列表",
            "查询当前用户列表之后修改所有用户的备忘录状态为公开"
        ]
        
        print("\n=== 智能代理演示 ===")
        
        for query in test_queries:
            print(f"\n用户查询: {query}")
            print("-" * 50)
            
            result = await agent.process_user_query(query)
            
            if result["success"]:
                print(f"[成功] 生成 {len(result['api_tasks'])} 个API访问任务")
                
                # 显示任务详情
                for i, task in enumerate(result['api_tasks'], 1):
                    print(f"\n任务 {i}:")
                    print(f"  API接口: {task['api_interface']}")
                    print(f"  MCP工具: {task['mcp_tool_name']}")
                    print(f"  参数: {task['parameters']}")
                    print(f"  预计调用次数: {task['expected_calls']}")
                    if task['has_dependency']:
                        print(f"  依赖: {task['dependency_api']}")
                
                # 显示调度器格式
                print(f"\n调度器格式:")
                print(json.dumps(result['formatted_tasks'], ensure_ascii=False, indent=2))
            else:
                print(f"[失败] 处理失败: {result.get('error', '未知错误')}")
            
            print("\n" + "="*60)
    
    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"运行失败: {e}")
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
