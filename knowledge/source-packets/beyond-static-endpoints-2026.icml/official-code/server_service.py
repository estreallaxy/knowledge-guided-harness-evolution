"""
ToolPro Server 服务
负责编译和执行 WebAssembly 代码，运行在端口 9000
"""

import json
import logging
import os
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

from core.wasm_runtime import WasmRuntime
from core.compilation_engine import CompilationEngine
from core.debug_engine import DebugEngine
from core.code_generator import CodeGenerator
from core.separated_execution_engine import SeparatedExecutionEngine
from core.execution_mode_detector import ExecutionModeDetector, NetworkOperation
from core.stepwise_agent_handler import build_llm_stepwise_handler
from core.global_cost_tracker import get_global_cost_tracker
from services.query_processor import QueryProcessor
from services.maintenance_service import MaintenanceService

# 配置
SERVER_PORT = 8001

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("Server 服务启动中...")
    
    
    await query_processor.initialize()
    await maintenance_service.start()
    yield
    # 关闭时清理
    logger.info("Server 服务关闭中...")
    
    

app = FastAPI(
    title="ToolPro Server Service",
    description="编译和执行 WebAssembly 代码的服务器端服务",
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

# 全局组件初始化
wasm_runtime = WasmRuntime()
compilation_engine = CompilationEngine()
debug_engine = DebugEngine()
code_generator = CodeGenerator()

# 新增的分离执行相关组件
execution_mode_detector = ExecutionModeDetector()
separated_execution_engine = SeparatedExecutionEngine(wasm_runtime, compilation_engine)
separated_execution_engine.register_stepwise_handler(build_llm_stepwise_handler())

query_processor = QueryProcessor(
    compilation_engine=compilation_engine,
    debug_engine=debug_engine,
    code_generator=code_generator
)

maintenance_service = MaintenanceService(query_processor)

class CompileExecuteRequest(BaseModel):
    source_code: str
    semantic_info: Dict[str, Any]
    input_data: str
    user_query: Optional[str] = None
    force_read_mode: Optional[bool] = False
    replay: Optional[str] = "on"
    fallback_policy: Optional[str] = "safe_stepwise"
    replay_conflict_policy: Optional[str] = "strict_prefix"
    repair_attempt_budget: Optional[int] = None
    intent_instance_id: Optional[str] = None
    replay_allow_nondeterministic_writes: Optional[bool] = False

class NetworkOperationResponse(BaseModel):
    """网络操作响应模型"""
    operation_type: str
    api_call: str
    line_number: int
    url: str
    method: str
    sequence_number: int
    expected_impact: str

def convert_network_operations_to_response(network_operations: List[NetworkOperation]) -> List[NetworkOperationResponse]:
    """将 NetworkOperation 对象转换为可序列化的响应模型"""
    if not network_operations:
        return []
    
    return [
        NetworkOperationResponse(
            operation_type=op.operation_type,
            api_call=op.api_call,
            line_number=op.line_number,
            url=op.url,
            method=op.method,
            sequence_number=op.sequence_number,
            expected_impact=op.expected_impact
        )
        for op in network_operations
    ]

def sanitize_response_data(data: Any) -> Any:
    """清理响应数据，确保所有对象都可以被 Pydantic 序列化"""
    if data is None:
        return None
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], NetworkOperation):
                # 转换 NetworkOperation 列表
                sanitized[key] = convert_network_operations_to_response(value)
            elif isinstance(value, NetworkOperation):
                # 转换单个 NetworkOperation 对象
                sanitized[key] = convert_network_operations_to_response([value])[0]
            else:
                sanitized[key] = sanitize_response_data(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_response_data(item) for item in data]
    else:
        return data

class CompileExecuteResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_id: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
    execution_mode: Optional[str] = None
    strategy: Optional[str] = None
    network_operations: Optional[List[NetworkOperationResponse]] = None
    api_traffic_stats: Optional[Dict[str, Any]] = None
    # 新增编译阶段统计数据
    wasm_compile_stats: Optional[Dict[str, Any]] = None
    wasm_api_stats: Optional[Dict[str, Any]] = None
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
    projection_rejected: Optional[bool] = None
    projection_errors: Optional[List[str]] = None
    projection_diagnostics: Optional[List[str]] = None


@app.get("/api")
async def api_root():
    """API根路径"""
    return {"message": "ToolPro Server Service is running"}

@app.post("/compile-and-execute", response_model=CompileExecuteResponse)
async def compile_and_execute(request: CompileExecuteRequest):
    """编译并执行Rust代码"""
    try:
        # 预处理输入数据：如果不是JSON格式，则转换为JSON
        processed_input_data = request.input_data

        # 检查输入数据是否为有效的JSON
        is_valid_json = False
        try:
            json.loads(request.input_data)
            is_valid_json = True
        except json.JSONDecodeError:
            # 不是有效的JSON，需要转换
            pass

        if not is_valid_json:
            # 将自然语言输入转换为结构化的JSON格式
            structured_input = {
                "raw_input": request.input_data,
                "timestamp": datetime.now().isoformat(),
                "input_type": "natural_language"
            }
            processed_input_data = json.dumps(structured_input, ensure_ascii=False)
            logger.info(f"转换自然语言输入为JSON: {processed_input_data}")

        # 关键修复：把 wasm 阶段“全局累计值”改为“本次请求增量”
        # 方案：执行前后分别读取 wasm_compile / wasm_api 的统计，返回 post-pre 的差值
        global_tracker = get_global_cost_tracker()

        def _take_stage_snapshot(stage_name: str) -> Dict[str, Any]:
            stats = global_tracker.get_stage_stats(stage_name) or {}
            return {
                "total_duration": float(stats.get("total_duration", 0.0)),
                "count": int(stats.get("count", 0)),
                "total_request_bytes": int(stats.get("total_request_bytes", 0)),
                "total_response_bytes": int(stats.get("total_response_bytes", 0)),
                "total_bytes": int(stats.get("total_bytes", 0)),
            }

        pre_wasm_compile_stats = _take_stage_snapshot("wasm_compile")
        pre_wasm_api_stats = _take_stage_snapshot("wasm_api")

        intent = (request.intent_instance_id or "").strip()
        if not intent:
            raise HTTPException(
                status_code=422,
                detail="intent_instance_id is required and must be non-empty",
            )

        _replay = (request.replay or "on").strip().lower()
        replay_enabled = _replay in ("on", "true", "1", "yes")

        # 使用新的分离执行引擎
        result = await separated_execution_engine.execute_with_mode_detection(
            module_id=f"module_{datetime.now().timestamp()}",
            source_code=request.source_code,
            input_data=processed_input_data,
            user_query=request.user_query or request.input_data,
            timeout=30,
            force_read_mode=request.force_read_mode,
            replay_enabled=replay_enabled,
            fallback_policy=request.fallback_policy or "safe_stepwise",
            replay_conflict_policy=request.replay_conflict_policy or "strict_prefix",
            repair_attempt_budget=request.repair_attempt_budget,
            intent_instance_id=intent,
            replay_allow_nondeterministic_writes=bool(
                request.replay_allow_nondeterministic_writes
            ),
        )
        
        def _compute_delta_stats(pre: Dict[str, Any], post: Dict[str, Any]) -> Dict[str, Any]:
            delta_count = max(0, int(post.get("count", 0)) - int(pre.get("count", 0)))
            delta_total_duration = max(0.0, float(post.get("total_duration", 0.0)) - float(pre.get("total_duration", 0.0)))
            delta_total_request_bytes = max(0, int(post.get("total_request_bytes", 0)) - int(pre.get("total_request_bytes", 0)))
            delta_total_response_bytes = max(0, int(post.get("total_response_bytes", 0)) - int(pre.get("total_response_bytes", 0)))
            delta_total_bytes = max(0, int(post.get("total_bytes", 0)) - int(pre.get("total_bytes", 0)))
            avg_duration = (delta_total_duration / delta_count) if delta_count > 0 else 0.0
            return {
                "total_duration": delta_total_duration,
                "count": delta_count,
                "avg_duration": avg_duration,
                "total_request_bytes": delta_total_request_bytes,
                "total_response_bytes": delta_total_response_bytes,
                "total_bytes": delta_total_bytes,
            }

        # 获取本次请求的 wasm 编译阶段和 API 阶段统计（post-pre 增量）
        try:
            post_wasm_compile_stats = _take_stage_snapshot("wasm_compile")
            post_wasm_api_stats = _take_stage_snapshot("wasm_api")

            result["wasm_compile_stats"] = _compute_delta_stats(pre_wasm_compile_stats, post_wasm_compile_stats)
            result["wasm_api_stats"] = _compute_delta_stats(pre_wasm_api_stats, post_wasm_api_stats)

            logger.info(f"添加编译阶段增量统计数据: {result.get('wasm_compile_stats')}")
            logger.info(f"添加API阶段增量统计数据: {result.get('wasm_api_stats')}")
        except Exception as e:
            logger.warning(f"获取/计算 wasm 阶段增量统计数据失败: {e}")
            result["wasm_compile_stats"] = {
                "total_duration": 0.0,
                "count": 0,
                "avg_duration": 0.0,
                "total_request_bytes": 0,
                "total_response_bytes": 0,
                "total_bytes": 0,
            }
            result["wasm_api_stats"] = {
                "total_duration": 0.0,
                "count": 0,
                "avg_duration": 0.0,
                "total_request_bytes": 0,
                "total_response_bytes": 0,
                "total_bytes": 0,
            }
        
        # 清理响应数据，确保可以序列化
        sanitized_result = sanitize_response_data(result)
        
        # 应用debug配置过滤
        from core.debug_config import debug_config
        filtered_result = debug_config.filter_response_data(sanitized_result)
        
        return CompileExecuteResponse(
            success=filtered_result.get("success", False),
            result=filtered_result.get("data"),
            error=filtered_result.get("error"),
            execution_id=filtered_result.get("execution_id"),
            debug_info=filtered_result.get("debug_info") if debug_config.should_include_debug_in_response() else None,
            execution_mode=filtered_result.get("execution_mode"),
            strategy=filtered_result.get("strategy"),
            network_operations=filtered_result.get("network_operations"),
            api_traffic_stats=filtered_result.get("api_traffic_stats"),
            wasm_compile_stats=filtered_result.get("wasm_compile_stats"),
            wasm_api_stats=filtered_result.get("wasm_api_stats"),
            intent_instance_id=filtered_result.get("intent_instance_id"),
            replay_enabled=filtered_result.get("replay_enabled"),
            fallback_policy=filtered_result.get("fallback_policy"),
            replay_conflict_policy=filtered_result.get("replay_conflict_policy"),
            repair_attempt_budget=filtered_result.get("repair_attempt_budget"),
            replay_allow_nondeterministic_writes=filtered_result.get(
                "replay_allow_nondeterministic_writes"
            ),
            fallback_triggered=filtered_result.get("fallback_triggered"),
            fallback_reason=filtered_result.get("fallback_reason"),
            fallback_to_stepwise_success=filtered_result.get("fallback_to_stepwise_success"),
            final_mode=filtered_result.get("final_mode"),
            projection_rejected=filtered_result.get("projection_rejected"),
            projection_errors=filtered_result.get("projection_errors"),
            projection_diagnostics=filtered_result.get("projection_diagnostics"),
        )
    except Exception as e:
        logger.error(f"编译执行失败: {e}")
        return CompileExecuteResponse(
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """健康检查"""
    system_status = await query_processor.get_system_status()
    maintenance_status = maintenance_service.get_service_status()
    
    return {
        "status": "healthy",
        "wasm_runtime": wasm_runtime.is_available(),
        "system_status": system_status,
        "maintenance_service": maintenance_status
    }

@app.post("/maintenance/force")
async def force_maintenance():
    """强制执行维护任务"""
    await maintenance_service.force_maintenance()
    return {"message": "维护任务已执行"}

@app.get("/maintenance/status")
async def get_maintenance_status():
    """获取维护服务状态"""
    return maintenance_service.get_service_status()


@app.get("/debug/{execution_id}")
async def get_debug_info(execution_id: str):
    """获取debug信息"""
    debug_history = debug_engine.get_debug_history(execution_id)
    return {
        "execution_id": execution_id,
        "debug_history": debug_history
    }

@app.get("/execution/stats")
async def get_execution_stats():
    """获取执行统计信息"""
    return separated_execution_engine.get_execution_stats()

@app.get("/execution/mode-detection")
async def get_mode_detection_info():
    """获取模式检测信息"""
    return {
        "detector_available": execution_mode_detector is not None
    }

@app.post("/execution/clear-data")
async def clear_execution_data():
    """清空执行数据"""
    separated_execution_engine.clear_execution_data()
    return {"message": "执行数据已清空"}




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)
