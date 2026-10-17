"""
Invocation Scheduler
负责接收API Access Tasks，动态选择Direct API Access或Custom API Access路线
"""

import asyncio
import json
import logging
import os
import time
import sys
from typing import Dict, List, Any, Optional
import httpx
from dataclasses import dataclass
from pathlib import Path

from .performance_tracker import PerformanceTracker
from core.global_cost_tracker import get_global_cost_tracker, start_stage_tracking, end_stage_tracking, get_stage_stats
from core.path_utils import PathUtils

# 添加MCP客户端路径
import sys
from pathlib import Path
mcp_client_path = PathUtils.get_mcp_client_dir()
if str(mcp_client_path) not in sys.path:
    sys.path.insert(0, str(mcp_client_path))

try:
    from session_manager import SessionManager
except ImportError:
    SessionManager = None

logger = logging.getLogger(__name__)


@dataclass
class APIAccessTask:
    """API访问任务数据结构"""
    user_input: str
    api_interface: str
    mcp_tool_name: str
    parameters: List[Dict[str, Any]]
    expected_calls: int
    has_dependency: bool
    dependency_api: Optional[str] = None


@dataclass
class ExecutionResult:
    """执行结果数据结构"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    route_used: str = ""
    api_calls_made: int = 0
    # 新增编译阶段和API阶段统计数据
    wasm_compile_stats: Optional[Dict[str, Any]] = None
    wasm_api_stats: Optional[Dict[str, Any]] = None
    # 新增响应验证开销统计
    validation_duration: float = 0.0
    validation_request_bytes: int = 0
    validation_response_bytes: int = 0
    configured_extra_rtt_ms: int = 0
    effective_rtt_ms: int = 0
    selected_mode: str = ""
    mode_switch_count: int = 0


class InvocationScheduler:
    """调用调度器类"""
    
    def __init__(self, 
                 client_service_url: str = "http://localhost:8000",
                 mcp_config_path: str = None):
        """
        初始化调用调度器
        
        Args:
            client_service_url: 客户端服务地址
            mcp_config_path: MCP配置文件路径
        """
        self.client_service_url = client_service_url
        self.performance_tracker = PerformanceTracker()
        
        # 设置MCP配置文件路径
        if mcp_config_path is None:
            mcp_client_dir = PathUtils.get_mcp_client_dir()
            self.mcp_config_path = str(mcp_client_dir / "client_config.toml")
        else:
            self.mcp_config_path = mcp_config_path
        
        # SessionManager实例，用于Direct路线
        self.session_manager = None
        
        logger.info(f"调用调度器初始化完成")
        logger.info(f"客户端服务: {self.client_service_url}")
        logger.info(f"MCP配置文件: {self.mcp_config_path}")

    @staticmethod
    def _map_route_selection(route_selection: Optional[str]) -> str:
        """
        对外 route_selection -> 内部三态：dynamic_select | direct | wasm

        program / program_mode -> wasm；stepwise -> direct。
        """
        r = (route_selection or "dynamic_select").strip().lower()
        if r in ("program", "program_mode"):
            return "wasm"
        if r == "stepwise":
            return "direct"
        if r in ("wasm", "direct", "dynamic_select"):
            return r
        logger.warning("未知 route_selection=%r，回退 dynamic_select", route_selection)
        return "dynamic_select"

    @staticmethod
    def _route_used_to_selected_mode(route_used: str) -> str:
        if route_used == "wasm":
            return "program"
        if route_used == "direct":
            return "stepwise"
        return route_used or "unknown"

    @staticmethod
    async def _sleep_extra_rtt_ms(ms: int) -> int:
        if ms and ms > 0:
            await asyncio.sleep(ms / 1000.0)
            return int(ms)
        return 0
    
    async def _create_session_manager(self) -> Optional[SessionManager]:
        """创建并初始化SessionManager实例"""
        try:
            logger.info("正在创建新的SessionManager实例...")
            
            # 检查SessionManager是否可用
            if SessionManager is None:
                logger.error("SessionManager模块不可用")
                return None
            
            # 创建新的SessionManager实例
            session_manager = SessionManager(self.mcp_config_path)
            
            # 启动MCP服务器
            if not await session_manager.start_all_servers():
                logger.error("启动MCP服务器失败")
                return None
            
            # 初始化连接
            if not await session_manager.initialize_connections():
                logger.error("初始化MCP连接失败")
                return None
            
            logger.info("SessionManager实例创建成功")
            return session_manager
            
        except Exception as e:
            logger.error(f"创建SessionManager实例失败: {e}")
            return None
    
    async def _create_agent_instance(self):
        """创建并初始化Agent实例"""
        try:
            logger.info("正在创建新的Agent实例...")
            
            # 动态导入agent模块
            import importlib.util
            
            project_root = PathUtils.get_project_root()
            agent_file = project_root / "experiment" / "agent.py"
            
            if not agent_file.exists():
                logger.error(f"Agent文件不存在: {agent_file}")
                return None
                
            spec = importlib.util.spec_from_file_location("agent", agent_file)
            agent_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(agent_module)
            
            # 创建Agent实例
            agent_instance = agent_module.IntelligentAgent(self.mcp_config_path)
            
            # 初始化Agent
            if await agent_instance.initialize():
                logger.info("Agent实例创建成功")
                return agent_instance
            else:
                logger.warning("Agent初始化失败")
                return None
                
        except Exception as e:
            logger.error(f"创建Agent实例失败: {e}")
            return None
    
    
    async def process_api_access_tasks(self, api_tasks: List[Dict[str, Any]], 
                                     force_read_mode: bool = False,
                                     route_selection: str = "dynamic_select",
                                     geo_delay: float = 0,
                                     extra_rtt_ms: int = 0) -> Dict[str, Any]:
        """
        处理API访问任务
        
        Args:
            api_tasks: API访问任务列表
            force_read_mode: 是否强制只读模式
            route_selection: 路线选择策略 (dynamic_select | direct | wasm | program | stepwise)
            geo_delay: 地理延迟时间（秒），默认0.1秒
            extra_rtt_ms: 每次 MCP / 单次 Wasm HTTP 请求前附加的 RTT（毫秒），默认 0
            
        Returns:
            处理结果
        """
        try:
            logger.info(f"开始处理 {len(api_tasks)} 个API访问任务")
            
            # 打印参数详情
            print(
                f"[InvocationScheduler] force_read_mode: {force_read_mode}, "
                f"route_selection: {route_selection}, extra_rtt_ms: {extra_rtt_ms}"
            )
            
            rs_raw = route_selection or "dynamic_select"
            mapped_rs = self._map_route_selection(rs_raw)

            # 转换为APIAccessTask对象
            tasks = []
            for task_data in api_tasks:
                task = APIAccessTask(
                    user_input=task_data.get("user_input", ""),
                    api_interface=task_data.get("api_interface", ""),
                    mcp_tool_name=task_data.get("mcp_tool_name", ""),
                    parameters=task_data.get("parameters", []),
                    expected_calls=task_data.get("expected_calls", 1),
                    has_dependency=task_data.get("has_dependency", False),
                    dependency_api=task_data.get("dependency_api")
                )
                tasks.append(task)
            
            # 获取全局开销统计器的当前数据（执行前）
            pre_execution_stats = self._get_current_global_stats()
            
            # 选择执行路线
            route = self._select_execution_route(tasks, mapped_rs)
            logger.info(f"选择的执行路线: {route} (请求 route_selection={rs_raw})")
            
            wasm_fallback_to_direct = False
            # 执行任务
            if route == "direct":
                result = await self._execute_direct_api_route(
                    tasks, geo_delay, extra_rtt_ms=extra_rtt_ms
                )
            elif route == "wasm":
                result = await self._execute_wasm_route(
                    tasks, force_read_mode, geo_delay, extra_rtt_ms=extra_rtt_ms
                )
                if mapped_rs == "dynamic_select" and not result.success:
                    logger.warning(
                        "Wasm 路线失败，dynamic_select 下自动改走 Direct（并递增 mode_switch_count）"
                    )
                    wasm_fallback_to_direct = True
                    result = await self._execute_direct_api_route(
                        tasks, geo_delay, extra_rtt_ms=extra_rtt_ms
                    )
            else:
                raise ValueError(f"未知的执行路线: {route}")
            
            # 获取全局开销统计器的更新后数据（执行后）
            post_execution_stats = self._get_current_global_stats()
            
            # 计算差值并更新性能跟踪器（以最终实际路线为准）
            perf_route = result.route_used or route
            self._update_performance_from_global_stats(pre_execution_stats, post_execution_stats, perf_route, result)
            
            logger.info(
                "任务执行完成，初选用路线: %s，最终 route_used=%s，成功: %s",
                route,
                getattr(result, "route_used", ""),
                result.success,
            )
            
            # 计算统计数据差值
            validation_duration = getattr(result, 'validation_duration', 0.0)
            validation_request_bytes = getattr(result, 'validation_request_bytes', 0)
            validation_response_bytes = getattr(result, 'validation_response_bytes', 0)
            stats_diff = self._calculate_stats_diff(
                pre_execution_stats, post_execution_stats, geo_delay,
                validation_duration, validation_request_bytes, validation_response_bytes, result
            )
            
            mode_switch_count = 1 if mapped_rs == "dynamic_select" else 0
            if wasm_fallback_to_direct:
                mode_switch_count += 1
            selected_mode = self._route_used_to_selected_mode(result.route_used)

            return {
                "success": result.success,
                "result": result.result,
                "error": result.error,
                "execution_time": result.execution_time,
                "route_used": result.route_used,
                "api_calls_made": result.api_calls_made,
                "tasks_processed": len(tasks),
                "stats_diff": stats_diff,  # 添加统计数据差值
                "wasm_compile_stats": result.wasm_compile_stats,  # 添加Wasm编译阶段统计数据
                "wasm_api_stats": result.wasm_api_stats,  # 添加Wasm API阶段统计数据
                "configured_extra_rtt_ms": int(extra_rtt_ms or 0),
                "effective_rtt_ms": int(getattr(result, "effective_rtt_ms", 0) or 0),
                "selected_mode": selected_mode or getattr(result, "selected_mode", ""),
                "mode_switch_count": mode_switch_count,
            }
            
        except Exception as e:
            logger.error(f"处理API访问任务失败: {e}")
            return {
                "success": False,
                "error": f"处理任务失败: {str(e)}",
                "execution_time": 0.0,
                "route_used": "none",
                "api_calls_made": 0,
                "tasks_processed": len(api_tasks) if api_tasks else 0,
                "stats_diff": None,
                "wasm_compile_stats": None,
                "wasm_api_stats": None,
                "configured_extra_rtt_ms": int(extra_rtt_ms or 0),
                "effective_rtt_ms": 0,
                "selected_mode": "",
                "mode_switch_count": 0,
            }
    
    def _select_execution_route(self, tasks: List[APIAccessTask], route_selection: str = "dynamic_select") -> str:
        """
        选择执行路线
        
        Args:
            tasks: API访问任务列表
            route_selection: 路线选择策略 ("dynamic_select", "direct", "wasm")
            
        Returns:
            选择的路线 ("direct" 或 "wasm")
        """
        try:
            # 如果指定了强制路线选择，直接返回
            if route_selection == "direct":
                logger.info("强制选择Direct路线")
                return "direct"
            elif route_selection == "wasm":
                logger.info("强制选择Wasm路线")
                return "wasm"
            
            # 否则使用动态选择算法
            logger.info("使用动态选择算法")
            
            # 1. 检查是否有依赖关系
            has_dependency = any(task.has_dependency for task in tasks)
            if has_dependency:
                logger.info("检测到依赖关系，选择Wasm路线")
                return "wasm"
            
            # 2. 计算预计调用次数
            total_expected_calls = sum(task.expected_calls for task in tasks)
            logger.info(f"总预计调用次数: {total_expected_calls}")
            
            # 3. 获取性能预测（每次都重新从配置文件读取最新数据）
            performance_prediction = self._calculate_route_performance_from_file(total_expected_calls)
            
            # 4. 选择路线
            direct_avg_time = performance_prediction["direct_avg_time"]
            wasm_avg_time = performance_prediction["wasm_avg_time"]
            logger.info(f"  direct_avg_time: {direct_avg_time}")
            logger.info(f"  wasm_avg_time: {wasm_avg_time}")
            
            # 如果首次选择（时间为0），默认选择Wasm路线来获得初始数据
            if direct_avg_time == 0.0 and wasm_avg_time == 0.0:
                logger.info("首次选择，默认选择Wasm路线")
                return "wasm"
            
            # 如果只有Direct路线有数据
            if direct_avg_time > 0.0 and wasm_avg_time == 0.0:
                logger.info("只有Direct路线有数据，选择Direct路线")
                return "direct"
            
            # 如果只有Wasm路线有数据
            if direct_avg_time == 0.0 and wasm_avg_time > 0.0:
                logger.info("只有Wasm路线有数据，选择Wasm路线")
                return "wasm"
            
            # 比较时间选择路线
            if wasm_avg_time < direct_avg_time:
                logger.info(f"Wasm路线更快 ({wasm_avg_time:.3f}s < {direct_avg_time:.3f}s)，选择Wasm路线")
                return "wasm"
            else:
                logger.info(f"Direct路线更快 ({direct_avg_time:.3f}s < {wasm_avg_time:.3f}s)，选择Direct路线")
                return "direct"
                
        except Exception as e:
            logger.error(f"选择执行路线失败: {e}")
            # 默认选择Wasm路线
            return "wasm"
    
    async def _execute_direct_api_route(
        self,
        tasks: List[APIAccessTask],
        geo_delay: float = 0,
        extra_rtt_ms: int = 0,
    ) -> ExecutionResult:
        """
        执行Direct API Access路线
        
        Args:
            tasks: API访问任务列表
            geo_delay: 地理延迟时间（秒），默认0.1秒
            
        Returns:
            执行结果
        """
        # 开始invocation-scheduler-direct-server阶段统计
        start_time = start_stage_tracking("invocation_scheduler_direct_server")
        
        execution_start_time = time.time()
        api_calls_made = 0
        total_request_bytes = 0
        total_response_bytes = 0
        agent_instance = None
        extra_rtt_total_ms = 0
        # 响应验证的流量和时间跟踪
        validation_request_bytes = 0
        validation_response_bytes = 0
        validation_duration = 0.0
        
        try:
            logger.info(f"开始执行Direct API路线，任务数量: {len(tasks)}")
            
            # 初始化SessionManager实例
            self.session_manager = await self._create_session_manager()
            if not self.session_manager:
                logger.error("创建SessionManager实例失败")
                return ExecutionResult(
                    success=False,
                    error="创建SessionManager实例失败",
                    execution_time=time.time() - execution_start_time,
                    route_used="direct",
                    api_calls_made=0,
                    configured_extra_rtt_ms=int(extra_rtt_ms or 0),
                    effective_rtt_ms=0,
                    selected_mode="stepwise",
                )
            
            # 创建agent实例用于响应验证
            agent_instance = await self._create_agent_instance()
            if not agent_instance:
                logger.warning("创建agent实例失败，将跳过响应验证")
            
            results = []
            
            # 逐个处理任务
            for task in tasks:
                logger.info(f"处理任务: {task.api_interface}, 预计调用次数: {task.expected_calls}")
                
                # 根据expected_calls重复执行
                for call_index in range(task.expected_calls):
                    logger.info(f"执行第 {call_index + 1}/{task.expected_calls} 次调用")
                    
                    # 处理每个参数集合
                    for param_set in task.parameters:
                        try:
                            # 计算请求字节数
                            request_bytes = len(json.dumps(param_set).encode('utf-8'))
                            total_request_bytes += request_bytes
                            
                            extra_rtt_total_ms += await self._sleep_extra_rtt_ms(int(extra_rtt_ms or 0))
                            # 调用MCP工具
                            result = await self._call_mcp_tool(task.mcp_tool_name, param_set)
                            
                            # 验证响应结果
                            if agent_instance:
                                try:
                                    validation_start_time = time.time()
                                    
                                    # 计算验证请求的字节数（工具名称 + 参数 + 响应结果）
                                    validation_request_data = {
                                        "tool_name": task.mcp_tool_name,
                                        "parameters": param_set,
                                        "response": result
                                    }
                                    validation_req_bytes = len(json.dumps(validation_request_data).encode('utf-8'))
                                    validation_request_bytes += validation_req_bytes
                                    
                                    validation_result = await agent_instance.validate_mcp_response(
                                        task.mcp_tool_name, param_set, result
                                    )
                                    
                                    # 计算验证响应字节数和时间
                                    validation_resp_bytes = len(json.dumps(validation_result).encode('utf-8'))
                                    validation_response_bytes += validation_resp_bytes
                                    validation_duration += time.time() - validation_start_time
                                    
                                    if validation_result != "ok":
                                        print("调用结果出错")
                                        logger.warning(f"MCP工具 {task.mcp_tool_name} 响应验证失败")
                                except Exception as e:
                                    logger.error(f"响应验证过程中出错: {e}")
                            
                            # 计算响应字节数
                            response_bytes = len(json.dumps(result).encode('utf-8'))
                            total_response_bytes += response_bytes
                            
                            results.append(result)
                            api_calls_made += 1
                            
                            logger.info(f"MCP工具调用成功: {task.mcp_tool_name} (第{call_index + 1}次)")
                            
                        except Exception as e:
                            logger.error(f"MCP工具调用失败: {task.mcp_tool_name} (第{call_index + 1}次), 错误: {e}")
                            error_result = {
                                "success": False,
                                "error": f"MCP工具调用失败: {str(e)}",
                                "call_index": call_index + 1
                            }
                            # 计算错误响应的字节数
                            error_response_bytes = len(json.dumps(error_result).encode('utf-8'))
                            total_response_bytes += error_response_bytes
                            
                            results.append(error_result)
                            api_calls_made += 1
            
            execution_time = time.time() - execution_start_time
            
            # 结束invocation-scheduler-direct-server阶段统计
            # 传入实际的MCP工具调用次数乘以2作为count_increment
            end_stage_tracking("invocation_scheduler_direct_server", start_time, total_request_bytes, total_response_bytes, api_calls_made * 2)
            
            return ExecutionResult(
                success=True,
                result=results,
                execution_time=execution_time,
                route_used="direct",
                api_calls_made=api_calls_made,
                validation_duration=validation_duration,
                validation_request_bytes=validation_request_bytes,
                validation_response_bytes=validation_response_bytes,
                configured_extra_rtt_ms=int(extra_rtt_ms or 0),
                effective_rtt_ms=int(extra_rtt_total_ms),
                selected_mode="stepwise",
            )
            
        except Exception as e:
            execution_time = time.time() - execution_start_time 
            logger.error(f"Direct API路线执行失败: {e}")
            
            # 即使出错也要结束统计，传入已完成的MCP工具调用次数乘以2
            end_stage_tracking("invocation_scheduler_direct_server", start_time, total_request_bytes, total_response_bytes, api_calls_made * 2)
            
            return ExecutionResult(
                success=False,
                error=f"Direct API路线执行失败: {str(e)}",
                execution_time=execution_time,
                route_used="direct",
                api_calls_made=api_calls_made,
                configured_extra_rtt_ms=int(extra_rtt_ms or 0),
                effective_rtt_ms=int(extra_rtt_total_ms),
                selected_mode="stepwise",
            )
        finally:
            # 确保关闭SessionManager实例
            if self.session_manager:
                try:
                    await self.session_manager.shutdown()
                    logger.info("SessionManager实例已关闭")
                    self.session_manager = None
                except Exception as e:
                    logger.error(f"关闭SessionManager实例失败: {e}")
            
            # 确保关闭agent实例
            if agent_instance:
                try:
                    await agent_instance.shutdown()
                    logger.info("Agent实例已关闭")
                except Exception as e:
                    logger.error(f"关闭Agent实例失败: {e}")
    
    async def _execute_wasm_route(
        self,
        tasks: List[APIAccessTask],
        force_read_mode: bool = False,
        geo_delay: float = 0,
        extra_rtt_ms: int = 0,
    ) -> ExecutionResult:
        """
        执行Custom API Access (Wasm)路线
        
        Args:
            tasks: API访问任务列表
            force_read_mode: 是否强制只读模式
            geo_delay: 地理延迟时间（秒），默认0.1秒
            extra_rtt_ms: 单次 Wasm HTTP（/generate-code）请求前附加 RTT（毫秒）
            
        Returns:
            执行结果
        """
        start_time = time.time()
        extra_rtt_total_ms = 0
        
        try:
            logger.info(f"开始执行Wasm路线，任务数量: {len(tasks)}")
            
            # 打印参数详情
            print(f"[InvocationScheduler._execute_wasm_route] force_read_mode: {force_read_mode}")
            
            # 构建查询描述
            query_description = self._build_query_description(tasks)
            
            # 将API Access Tasks转换为字典格式
            api_tasks_data = []
            for task in tasks:
                api_tasks_data.append({
                    "user_input": task.user_input,
                    "api_interface": task.api_interface,
                    "mcp_tool_name": task.mcp_tool_name,
                    "parameters": task.parameters,
                    "expected_calls": task.expected_calls,
                    "has_dependency": task.has_dependency,
                    "dependency_api": task.dependency_api
                })
            
            extra_rtt_total_ms += await self._sleep_extra_rtt_ms(int(extra_rtt_ms or 0))

            # 直接调用 /generate-code 端点，传递API Access Tasks
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.client_service_url}/generate-code",
                    json={
                        "query": query_description,
                        "api_tasks": api_tasks_data,  # 传递API Access Tasks
                        "force_read_mode": force_read_mode,
                        "geo_delay": geo_delay  # 传递地理延迟参数
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    execution_time = time.time() - start_time
                    
                    return ExecutionResult(
                        success=result.get("success", False),
                        result=result.get("result"),
                        error=result.get("error"),
                        execution_time=execution_time,
                        route_used="wasm",
                        api_calls_made=len(tasks),  # 假设每个任务对应一次API调用
                        wasm_compile_stats=result.get("wasm_compile_stats"),
                        wasm_api_stats=result.get("wasm_api_stats"),
                        configured_extra_rtt_ms=int(extra_rtt_ms or 0),
                        effective_rtt_ms=int(extra_rtt_total_ms),
                        selected_mode="program",
                    )
                else:
                    execution_time = time.time() - start_time
                    return ExecutionResult(
                        success=False,
                        error=f"Wasm路线执行失败: HTTP {response.status_code} - {response.text}",
                        execution_time=execution_time,
                        route_used="wasm",
                        api_calls_made=0,
                        configured_extra_rtt_ms=int(extra_rtt_ms or 0),
                        effective_rtt_ms=int(extra_rtt_total_ms),
                        selected_mode="program",
                    )
                    
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Wasm路线执行失败: {e}")
            
            return ExecutionResult(
                success=False,
                error=f"Wasm路线执行失败: {str(e)}",
                execution_time=execution_time,
                route_used="wasm",
                api_calls_made=0,
                configured_extra_rtt_ms=int(extra_rtt_ms or 0),
                effective_rtt_ms=int(extra_rtt_total_ms),
                selected_mode="program",
            )
    
    async def _call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any], session_manager: Optional[SessionManager] = None) -> Dict[str, Any]:
        """
        调用MCP工具
        
        Args:
            tool_name: 工具名称
            parameters: 参数
            session_manager: SessionManager实例，如果为None则使用self.session_manager
            
        Returns:
            调用结果
        """
        try:
            # 使用传入的session_manager或self.session_manager
            manager = session_manager or self.session_manager
            if not manager:
                logger.error("SessionManager实例不可用")
                return {
                    "success": False,
                    "error": "SessionManager实例不可用"
                }
            
            # 使用SessionManager调用MCP工具
            # 根据配置文件，服务器名称是 "local_apis"
            result = await manager.call_tool("local_apis", tool_name, parameters)
            
            # 确保返回格式一致
            if isinstance(result, dict):
                return result
            else:
                return {
                    "success": True,
                    "result": result
                }
                    
        except Exception as e:
            logger.error(f"MCP工具调用失败: {tool_name}, 错误: {e}")
            return {
                "success": False,
                "error": f"MCP工具调用异常: {str(e)}"
            }
    
    def _get_current_global_stats(self) -> Dict[str, Any]:
        """
        获取当前全局开销统计器的数据
        
        Returns:
            当前各阶段的统计数据
        """
        try:
            global_tracker = get_global_cost_tracker()
            stage_summary = global_tracker.get_stage_summary()
            
            # 提取我们需要的阶段数据
            stats = {}
            for stage_name in ["invocation_scheduler_llm", "invocation_scheduler_direct_server", 
                             "invocation_scheduler_wasm_server", "wasm_compile", "wasm_api"]:
                if stage_name in stage_summary:
                    stats[stage_name] = {
                        "total_duration": stage_summary[stage_name]["total_duration"],
                        "count": stage_summary[stage_name]["count"],
                        "total_request_bytes": stage_summary[stage_name]["total_request_bytes"],
                        "total_response_bytes": stage_summary[stage_name]["total_response_bytes"],
                        "total_bytes": stage_summary[stage_name]["total_bytes"]
                    }
                else:
                    stats[stage_name] = {
                        "total_duration": 0.0, 
                        "count": 0,
                        "total_request_bytes": 0,
                        "total_response_bytes": 0,
                        "total_bytes": 0
                    }
            
            logger.info(f"获取当前全局统计数据: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"获取全局统计数据失败: {e}")
            return {
                "invocation_scheduler_llm": {"total_duration": 0.0, "count": 0, "total_request_bytes": 0, "total_response_bytes": 0, "total_bytes": 0},
                "invocation_scheduler_direct_server": {"total_duration": 0.0, "count": 0, "total_request_bytes": 0, "total_response_bytes": 0, "total_bytes": 0},
                "invocation_scheduler_wasm_server": {"total_duration": 0.0, "count": 0, "total_request_bytes": 0, "total_response_bytes": 0, "total_bytes": 0},
                "wasm_compile": {"total_duration": 0.0, "count": 0, "total_request_bytes": 0, "total_response_bytes": 0, "total_bytes": 0},
                "wasm_api": {"total_duration": 0.0, "count": 0, "total_request_bytes": 0, "total_response_bytes": 0, "total_bytes": 0}
            }
    
    def _calculate_stats_diff(self, pre_stats: Dict[str, Any], post_stats: Dict[str, Any], geo_delay: float = 0, 
                             validation_duration: float = 0.0, validation_request_bytes: int = 0, 
                             validation_response_bytes: int = 0, execution_result: Optional[ExecutionResult] = None) -> Dict[str, Any]:
        """
        计算统计数据差值
        
        Args:
            pre_stats: 执行前的统计数据
            post_stats: 执行后的统计数据
            geo_delay: 地理延迟时间（秒），默认0秒
            validation_duration: 响应验证的总时间开销
            validation_request_bytes: 响应验证的总请求字节数
            validation_response_bytes: 响应验证的总响应字节数
            
        Returns:
            统计数据差值
        """
        try:
            stats_diff = {}
            
            # 计算各阶段的差值
            for stage_name in ["invocation_scheduler_llm", "invocation_scheduler_direct_server", 
                             "invocation_scheduler_wasm_server", "wasm_compile", "wasm_api"]:
                
                # 对于wasm_compile和wasm_api阶段，优先使用execution_result中的数据
                if stage_name in ["wasm_compile", "wasm_api"] and execution_result:
                    if stage_name == "wasm_compile" and execution_result.wasm_compile_stats:
                        # 使用响应中的编译阶段统计数据
                        stage_stats = execution_result.wasm_compile_stats
                        base_duration_diff = stage_stats.get("total_duration", 0.0)
                        count_diff = stage_stats.get("count", 0)
                        base_request_bytes_diff = stage_stats.get("total_request_bytes", 0)
                        base_response_bytes_diff = stage_stats.get("total_response_bytes", 0)
                        base_total_bytes_diff = stage_stats.get("total_bytes", 0)
                        logger.info(f"使用响应中的{stage_name}统计数据: 时间={base_duration_diff:.3f}s, 次数={count_diff}")
                    elif stage_name == "wasm_api" and execution_result.wasm_api_stats:
                        # 使用响应中的API阶段统计数据
                        stage_stats = execution_result.wasm_api_stats
                        base_duration_diff = stage_stats.get("total_duration", 0.0)
                        count_diff = stage_stats.get("count", 0)
                        base_request_bytes_diff = stage_stats.get("total_request_bytes", 0)
                        base_response_bytes_diff = stage_stats.get("total_response_bytes", 0)
                        base_total_bytes_diff = stage_stats.get("total_bytes", 0)
                        logger.info(f"使用响应中的{stage_name}统计数据: 时间={base_duration_diff:.3f}s, 次数={count_diff}")
                    else:
                        # 回退到全局统计器（可能为0）
                        pre_duration = pre_stats.get(stage_name, {}).get("total_duration", 0.0)
                        post_duration = post_stats.get(stage_name, {}).get("total_duration", 0.0)
                        pre_count = pre_stats.get(stage_name, {}).get("count", 0)
                        post_count = post_stats.get(stage_name, {}).get("count", 0)
                        pre_request_bytes = pre_stats.get(stage_name, {}).get("total_request_bytes", 0)
                        post_request_bytes = post_stats.get(stage_name, {}).get("total_request_bytes", 0)
                        pre_response_bytes = pre_stats.get(stage_name, {}).get("total_response_bytes", 0)
                        post_response_bytes = post_stats.get(stage_name, {}).get("total_response_bytes", 0)
                        pre_total_bytes = pre_stats.get(stage_name, {}).get("total_bytes", 0)
                        post_total_bytes = post_stats.get(stage_name, {}).get("total_bytes", 0)
                        
                        base_duration_diff = post_duration - pre_duration
                        count_diff = post_count - pre_count
                        base_request_bytes_diff = post_request_bytes - pre_request_bytes
                        base_response_bytes_diff = post_response_bytes - pre_response_bytes
                        base_total_bytes_diff = post_total_bytes - pre_total_bytes
                        logger.warning(f"回退到全局统计器获取{stage_name}数据: 时间={base_duration_diff:.3f}s, 次数={count_diff}")
                else:
                    # 其他阶段使用全局统计器
                    pre_duration = pre_stats.get(stage_name, {}).get("total_duration", 0.0)
                    post_duration = post_stats.get(stage_name, {}).get("total_duration", 0.0)
                    pre_count = pre_stats.get(stage_name, {}).get("count", 0)
                    post_count = post_stats.get(stage_name, {}).get("count", 0)
                    pre_request_bytes = pre_stats.get(stage_name, {}).get("total_request_bytes", 0)
                    post_request_bytes = post_stats.get(stage_name, {}).get("total_request_bytes", 0)
                    pre_response_bytes = pre_stats.get(stage_name, {}).get("total_response_bytes", 0)
                    post_response_bytes = post_stats.get(stage_name, {}).get("total_response_bytes", 0)
                    pre_total_bytes = pre_stats.get(stage_name, {}).get("total_bytes", 0)
                    post_total_bytes = post_stats.get(stage_name, {}).get("total_bytes", 0)
                    
                    base_duration_diff = post_duration - pre_duration
                    count_diff = post_count - pre_count
                    base_request_bytes_diff = post_request_bytes - pre_request_bytes
                    base_response_bytes_diff = post_response_bytes - pre_response_bytes
                    base_total_bytes_diff = post_total_bytes - pre_total_bytes
                
                # 为invocation_scheduler_direct_server和invocation_scheduler_wasm_server阶段添加地理延迟
                commontime = 0.0
                if stage_name in ["invocation_scheduler_direct_server", "invocation_scheduler_wasm_server"] and geo_delay > 0:
                    geo_delay_adjustment = geo_delay * count_diff 
                    duration_diff = base_duration_diff + geo_delay_adjustment
                    commontime = geo_delay_adjustment
                    logger.info(f"{stage_name}阶段添加地理延迟: {geo_delay_adjustment:.3f}s (geo_delay={geo_delay}, count_diff={count_diff})")
                else:
                    duration_diff = base_duration_diff
                
                # 调整响应验证时间开销
                if stage_name == "invocation_scheduler_direct_server":
                    # 从direct_server中减去响应验证的时间开销
                    duration_diff -= validation_duration
                    request_bytes_diff = base_request_bytes_diff
                    response_bytes_diff = base_response_bytes_diff
                    total_bytes_diff = base_total_bytes_diff
                    logger.info(f"从direct_server中减去响应验证时间开销: -{validation_duration:.3f}s")
                elif stage_name == "invocation_scheduler_llm":
                    # 将响应验证的时间开销和流量开销加到llm中
                    duration_diff += validation_duration
                    request_bytes_diff = base_request_bytes_diff + validation_request_bytes
                    response_bytes_diff = base_response_bytes_diff + validation_response_bytes
                    total_bytes_diff = base_total_bytes_diff + (validation_request_bytes + validation_response_bytes)
                    logger.info(f"将响应验证开销加到llm: 时间+{validation_duration:.3f}s, 请求字节+{validation_request_bytes}, 响应字节+{validation_response_bytes}")
                else:
                    # 其他阶段保持不变
                    request_bytes_diff = base_request_bytes_diff
                    response_bytes_diff = base_response_bytes_diff
                    total_bytes_diff = base_total_bytes_diff
                
                stats_diff[stage_name] = {
                    "duration_diff": duration_diff,
                    "count_diff": count_diff,
                    "request_bytes_diff": request_bytes_diff,
                    "response_bytes_diff": response_bytes_diff,
                    "total_bytes_diff": total_bytes_diff,
                    "commontime": commontime
                }
            
            # 计算汇总统计数据
            total_llm_bytes = (stats_diff.get("invocation_scheduler_llm", {}).get("total_bytes_diff", 0))
            total_communication_bytes = (stats_diff.get("invocation_scheduler_direct_server", {}).get("total_bytes_diff", 0) + 
                                       stats_diff.get("invocation_scheduler_wasm_server", {}).get("total_bytes_diff", 0))
            total_bytes = total_llm_bytes + total_communication_bytes
            
            total_llm_time = stats_diff.get("invocation_scheduler_llm", {}).get("duration_diff", 0.0)
            total_communication_time = (stats_diff.get("invocation_scheduler_direct_server", {}).get("duration_diff", 0.0) + 
                                      stats_diff.get("invocation_scheduler_wasm_server", {}).get("duration_diff", 0.0))
            total_time = total_llm_time + total_communication_time
            
            # 计算总的端到端延迟（commontime）
            total_commontime = 0.0
            for stage_name in ["invocation_scheduler_direct_server", "invocation_scheduler_wasm_server"]:
                if stage_name in stats_diff:
                    stage_commontime = stats_diff[stage_name].get("commontime", 0.0)
                    total_commontime += stage_commontime
            
            stats_diff["summary"] = {
                "total_bytes": total_bytes,
                "total_llm_bytes": total_llm_bytes,
                "total_communication_bytes": total_communication_bytes,
                "total_time": total_time,
                "total_llm_time": total_llm_time,
                "total_communication_time": total_communication_time,
                "commontime": total_commontime
            }
            
            logger.info(f"计算统计数据差值: {stats_diff}")
            return stats_diff
            
        except Exception as e:
            logger.error(f"计算统计数据差值失败: {e}")
            return {}
    
    def _update_performance_from_global_stats(self, pre_stats: Dict[str, Any], 
                                            post_stats: Dict[str, Any], route: str,
                                            execution_result: Optional[ExecutionResult] = None):
        """
        根据全局统计数据的前后差值更新性能跟踪器
        
        Args:
            pre_stats: 执行前的统计数据
            post_stats: 执行后的统计数据
            route: 执行的路线 ("direct" 或 "wasm")
            execution_result: 执行结果，包含从响应中获取的统计数据
        """
        try:
            if route == "direct":
                # Direct路线：更新mcp_direct_call_time和direct_call_count
                direct_duration_diff = (post_stats["invocation_scheduler_direct_server"]["total_duration"] - 
                                      pre_stats["invocation_scheduler_direct_server"]["total_duration"])
                direct_count_diff = (post_stats["invocation_scheduler_direct_server"]["count"] - 
                                   pre_stats["invocation_scheduler_direct_server"]["count"])
                
                if direct_duration_diff > 0 or direct_count_diff > 0:
                    # 使用原有的更新方法，但传入的是差值
                    self.performance_tracker.update_direct_api_performance(direct_duration_diff, direct_count_diff)
                    logger.info(f"Direct路线性能更新: 时间+{direct_duration_diff:.3f}s, 次数+{direct_count_diff}")
                
            elif route == "wasm":
                # Wasm路线：更新wasm相关数据
                llm_duration_diff = (post_stats["invocation_scheduler_llm"]["total_duration"] - 
                                   pre_stats["invocation_scheduler_llm"]["total_duration"])
                llm_count_diff = (post_stats["invocation_scheduler_llm"]["count"] - 
                                pre_stats["invocation_scheduler_llm"]["count"])
                
                # 优先使用从响应中获取的编译阶段统计数据
                if execution_result and execution_result.wasm_compile_stats:
                    compile_duration_diff = execution_result.wasm_compile_stats.get("total_duration", 0.0)
                    compile_count_diff = execution_result.wasm_compile_stats.get("count", 0)
                    logger.info(f"使用响应中的编译阶段统计数据: 时间={compile_duration_diff:.3f}s, 次数={compile_count_diff}")
                else:
                    # 回退到从全局统计器获取（可能为0）
                    compile_duration_diff = (post_stats["wasm_compile"]["total_duration"] - 
                                           pre_stats["wasm_compile"]["total_duration"])
                    compile_count_diff = (post_stats["wasm_compile"]["count"] - 
                                        pre_stats["wasm_compile"]["count"])
                    logger.warning(f"回退到全局统计器获取编译阶段数据: 时间={compile_duration_diff:.3f}s, 次数={compile_count_diff}")
                
                # 优先使用从响应中获取的API阶段统计数据
                if execution_result and execution_result.wasm_api_stats:
                    wasm_api_duration_diff = execution_result.wasm_api_stats.get("total_duration", 0.0)
                    wasm_api_count_diff = execution_result.wasm_api_stats.get("count", 0)
                    logger.info(f"使用响应中的API阶段统计数据: 时间={wasm_api_duration_diff:.3f}s, 次数={wasm_api_count_diff}")
                else:
                    # 回退到从全局统计器获取（可能为0）
                    wasm_api_duration_diff = (post_stats["wasm_api"]["total_duration"] - 
                                            pre_stats["wasm_api"]["total_duration"])
                    wasm_api_count_diff = (post_stats["wasm_api"]["count"] - 
                                         pre_stats["wasm_api"]["count"])
                    logger.warning(f"回退到全局统计器获取API阶段数据: 时间={wasm_api_duration_diff:.3f}s, 次数={wasm_api_count_diff}")
                
                wasm_server_duration_diff = (post_stats["invocation_scheduler_wasm_server"]["total_duration"] - 
                                           pre_stats["invocation_scheduler_wasm_server"]["total_duration"])
                wasm_server_count_diff = (post_stats["invocation_scheduler_wasm_server"]["count"] - 
                                        pre_stats["invocation_scheduler_wasm_server"]["count"])
                
                # 计算wasm_call_time：wasm_server总时间减去compile时间再减去wasm_api时间，为了与direct线路中的时间开销对齐，加上一次api调用平均实际时间
                if wasm_api_count_diff > 0:
                    wasm_call_time_diff = wasm_server_duration_diff - compile_duration_diff 
                    - wasm_api_duration_diff + wasm_api_duration_diff / wasm_api_count_diff
                else:
                    # 当API调用次数为0时，不进行除法运算，避免除零错误
                    wasm_call_time_diff = wasm_server_duration_diff - compile_duration_diff - wasm_api_duration_diff
                    logger.warning(f"API调用次数为0，跳过除法运算: wasm_api_count_diff={wasm_api_count_diff}, wasm_api_duration_diff={wasm_api_duration_diff:.3f}s")
                
                if (llm_duration_diff > 0 or llm_count_diff > 0 or 
                    compile_duration_diff > 0 or compile_count_diff > 0 or 
                    wasm_api_duration_diff > 0 or wasm_api_count_diff > 0 or
                    wasm_call_time_diff > 0 or wasm_server_count_diff > 0):
                    
                    # 使用原有的更新方法，但传入的是差值
                    self.performance_tracker.update_wasm_performance(
                        llm_duration_diff,      # wasm_generate_time
                        compile_duration_diff,  # wasm_compilation_time
                        wasm_call_time_diff,    # wasm_call_time
                        llm_count_diff,         # wasm_generate_count
                        compile_count_diff,     # wasm_compilation_count
                        wasm_server_count_diff  # wasm_call_count
                    )
                    logger.info(f"Wasm路线性能更新: 生成+{llm_duration_diff:.3f}s, 编译+{compile_duration_diff:.3f}s, API+{wasm_api_duration_diff:.3f}s, 调用+{wasm_call_time_diff:.3f}s")
                    logger.info(f"Wasm路线计数更新: 生成+{llm_count_diff}, 编译+{compile_count_diff}, API+{wasm_api_count_diff}, 调用+{wasm_server_count_diff}")
            
        except Exception as e:
            logger.error(f"根据全局统计数据更新性能跟踪器失败: {e}")
    
    def _calculate_route_performance_from_file(self, expected_calls: int) -> Dict[str, Any]:
        """
        直接从配置文件读取数据并计算路线性能预测
        
        Args:
            expected_calls: 预计调用次数
            
        Returns:
            包含性能预测的字典
        """
        try:
            # 直接从配置文件读取数据
            config_file = self.performance_tracker.config_file
            if not os.path.exists(config_file):
                logger.warning(f"配置文件不存在: {config_file}，使用默认值")
                return self._get_default_performance_prediction(expected_calls)
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            perf_data = config.get("performance_data", {})
            threshold = config.get("threshold", 100)
            buffer_factor = config.get("buffer_factor", 0.4)
            
            logger.info(f"从配置文件读取性能数据: {perf_data}")
            
            # 计算置信度
            direct_confidence = min(1.0, (perf_data.get("direct_call_count", 0) + perf_data.get("wasm_call_count", 0)) / threshold)
            wasm_confidence = min(1.0, (
                perf_data.get("wasm_compilation_count", 0) +
                perf_data.get("wasm_generate_count", 0)
            ) / threshold)
            
            # 计算平均通信时间
            total_calls = perf_data.get("direct_call_count", 0) + perf_data.get("wasm_call_count", 0)
            if total_calls > 0:
                avg_communication_time = (perf_data.get("mcp_direct_call_time", 0.0) + perf_data.get("wasm_call_time", 0.0)) / total_calls
            else:
                avg_communication_time = 0.0
            
            # 处理expected_calls的特殊情况
            if expected_calls < 1:
                logger.error(f"无效的预期调用次数: {expected_calls}，必须大于等于1")
                return self._get_default_performance_prediction(expected_calls)
            
            # 直接计算direct_avg_time
            direct_avg_time = avg_communication_time * 2 * expected_calls * (1 + (1 - direct_confidence) * buffer_factor)
            
            # 直接计算wasm_avg_time
            wasm_generate_count = max(perf_data.get("wasm_generate_count", 0), 1)
            wasm_compilation_count = max(perf_data.get("wasm_compilation_count", 0), 1)
            
            wasm_avg_time = (
                perf_data.get("wasm_generate_time", 0.0) / wasm_generate_count +
                perf_data.get("wasm_compilation_time", 0.0) / wasm_compilation_count +
                avg_communication_time
            ) * (1 + (1 - wasm_confidence) * buffer_factor)
            
            result = {
                "direct_confidence": direct_confidence,
                "wasm_confidence": wasm_confidence,
                "avg_communication_time": avg_communication_time,
                "direct_avg_time": direct_avg_time,
                "wasm_avg_time": wasm_avg_time,
                "expected_calls": expected_calls,
                "performance_data": perf_data.copy()
            }
            
            logger.info(f"性能预测计算完成（从文件读取）:")
            logger.info(f"  Direct置信度: {direct_confidence:.3f}, 预计时间: {direct_avg_time:.3f}s")
            logger.info(f"  Wasm置信度: {wasm_confidence:.3f}, 预计时间: {wasm_avg_time:.3f}s")
            logger.info(f"  平均通信时间: {avg_communication_time:.3f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"从文件计算路线性能失败: {e}")
            return self._get_default_performance_prediction(expected_calls)
    
    def _get_default_performance_prediction(self, expected_calls: int) -> Dict[str, Any]:
        """
        获取默认的性能预测（当配置文件不存在或读取失败时）
        
        Args:
            expected_calls: 预计调用次数
            
        Returns:
            默认的性能预测字典
        """
        return {
            "direct_confidence": 0.0,
            "wasm_confidence": 0.0,
            "avg_communication_time": 0.0,
            "direct_avg_time": 0.0,
            "wasm_avg_time": 0.0,
            "expected_calls": expected_calls,
            "performance_data": {}
        }
    
    def _build_query_description(self, tasks: List[APIAccessTask]) -> str:
        """
        构建查询描述
        
        Args:
            tasks: API访问任务列表
            
        Returns:
            查询描述
        """
        descriptions = []
        
        for task in tasks:
            if task.has_dependency:
                descriptions.append(f"先{task.user_input}，然后使用结果进行后续操作")
            else:
                descriptions.append(task.user_input)
        
        return "；".join(descriptions)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息（从配置文件读取最新数据）"""
        try:
            # 直接从配置文件读取数据
            config_file = self.performance_tracker.config_file
            if not os.path.exists(config_file):
                logger.warning(f"配置文件不存在: {config_file}")
                return {}
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            perf_data = config.get("performance_data", {})
            threshold = config.get("threshold", 100)
            buffer_factor = config.get("buffer_factor", 0.4)
            
            stats = {
                "threshold": threshold,
                "buffer_factor": buffer_factor,
                "direct_api": {
                    "total_time": perf_data.get("mcp_direct_call_time", 0.0),
                    "call_count": perf_data.get("direct_call_count", 0),
                    "avg_time": perf_data.get("mcp_direct_call_time", 0.0) / max(perf_data.get("direct_call_count", 0), 1)
                },
                "wasm_api": {
                    "generate_time": perf_data.get("wasm_generate_time", 0.0),
                    "compilation_time": perf_data.get("wasm_compilation_time", 0.0),
                    "call_time": perf_data.get("wasm_call_time", 0.0),
                    "generate_count": perf_data.get("wasm_generate_count", 0),
                    "compilation_count": perf_data.get("wasm_compilation_count", 0),
                    "call_count": perf_data.get("wasm_call_count", 0),
                    "avg_generate_time": perf_data.get("wasm_generate_time", 0.0) / max(perf_data.get("wasm_generate_count", 0), 1),
                    "avg_compilation_time": perf_data.get("wasm_compilation_time", 0.0) / max(perf_data.get("wasm_compilation_count", 0), 1),
                    "avg_call_time": perf_data.get("wasm_call_time", 0.0) / max(perf_data.get("wasm_call_count", 0), 1)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"从文件获取性能统计失败: {e}")
            return {}
    
    def reset_performance_data(self):
        """重置性能数据"""
        self.performance_tracker.reset_performance_data()
    
    def update_config(self, threshold: Optional[int] = None, buffer_factor: Optional[float] = None):
        """更新配置参数"""
        self.performance_tracker.update_config(threshold, buffer_factor)
    
    async def shutdown(self):
        """关闭调度器"""
        try:
            # 确保关闭任何可能存在的SessionManager实例
            if self.session_manager:
                await self.session_manager.shutdown()
                self.session_manager = None
                logger.info("SessionManager实例已关闭")
            logger.info("调用调度器已关闭")
        except Exception as e:
            logger.error(f"关闭调度器失败: {e}")