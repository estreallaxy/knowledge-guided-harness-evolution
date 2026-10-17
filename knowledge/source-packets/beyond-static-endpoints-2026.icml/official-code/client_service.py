"""
ToolPro Client 服务
负责自然语言到 Rust 代码的生成，运行在端口 8000
"""

import asyncio
import json
import httpx
import logging
import os
import time
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import uvicorn

# 加载环境配置
from dotenv import load_dotenv
load_dotenv()

# 根据环境变量设置日志级别
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

from client.client_code_generator import ClientCodeGenerator
from client.invocation_scheduler import InvocationScheduler
from core.global_cost_tracker import get_global_cost_tracker, start_stage_tracking, end_stage_tracking
from core.path_utils import PathUtils
from config import Config

# 配置
CLIENT_PORT = Config.CLIENT_PORT
SERVER_URL = Config.SERVER_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("Client 服务启动中...")
    
    # 重置全局开销统计器
    try:
        from core.global_cost_tracker import reset_global_cost_tracker
        reset_global_cost_tracker()
        logger.info("全局开销统计器已重置")
    except Exception as e:
        logger.warning(f"重置全局开销统计器失败: {e}")
    
    yield
    # 关闭时清理
    logger.info("Client 服务关闭中...")
    
    # 打印最终统计摘要
    try:
        from core.global_cost_tracker import print_stats_summary
        print_stats_summary()
    except Exception as e:
        logger.warning(f"打印统计摘要失败: {e}")

app = FastAPI(
    title="ToolPro Client Service",
    description="动态生成 Rust 代码的客户端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 初始化客户端代码生成器
client_code_generator = ClientCodeGenerator()

# 初始化调用调度器
invocation_scheduler = InvocationScheduler()

class NetworkOperationResponse(BaseModel):
    """网络操作响应模型"""
    operation_type: str
    api_call: str
    line_number: int
    url: str
    method: str
    sequence_number: int
    expected_impact: str

class GenerateCodeRequest(BaseModel):
    query: str
    llm_config: Optional[Dict[str, str]] = None
    force_read_mode: Optional[bool] = False
    api_tasks: Optional[List[Dict[str, Any]]] = None  # 新增API Access Tasks字段
    geo_delay: Optional[float] = 0  # 地理延迟参数，默认0秒

class GenerateCodeResponse(BaseModel):
    success: bool
    source_code: Optional[str] = None
    semantic_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_id: Optional[str] = None
    # 新增编译执行相关字段
    result: Optional[Any] = None
    debug_info: Optional[Dict[str, Any]] = None
    execution_mode: Optional[str] = None
    strategy: Optional[str] = None
    network_operations: Optional[List[NetworkOperationResponse]] = None
    api_traffic_stats: Optional[Dict[str, Any]] = None
    # 修改WASM流量统计字段（只包含请求流量）
    wasm_traffic_stats: Optional[Dict[str, Any]] = None
    # 新增LLM流量统计字段
    llm_traffic_stats: Optional[Dict[str, Any]] = None
    # 新增编译阶段和API阶段统计数据
    wasm_compile_stats: Optional[Dict[str, Any]] = None
    wasm_api_stats: Optional[Dict[str, Any]] = None
    replay_allow_nondeterministic_writes: Optional[bool] = None
    fallback_triggered: Optional[bool] = None
    fallback_reason: Optional[str] = None
    fallback_to_stepwise_success: Optional[bool] = None
    final_mode: Optional[str] = None

class CompileExecuteRequest(BaseModel):
    source_code: str
    semantic_info: Dict[str, Any]
    input_data: str
    user_query: Optional[str] = None
    geo_delay: Optional[float] = 0  # 地理延迟参数，默认0秒
    force_read_mode: Optional[bool] = False
    replay: Optional[str] = "on"
    fallback_policy: Optional[str] = "safe_stepwise"
    replay_conflict_policy: Optional[str] = "strict_prefix"
    repair_attempt_budget: Optional[int] = None
    intent_instance_id: Optional[str] = None

class CompileExecuteResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_id: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
    execution_mode: Optional[str] = None
    strategy: Optional[str] = None
    network_operations: Optional[List[NetworkOperationResponse]] = None
    intent_instance_id: Optional[str] = None
    replay_enabled: Optional[bool] = None
    fallback_policy: Optional[str] = None
    replay_conflict_policy: Optional[str] = None
    repair_attempt_budget: Optional[int] = None
    replay_allow_nondeterministic_writes: Optional[bool] = None
    fallback_triggered: Optional[bool] = None
    fallback_reason: Optional[str] = None
    fallback_to_stepwise_success: Optional[bool] = None
    final_mode: Optional[str] = None

class APIAccessTaskRequest(BaseModel):
    """API访问任务请求模型"""
    api_tasks: List[Dict[str, Any]]
    force_read_mode: Optional[bool] = False
    route_selection: Optional[str] = "dynamic_select"
    geo_delay: Optional[float] = 0  # 地理延迟参数，默认0秒
    extra_rtt_ms: Optional[int] = 0  # 每次 MCP 调用或单次 Wasm HTTP 前附加 RTT（毫秒）

class APIAccessTaskResponse(BaseModel):
    """API访问任务响应模型"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    route_used: str = ""
    api_calls_made: int = 0
    tasks_processed: int = 0
    stats_diff: Optional[Dict[str, Any]] = None  # 添加统计数据差值
    wasm_compile_stats: Optional[Dict[str, Any]] = None
    wasm_api_stats: Optional[Dict[str, Any]] = None
    configured_extra_rtt_ms: int = 0
    effective_rtt_ms: int = 0
    selected_mode: str = ""
    mode_switch_count: int = 0

class PerformanceStatsResponse(BaseModel):
    """性能统计响应模型"""
    threshold: int
    buffer_factor: float
    direct_api: Dict[str, Any]
    wasm_api: Dict[str, Any]


@app.get("/api")
async def api_root():
    """API根路径"""
    return {"message": "ToolPro Client Service is running", "server_url": SERVER_URL}

@app.post("/generate-code", response_model=GenerateCodeResponse)
async def generate_code(request: GenerateCodeRequest):
    """生成 Rust 代码并自动编译执行"""
    try:
        
        # 如果提供了LLM配置，更新客户端代码生成器的配置
        if request.llm_config:
            api_key = request.llm_config.get("apiKey", "")
            base_url = request.llm_config.get("baseUrl", "")
            model = request.llm_config.get("model", "")
            
            # 只有当API密钥不是占位符且不为空时才更新
            if api_key and api_key != "api-key":
                client_code_generator.set_llm_config(
                    api_key=api_key,
                    base_url=base_url or client_code_generator.llm_config["base_url"],
                    model=model or client_code_generator.llm_config["model"]
                )
        
        # 1. 调用客户端代码生成器（LLM交互阶段）
        # 开始invocation-scheduler-llm阶段统计
        start_time = start_stage_tracking("invocation_scheduler_llm")
        
        # 打印参数详情
        print(f"[ClientService.generate-code] force_read_mode: {request.force_read_mode}")
        
        code_result = await client_code_generator.generate_code_from_natural_language(
            query=request.query,
            force_read_mode=request.force_read_mode,
            api_tasks=request.api_tasks  # 传递API Access Tasks
        )
        
        # 结束invocation-scheduler-llm阶段统计
        # 计算请求和响应的字节数
        request_data = {
            "query": request.query,
            "force_read_mode": request.force_read_mode,
            "api_tasks": request.api_tasks
        }
        request_bytes = len(json.dumps(request_data).encode('utf-8'))
        
        response_data = {
            "success": code_result.get("success", False),
            "source_code": code_result.get("source_code", ""),
            "semantic_info": code_result.get("semantic_info", {}),
            "error": code_result.get("error", "")
        }
        response_bytes = len(json.dumps(response_data).encode('utf-8'))
        
        end_stage_tracking("invocation_scheduler_llm", start_time, request_bytes, response_bytes, 1)
        
        # 如果代码生成失败，直接返回
        if not code_result.get("success"):
            return GenerateCodeResponse(
                success=False,
                error=code_result.get("error", "代码生成失败"),
                source_code=code_result.get("source_code"),
                semantic_info=code_result.get("semantic_info")
            )
        
        source_code = code_result.get("source_code", "")
        semantic_info = code_result.get("semantic_info", {})
        
        # 如果代码生成成功，保存到temp目录
        await save_generated_code_to_temp(code_result, request.query)
        
        # 2. 自动进行编译执行（WASM端到端通信阶段）
        logger.info("代码生成成功，开始自动编译执行...")
        
        # 流量监测器功能已移除
        
        # 准备输入数据
        input_data = json.dumps({
            "test_timestamp": datetime.now().isoformat(),
            "user_query": request.query
        })
        
        # 调用 Server 服务进行编译执行
        try:
            # 开始invocation-scheduler-wasm-server阶段统计
            wasm_start_time = start_stage_tracking("invocation_scheduler_wasm_server")
            
            # 记录dw-client与dw-server通信开始时间
            execution_start_time = time.time()
            
            # 计算请求大小
            request_data = {
                "source_code": source_code,
                "semantic_info": semantic_info,
                "input_data": input_data,
                "user_query": request.query,
                "force_read_mode": request.force_read_mode,
                "intent_instance_id": str(uuid.uuid4()),
            }
            request_bytes = len(json.dumps(request_data).encode('utf-8'))
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                compile_response = await client.post(
                    f"{SERVER_URL}/compile-and-execute",
                    json=request_data
                )
                
                # 计算响应大小
                response_bytes = len(compile_response.content)
                
                # 结束invocation-scheduler-wasm-server阶段统计
                end_stage_tracking("invocation_scheduler_wasm_server", wasm_start_time, request_bytes, response_bytes, 2)
                
                if compile_response.status_code == 200:
                    compile_result = compile_response.json()
                    
                    # 合并代码生成和编译执行的结果
                    return GenerateCodeResponse(
                        success=code_result.get("success", False) and compile_result.get("success", False),
                        source_code=source_code,
                        semantic_info=semantic_info,
                        error=compile_result.get("error") if not compile_result.get("success", False) else None,
                        execution_id=compile_result.get("execution_id"),
                        result=compile_result.get("result"),
                        debug_info=compile_result.get("debug_info"),
                        execution_mode=compile_result.get("execution_mode"),
                        strategy=compile_result.get("strategy"),
                        network_operations=compile_result.get("network_operations"),
                        api_traffic_stats=compile_result.get("api_traffic_stats"),
                        wasm_compile_stats=compile_result.get("wasm_compile_stats"),
                        wasm_api_stats=compile_result.get("wasm_api_stats"),
                        replay_allow_nondeterministic_writes=compile_result.get(
                            "replay_allow_nondeterministic_writes"
                        ),
                        fallback_triggered=compile_result.get("fallback_triggered"),
                        fallback_reason=compile_result.get("fallback_reason"),
                        fallback_to_stepwise_success=compile_result.get(
                            "fallback_to_stepwise_success"
                        ),
                        final_mode=compile_result.get("final_mode"),
                    )
                else:
                    logger.error(f"编译执行失败: HTTP {compile_response.status_code}")
                    
                    return GenerateCodeResponse(
                        success=False,
                        source_code=source_code,
                        semantic_info=semantic_info,
                        error=f"编译执行失败: HTTP {compile_response.status_code} - {compile_response.text}",
                        execution_id=None
                    )
                    
        except httpx.ConnectError:
            # 即使出错也要结束统计
            end_stage_tracking("invocation_scheduler_wasm_server", wasm_start_time, 0, 0, 2)
            logger.error("无法连接到 Server 服务")
            
            error_response = "无法连接到 Server 服务，请确保 Server 服务正在运行"
            
            return GenerateCodeResponse(
                success=False,
                source_code=source_code,
                semantic_info=semantic_info,
                error=error_response,
                execution_id=None
            )
        except Exception as compile_error:
            # 即使出错也要结束统计
            end_stage_tracking("invocation_scheduler_wasm_server", wasm_start_time, 0, 0, 2)
            logger.error(f"编译执行过程出错: {compile_error}")
            
            error_response = f"编译执行过程出错: {str(compile_error)}"
            
            return GenerateCodeResponse(
                success=False,
                source_code=source_code,
                semantic_info=semantic_info,
                error=error_response,
                execution_id=None
            )
        
    except Exception as e:
        logger.error(f"代码生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compile-and-execute", response_model=CompileExecuteResponse)
async def compile_and_execute(request: CompileExecuteRequest):
    """编译并执行 Rust 代码 - 转发到 Server 服务"""
    # 注意：不在此处进行invocation_scheduler_wasm_server阶段统计
    # 因为/generate-code端点已经统计了，避免重复统计
    
    try:
        # 记录dw-client与dw-server通信开始时间
        execution_start_time = time.time()
        
        # 计算请求大小
        request_data = request.dict()
        if not (str(request_data.get("intent_instance_id") or "").strip()):
            request_data["intent_instance_id"] = str(uuid.uuid4())
        request_bytes = len(json.dumps(request_data).encode('utf-8'))
        
        # 流量监测器功能已移除
        
        async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{SERVER_URL}/compile-and-execute",
                    json=request_data
                )
            
        # 计算响应大小
        response_bytes = len(response.content)
        
        # 注意：不在此处进行invocation_scheduler_wasm_server阶段统计
        # 因为/generate-code端点已经统计了，避免重复统计
        
        # Monkey Patching已自动记录dw-client与dw-server通信流量，无需手动记录
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Server 服务错误: {response.text}"
            )
        
        server_result = response.json()
        
        return CompileExecuteResponse(
            success=server_result.get("success", False),
            result=server_result.get("result"),
            error=server_result.get("error"),
            execution_id=server_result.get("execution_id"),
            debug_info=server_result.get("debug_info"),
            execution_mode=server_result.get("execution_mode"),
            strategy=server_result.get("strategy"),
            network_operations=server_result.get("network_operations"),
            intent_instance_id=server_result.get("intent_instance_id"),
            replay_enabled=server_result.get("replay_enabled"),
            fallback_policy=server_result.get("fallback_policy"),
            replay_conflict_policy=server_result.get("replay_conflict_policy"),
            repair_attempt_budget=server_result.get("repair_attempt_budget"),
            replay_allow_nondeterministic_writes=server_result.get(
                "replay_allow_nondeterministic_writes"
            ),
            fallback_triggered=server_result.get("fallback_triggered"),
            fallback_reason=server_result.get("fallback_reason"),
            fallback_to_stepwise_success=server_result.get("fallback_to_stepwise_success"),
            final_mode=server_result.get("final_mode"),
        )
            
    except httpx.ConnectError:
        # 注意：不在此处进行invocation_scheduler_wasm_server阶段统计
        # 因为/generate-code端点已经统计了，避免重复统计
        error_response = "无法连接到 Server 服务，请确保 Server 服务正在运行"
        
        raise HTTPException(
            status_code=503,
            detail=error_response
        )
    except Exception as e:
        # 注意：不在此处进行invocation_scheduler_wasm_server阶段统计
        # 因为/generate-code端点已经统计了，避免重复统计
        logger.error(f"转发到 Server 服务失败: {e}")
        
        error_response = str(e)
        
        raise HTTPException(status_code=500, detail=error_response)

@app.post("/invocation-scheduler/process-tasks", response_model=APIAccessTaskResponse)
async def process_api_access_tasks(request: APIAccessTaskRequest):
    """处理API访问任务 - invocation scheduler端点"""
    try:
        logger.info(f"收到API访问任务请求，任务数量: {len(request.api_tasks)}")
        
        # 打印参数详情
        print(f"[ClientService] force_read_mode: {request.force_read_mode}, route_selection: {request.route_selection}, extra_rtt_ms: {request.extra_rtt_ms}")
        
        # 使用调用调度器处理任务
        result = await invocation_scheduler.process_api_access_tasks(
            request.api_tasks, 
            force_read_mode=request.force_read_mode,
            route_selection=request.route_selection,
            geo_delay=request.geo_delay,
            extra_rtt_ms=int(request.extra_rtt_ms or 0),
        )
        
        logger.info(f"API访问任务处理完成，成功: {result['success']}, 路线: {result['route_used']}")
        
        return APIAccessTaskResponse(
            success=result["success"],
            result=result["result"],
            error=result["error"],
            execution_time=result["execution_time"],
            route_used=result["route_used"],
            api_calls_made=result["api_calls_made"],
            tasks_processed=result["tasks_processed"],
            stats_diff=result.get("stats_diff"),
            wasm_compile_stats=result.get("wasm_compile_stats"),
            wasm_api_stats=result.get("wasm_api_stats"),
            configured_extra_rtt_ms=int(result.get("configured_extra_rtt_ms") or 0),
            effective_rtt_ms=int(result.get("effective_rtt_ms") or 0),
            selected_mode=str(result.get("selected_mode") or ""),
            mode_switch_count=int(result.get("mode_switch_count") or 0),
        )
        
    except Exception as e:
        logger.error(f"处理API访问任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/invocation-scheduler/performance-stats", response_model=PerformanceStatsResponse)
async def get_performance_stats():
    """获取性能统计信息"""
    try:
        stats = invocation_scheduler.get_performance_stats()
        return PerformanceStatsResponse(**stats)
    except Exception as e:
        logger.error(f"获取性能统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/invocation-scheduler/reset-performance")
async def reset_performance_data():
    """重置性能数据"""
    try:
        invocation_scheduler.reset_performance_data()
        return {"success": True, "message": "性能数据已重置"}
    except Exception as e:
        logger.error(f"重置性能数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/invocation-scheduler/update-config")
async def update_scheduler_config(threshold: Optional[int] = None, buffer_factor: Optional[float] = None):
    """更新调度器配置"""
    try:
        invocation_scheduler.update_config(threshold, buffer_factor)
        return {"success": True, "message": "配置已更新"}
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost-stats")
async def get_cost_stats():
    """获取全局开销统计信息"""
    try:
        from core.global_cost_tracker import get_all_stats
        stats = get_all_stats()
        return stats
    except Exception as e:
        logger.error(f"获取开销统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cost-stats/reset")
async def reset_cost_stats():
    """重置全局开销统计"""
    try:
        from core.global_cost_tracker import reset_global_cost_tracker
        reset_global_cost_tracker()
        return {"success": True, "message": "开销统计已重置"}
    except Exception as e:
        logger.error(f"重置开销统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost-stats/summary")
async def get_cost_stats_summary():
    """获取开销统计摘要"""
    try:
        from core.global_cost_tracker import get_global_cost_tracker
        tracker = get_global_cost_tracker()
        summary = tracker.get_stage_summary()
        return summary
    except Exception as e:
        logger.error(f"获取开销统计摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def save_generated_code_to_temp(result: Dict[str, Any], query: str):
    """保存生成的代码到temp目录"""
    try:
        # 确保temp目录存在
        temp_dir = PathUtils.get_temp_dir()
        
        # 生成文件名（包含时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 从查询中提取前20个字符作为文件名的一部分
        query_safe = "".join(c for c in query[:20] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        query_safe = query_safe.replace(' ', '_')
        filename = f"generated_code_{timestamp}_{query_safe}.txt"
        filepath = temp_dir / filename
        
        # 准备保存的内容
        save_content = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "success": result.get("success", False),
            "source_code": result.get("source_code", ""),
            "semantic_info": result.get("semantic_info", {}),
            "api_spec": result.get("api_spec", {}),
            "error": result.get("error", "")
        }
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== 生成的代码文件 ===\n")
            f.write(f"时间: {save_content['timestamp']}\n")
            f.write(f"查询: {save_content['query']}\n")
            f.write(f"成功: {save_content['success']}\n")
            f.write(f"错误: {save_content['error']}\n")
            f.write(f"\n=== 源代码 ===\n")
            f.write(save_content['source_code'])
            f.write(f"\n\n=== 语义信息 ===\n")
            f.write(json.dumps(save_content['semantic_info'], indent=2, ensure_ascii=False))
            f.write(f"\n\n=== API规范 ===\n")
            f.write(json.dumps(save_content['api_spec'], indent=2, ensure_ascii=False))
        
        logger.info(f"生成的代码已保存到: {filepath}")
        
    except Exception as e:
        logger.error(f"保存生成的代码失败: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=CLIENT_PORT)
