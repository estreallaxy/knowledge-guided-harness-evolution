"""
WebAssembly Runtime 集成模块
使用 wasmtime-py 提供动态加载和执行 Wasm 代码的能力
支持自定义Host Functions进行HTTP API调用
重构版本：移除模拟执行，采用历史缓存+错误重启策略
"""

import wasmtime
import logging
import asyncio
import httpx
import os
from typing import Dict, Any, Optional, List, Tuple
import json
import nest_asyncio
import psutil
import time
import threading
from collections import OrderedDict

from .global_cost_tracker import start_stage_tracking, end_stage_tracking
from .history_manager import HistoryManager, global_history_manager
from .path_utils import PathUtils
#  修复循环依赖：延迟导入MCPDebugManager

logger = logging.getLogger(__name__)


def mcp_call_tool_timeout_seconds() -> float:
    """
    MCP ``call_tool`` 等待上限（秒）。子进程冷启动 + baseline 导入可能远超 10s；
    可用环境变量 ``WASM_MCP_CALL_TIMEOUT_S`` 覆盖（5–600）。
    """
    raw = (os.environ.get("WASM_MCP_CALL_TIMEOUT_S") or "").strip()
    if raw:
        try:
            v = float(raw)
        except ValueError:
            return 120.0
        return max(5.0, min(v, 600.0))
    return 120.0


class WasmRuntime:
    """WebAssembly 运行时管理器"""
    
    _instance: Optional['WasmRuntime'] = None
    _lock = threading.Lock()  # 线程安全锁
    
    def __new__(cls, auto_init_session_manager: bool = True):
        # 双重检查锁定模式确保线程安全
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False  # 标识是否已初始化
                    
                    # 创建线程安全的属性
                    instance.engine = None
                    instance.store = None
                    instance.instances: Dict[str, wasmtime.Instance] = {}
                    instance.memory = None
                    
                    # SessionManager和MCP调试管理器
                    instance.session_manager = None  # 确保SessionManager属性存在
                    instance.mcp_debug_manager = None
                    
                    # intent 作用域内使用独立 HistoryManager（见 begin_intent_history_scope）
                    instance._scoped_history_manager = None  # type: ignore[attr-defined]
                    instance._active_intent_instance_id = None  # type: ignore[attr-defined]
                    instance._intent_history_registry = OrderedDict()  # type: ignore[attr-defined]
                    instance._intent_history_registry_max = 256  # type: ignore[attr-defined]
                    instance.execution_mode = "unknown"
                    instance.current_transaction_id = None
                    
                    # 线程本地存储支持
                    instance.thread_local_data = threading.local()
                    instance.loading_occurred = threading.Event()
                    instance.event_loop: Optional[asyncio.AbstractEventLoop] = None
                    instance.thread_id = threading.current_thread().ident
                    
                    # 内存管理改进
                    instance._memory_lock = threading.Lock()
                    instance._allocated_memory: int = 0x1000
                    instance._allocations: Dict[int, dict] = {}
                    instance._free_list: List[Tuple[int, int]] = []  #  添加缺少的属性初始化
                    instance._next_memory_address: int = 0x1000
                    
                    nest_asyncio.apply()
                    logger.info(f"WasmRuntime实例创建 - 线程ID: {instance.thread_id}")
                    
                    cls._instance = instance
        return cls._instance

    def __init__(self, auto_init_session_manager: bool = True):
        if hasattr(self, '_initialized'):
            return
            
        # 初始化核心组件
        self._initialize_core_components()
        
        # SessionManager和和MCP调试管理器
        self.session_manager = None  # SessionManager实例
        self.mcp_debug_manager = None  # MCP调试管理器
        
        # 执行模式相关（简化版本）
        self.execution_mode = "unknown"  # unknown, read_only, write_mode
        self.current_transaction_id = None
        self.replay_enabled = True
        self.replay_conflict_policy = "strict_prefix"
        self.replay_allow_nondeterministic_writes: bool = False
        self._mcp_write_tool_meta_registry: Optional[Dict[str, Dict[str, Any]]] = None

        # 统一的事件循环管理
        self.event_loop = None
        
        self._initialized = True
        logger.info(f"WasmRuntime初始化完成 - 线程ID: {self.thread_id}")
        
        # 同步初始化SessionManager（移除多线程）
        if auto_init_session_manager:
            try:
                logger.info(f"开始同步初始化SessionManager - 线程ID: {self.thread_id}")
                self._initialize_session_manager_sync()
                logger.info(f"SessionManager同步初始化完成 - 线程ID: {self.thread_id}")
            except Exception as e:
                logger.error(f"SessionManager同步初始化失败: {e} - 线程ID: {self.thread_id}")
                # 不抛出异常，允许后续延迟初始化
    
    def _initialize_core_components(self):
        """初始化核心Wasm组件"""
        with self._memory_lock:
            if self.engine is None:
                self.engine = wasmtime.Engine()
                self.store = wasmtime.Store(self.engine)
    
    def _initialize_session_manager_sync(self):
        """同步初始化SessionManager（统一事件循环管理）"""
        try:
            logger.info(f"开始同步初始化SessionManager - 线程ID: {self.thread_id}")
            
            # 统一的事件循环管理
            self._setup_unified_event_loop()
            logger.info(f"事件循环设置完成 - 线程ID: {self.thread_id}")
            
            # 在事件循环中初始化SessionManager
            logger.info(f"开始执行_create_session_manager异步方法 - 线程ID: {self.thread_id}")
            session_manager = self.event_loop.run_until_complete(self._create_session_manager())
            logger.info(f"_create_session_manager异步方法执行完成，返回值: {session_manager} - 线程ID: {self.thread_id}")
            
            if session_manager:
                self.session_manager = session_manager
                logger.info(f"SessionManager实例已设置，ID: {id(session_manager)} - 线程ID: {self.thread_id}")
                
                # 延迟初始化MCP调试管理器
                self._lazy_init_mcp_debug_manager(session_manager)
                
                logger.info(f"SessionManager同步初始化完成 - 线程ID: {self.thread_id}")
            else:
                logger.error(f"SessionManager同步初始化失败：_create_session_manager返回None - 线程ID: {self.thread_id}")
                self.session_manager = None
                
        except Exception as e:
            logger.error(f"SessionManager同步初始化异常: {e} - 线程ID: {self.thread_id}")
            import traceback
            logger.error(f"同步初始化错误堆栈: {traceback.format_exc()}")
            # 确保在异常情况下也设置session_manager为None
            self.session_manager = None
            
    def _setup_unified_event_loop(self):
        """设置统一的事件循环"""
        try:
            # 检查是否有运行中的事件循环
            try:
                current_loop = asyncio.get_running_loop()
                logger.info(f"发现在运行的事件循环: {current_loop} - 线程ID: {self.thread_id}")
                self.event_loop = current_loop
            except RuntimeError:
                # 没有运行中的事件循环，创建新的
                self.event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.event_loop)
                logger.info(f"创建新事件循环: {self.event_loop} - 线程ID: {self.thread_id}")
        except Exception as e:
            logger.error(f"设置事件循环失败: {e} - 线程ID: {self.thread_id}")
            # 创建备用事件循环
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
    
    def _lazy_init_mcp_debug_manager(self, session_manager):
        """ 延迟初始化MCP调试管理器，避免循环依赖"""
        try:
            from .mcp_debug_manager import MCPDebugManager
            self.mcp_debug_manager = MCPDebugManager(session_manager)
            logger.info(f"MCPDebugManager延迟初始化成功 - 线程ID: {self.thread_id}")
        except ImportError as e:
            logger.warning(f"无法导入MCPDebugManager: {e} - 线程ID: {self.thread_id}")
            self.mcp_debug_manager = None
        except Exception as e:
            logger.error(f"MCPDebugManager初始化失败: {e} - 线程ID: {self.thread_id}")
            self.mcp_debug_manager = None
    
    def cleanup_resources(self):
        """清理资源，确保没有内存泄漏"""
        try:
            # 清理SessionManager
            if hasattr(self, 'session_manager') and self.session_manager:
                if hasattr(self.session_manager, 'cleanup'):
                    self.session_manager.cleanup()
                self.session_manager = None
            
            # 清理MCP调试管理器
            if self.mcp_debug_manager:
                if hasattr(self.mcp_debug_manager, 'cleanup'):
                    self.mcp_debug_manager.cleanup()
                self.mcp_debug_manager = None
            
            # 清理Event循环
            if self.event_loop and not self.event_loop.is_closed():
                try:
                    # 取消所有pending的任务
                    pending_tasks = asyncio.all_tasks(self.event_loop)
                    for task in pending_tasks:
                        task.cancel()
                    
                    # 运行一次循环以处理取消
                    if pending_tasks:
                        self.event_loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
                    
                    # 关闭事件循环
                    self.event_loop.close()
                    logger.info(f"事件循环已关闭 - 线程ID: {self.thread_id}")
                except Exception as e:
                    logger.error(f"关闭事件循环失败: {e}")
                finally:
                    self.event_loop = None
            
            # 清理内存分配
            with self._memory_lock:
                self._allocations.clear()
                self._free_list.clear()
                self._next_memory_address = 0x1000
                
            logger.info(f"WasmRuntime资源清理完成 - 线程ID: {self.thread_id}")
            
        except Exception as e:
            logger.error(f"资源清理失败: {e}")
            import traceback
            logger.error(f"资源清理错误堆栈: {traceback.format_exc()}")
    
    def __del__(self):
        """析构函数，确保资源被正确清理"""
        try:
            self.cleanup_all()
        except Exception as e:
            logger.error(f"WasmRuntime析构时清理失败: {e}")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动清理"""
        self.cleanup_all()
    
    def set_execution_mode(self, mode: str):
        """设置执行模式"""
        self.execution_mode = mode
        logger.info(f"设置执行模式: {mode}")
        
        # 如果是写入模式，开始新事务
        if mode == "write_mode":
            self._start_new_transaction()

    def set_replay_runtime_options(
        self,
        *,
        replay_enabled: bool,
        replay_conflict_policy: str = "strict_prefix",
        replay_allow_nondeterministic_writes: Optional[bool] = None,
    ) -> None:
        """与执行引擎对齐的 replay 开关；同步到 HistoryManager。"""
        policy = replay_conflict_policy or "strict_prefix"
        self.replay_enabled = bool(replay_enabled)
        self.replay_conflict_policy = policy
        if replay_allow_nondeterministic_writes is not None:
            self.replay_allow_nondeterministic_writes = bool(
                replay_allow_nondeterministic_writes
            )
        hm = self.history_manager
        if hm is not None:
            hm.replay_enabled = bool(replay_enabled)
        logger.info(
            "WasmRuntime replay: enabled=%s, replay_conflict_policy=%s, allow_nd_writes=%s",
            self.replay_enabled,
            policy,
            getattr(self, "replay_allow_nondeterministic_writes", False),
        )

    def set_mcp_write_tool_meta_registry(
        self, registry: Optional[Dict[str, Dict[str, Any]]]
    ) -> None:
        """可选：工具名 → §3.2.7 元数据；与 ``core.default_mcp_write_tool_meta`` 内置表合并（后者为底，本方法覆盖）。"""
        self._mcp_write_tool_meta_registry = registry

    def get_mcp_tool_meta_for_write_replay(self, tool_name: str) -> Dict[str, Any]:
        """返回合并后的工具元数据（非 None），供 replay 策略评估。"""
        from .default_mcp_write_tool_meta import merge_write_tool_meta

        reg = getattr(self, "_mcp_write_tool_meta_registry", None)
        return merge_write_tool_meta(
            tool_name,
            reg if isinstance(reg, dict) else None,
        )

    def write_replay_policy_denied_json(
        self, tool_name: str, parameters: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        write_mode 下在 Q_history 命中与真实写之前调用 ``evaluate_write_replay_policy``。
        若禁止 program 侧 WRITE replay 语义，返回错误 JSON 字符串（上层可降级 stepwise）。
        """
        from .replay_guard import normalize_params
        from .replay_policy import evaluate_write_replay_policy

        tool_meta = self.get_mcp_tool_meta_for_write_replay(tool_name)
        normalized = normalize_params(dict(parameters or {}))
        allow_nd = bool(getattr(self, "replay_allow_nondeterministic_writes", False))
        pr = evaluate_write_replay_policy(
            tool_meta,
            normalized,
            allow_nondeterministic_writes=allow_nd,
        )
        if pr.replay_allowed:
            return None
        reason = pr.reason or "replay_policy_denied"
        nd_hit = reason == "replay_nondeterministic_no_idempotency"
        return json.dumps(
            {
                "success": False,
                "error": reason,
                "replay_policy_denied": True,
                "replay_nondeterministic_endpoint_hit": nd_hit,
                "tool": tool_name,
                "parameters": parameters,
            },
            ensure_ascii=False,
        )

    @property
    def history_manager(self) -> HistoryManager:
        """当前 intent 作用域下的 HistoryManager；无 intent 时退回进程级 global。"""
        sc = getattr(self, "_scoped_history_manager", None)
        if sc is not None:
            return sc
        return global_history_manager

    def begin_intent_history_scope(self, intent_instance_id: Optional[str]) -> None:
        """
        非空 ``intent_instance_id``：按 §3.2.8 **方案 A** 跨 ``begin/end`` 复用同一 ``HistoryManager``
        （有界 OrderedDict，默认最多 256 个 intent）。

        空 id：退回 global ``HistoryManager``（Program 路径应在 ``SeparatedExecutionEngine`` 入口拒绝）。
        """
        iid = (intent_instance_id or "").strip() or None
        self._active_intent_instance_id = iid
        if not iid:
            self._scoped_history_manager = None
            logger.warning(
                "intent_instance_id 未设置：使用 global HistoryManager（Program 路径应在引擎入口拒绝）"
            )
            return
        reg = getattr(self, "_intent_history_registry", None)
        if not isinstance(reg, OrderedDict):
            self._intent_history_registry = OrderedDict()
            reg = self._intent_history_registry
        max_n = int(getattr(self, "_intent_history_registry_max", 256) or 256)
        if iid in reg:
            hm = reg[iid]
            reg.move_to_end(iid, last=True)
        else:
            hm = HistoryManager()
            reg[iid] = hm
            while len(reg) > max_n:
                reg.popitem(last=False)
        hm.replay_enabled = bool(global_history_manager.replay_enabled)
        self._scoped_history_manager = hm
        logger.info(
            "HistoryManager intent 绑定/复用: intent_instance_id=%s hm_id=%s",
            iid,
            id(hm),
        )

    def end_intent_history_scope(self) -> None:
        """与 ``begin_intent_history_scope`` 成对，在引擎 ``finally`` 中调用。"""
        self._scoped_history_manager = None
        self._active_intent_instance_id = None

    def set_fixed_api_params(self, fixed_params: Dict[str, Any]) -> None:
        """设置修复后的API参数，用于增量执行"""
        self.fixed_api_params = fixed_params
        logger.info(f"WasmRuntime设置修复后的API参数: {fixed_params}")
    
    def get_fixed_api_params(self) -> Optional[Dict[str, Any]]:
        """获取修复后的API参数"""
        return getattr(self, 'fixed_api_params', None)
    
    def _start_new_transaction(self):
        """开始新事务（内部方法：仅当写入模式时使用）"""
        if self.execution_mode == "write_mode":
            import uuid
            self.current_transaction_id = str(uuid.uuid4())
            
            # 新版本的HistoryManager (Q_history/Q_working机制)
            # 关键：事务开始时清空Q_working和Q_history队列
            self.history_manager.clear_q_history()
            self.history_manager.q_working.clear()
            logger.info(f"使用新版本HistoryManager，事务ID: {self.current_transaction_id}")
            logger.info("🔄 事务开始：已清空Q_working和Q_history队列")
    
    def _start_new_transaction_for_context(self, source_code: str) -> str:
        """为事务上下文管理创建新事务（统一事务管理方法）"""
        import uuid
        transaction_id = str(uuid.uuid4())
        
        # 更新当前事务ID
        self.current_transaction_id = transaction_id
        
        # 新版本的HistoryManager (Q_history/Q_working机制)
        # 关键：事务开始时清空Q_working和Q_history队列
        self.history_manager.clear_q_history()
        self.history_manager.q_working.clear()
        logger.info(f"使用新版本HistoryManager，事务上下文ID: {transaction_id}")
        logger.info("🔄 事务开始：已清空Q_working和Q_history队列")
        
        return transaction_id
    
    def _ensure_transaction_id(self):
        """确保current_transaction_id属性存在"""
        if not hasattr(self, 'current_transaction_id'):
            logger.warning("current_transaction_id属性缺失，重新初始化")
            self.current_transaction_id = None

    def _end_transaction(self, success: bool = True):
        """结束事务并清理资源"""
        try:
            self._ensure_transaction_id()  # 确保属性存在
            if self.current_transaction_id:
                # 新版本HistoryManager (Q_history/Q_working机制)
                # 若调试保护开启，则在调试流程内由调试引擎统一处理Q_history清理/保留
                preserve_during_debug = getattr(self, '_preserve_history_during_debug', False)
                if success:
                    if preserve_during_debug:
                        logger.info(f"事务成功，但处于调试保护期，暂不清空Q_history: {self.current_transaction_id}")
                    else:
                        # 新版本：清空Q_history和Q_working，表示事务成功完成
                        self.history_manager.clear_q_history()
                        self.history_manager.q_working.clear()
                        logger.info(f"事务成功结束: {self.current_transaction_id} (新版本HistoryManager)")
                        logger.info("🔄 事务成功结束：已清空Q_working和Q_history队列")
                else:
                    if preserve_during_debug:
                        logger.info(f"事务失败，但处于调试保护期，由调试流程控制Q_history回滚/清理: {self.current_transaction_id}")
                    else:
                        # 新版本：回滚Q_working到Q_history
                        self.history_manager.rollback_to_q_history()
                        logger.info(f"事务失败，已回滚Q_working到Q_history: {self.current_transaction_id}")
                
                # 事务结束后的清理工作
                self._cleanup_after_transaction()
                
                self.current_transaction_id = None
        except AttributeError as e:
            logger.error(f"回滚事务时属性错误: {e}")
            # 创建缺失的属性
            self.current_transaction_id = None
            raise
    
    def _cleanup_after_transaction(self):
        """事务结束后的资源清理"""
        try:
            logger.info(f"开始事务后的资源清理 - 线程ID: {self.thread_id}")
            
            # 清理WASM内存
            self.cleanup_memory()
            
            # 清理模块实例（可选：保留编译好的模块以便重用）
            # 注意：这里可以选择性地清理模块，或者保留它们供下次复用
            
            logger.info(f"事务后资源清理完成 - 线程ID: {self.thread_id}")
            
        except Exception as e:
            logger.error(f"事务后清理失败: {e} - 线程ID: {self.thread_id}")
    
    def cleanup_session_manager_if_unused(self):
        """如果SessionManager不被使用则清理"""
        try:
            if hasattr(self, 'session_manager') and self.session_manager:
                # 检查是否有未完成的请求
                has_pending_requests = False
                if hasattr(self.session_manager, 'servers'):
                    for server_name, client_core in self.session_manager.servers.items():
                        if hasattr(client_core, 'pending_requests') and client_core.pending_requests:
                            has_pending_requests = True
                            break
                
                # 如果没有待处理的请求，可以选择性清理
                if not has_pending_requests:
                    logger.info(f"SessionManager当前无待处理请求，保留实例复用 - 线程ID: {self.thread_id}")
                    # 注意：这里不清理SessionManager，因为创建成本较高
                    # 可能需要在应用程序级别决定是否清理
                else:
                    logger.info(f"SessionManager有待处理请求，保持运行 - 线程ID: {self.thread_id}")
                    
        except Exception as e:
            logger.error(f"检查SessionManager状态失败: {e} - 线程ID: {self.thread_id}")
    
    def analyze_code_for_read_write_operations(self, source_code: str) -> Dict[str, Any]:
        """分析代码中的读写操作"""
        analysis = {
            "has_read_operations": False,
            "has_write_operations": False,
            "read_operations": [],
            "write_operations": [],
            "execution_mode": "unknown"
        }
        
        lines = source_code.split('\n')
        for i, line in enumerate(lines):
            line_num = i + 1
            if '@READ_OPERATION' in line:
                analysis["has_read_operations"] = True
                analysis["read_operations"].append(line_num)
            elif '@WRITE_OPERATION' in line:
                analysis["has_write_operations"] = True
                analysis["write_operations"].append(line_num)
        
        # 确定执行模式
        if analysis["has_write_operations"]:
            analysis["execution_mode"] = "write_mode"
        elif analysis["has_read_operations"]:
            analysis["execution_mode"] = "read_only"
        else:
            analysis["execution_mode"] = "unknown"
        
        logger.info(f"代码分析结果: {analysis}")
        return analysis
    
    def is_session_manager_available(self) -> bool:
        """检查SessionManager是否可用"""
        has_attr = hasattr(self, 'session_manager')
        is_not_none = self.session_manager is not None if has_attr else False
        
        logger.debug(f"SessionManager可用性检查: has_attr={has_attr}, is_not_none={is_not_none}, "
                    f"thread_id={self.thread_id}")
        
        if has_attr and self.session_manager is not None:
            logger.debug(f"SessionManager可用，ID: {id(self.session_manager)} - 线程ID: {self.thread_id}")
            return True
        else:
            logger.debug(f"SessionManager不可用: has_attr={has_attr}, session_manager={self.session_manager} - 线程ID: {self.thread_id}")
            return False
    
    def initialize_session_manager_if_needed(self) -> bool:
        """如果需要，同步初始化SessionManager实例 - 作为备选方案"""
        try:
            # 检查SessionManager是否已可用
            if self.is_session_manager_available():
                el = getattr(self, "event_loop", None)
                if el is None or (
                    hasattr(el, "is_closed") and el.is_closed()
                ):
                    logger.warning(
                        "SessionManager 仍存在但 event_loop 缺失或已关闭，丢弃旧引用并重连 "
                        f"- 线程ID: {self.thread_id}"
                    )
                    self.session_manager = None
                    self.mcp_debug_manager = None
                    self.event_loop = None
                else:
                    logger.info(f"SessionManager已可用 - 线程ID: {self.thread_id}")
                    return True
            
            logger.warning(f"SessionManager初始化失败，尝试延迟初始化 - 线程ID: {self.thread_id}")
            
            # 使用同步初始化方法作为备选
            self._initialize_session_manager_sync()
            
            # 检查初始化结果
            if self.is_session_manager_available():
                logger.info(f"SessionManager延迟初始化成功 - 线程ID: {self.thread_id}")
                return True
            else:
                logger.error(f"SessionManager延迟初始化失败 - 线程ID: {self.thread_id}")
                return False
                
        except Exception as e:
            logger.error(f"延迟初始化SessionManager失败 - 线程ID: {self.thread_id}, 错误: {e}")
            return False
    
    async def _create_session_manager(self):
        """创建SessionManager实例"""
        try:
            from pathlib import Path
            import sys
            
            # 使用默认配置路径
            mcp_client_path = PathUtils.get_mcp_client_dir()
            config_path = str(mcp_client_path / "client_config.toml")
            
            logger.info(f"SessionManager配置文件路径: {config_path} - 线程ID: {self.thread_id}")
            
            # 添加MCP客户端路径到sys.path
            if str(mcp_client_path) not in sys.path:
                sys.path.insert(0, str(mcp_client_path))
                logger.info(f"添加路径到sys.path: {mcp_client_path} - 线程ID: {self.thread_id}")
            
            # 动态导入SessionManager
            try:
                logger.info(f"开始导入SessionManager模块 - 线程ID: {self.thread_id}")
                from session_manager import SessionManager
                logger.info(f"SessionManager模块导入成功 - 线程ID: {self.thread_id}")
            except ImportError as e:
                logger.error(f"无法导入SessionManager - 线程ID: {self.thread_id}, 错误: {e}")
                return None
            
            # 创建SessionManager实例
            logger.info(f"创建SessionManager实例 - 线程ID: {self.thread_id}")
            session_manager = SessionManager(config_path)
            logger.info(f"SessionManager实例创建成功，ID: {id(session_manager)} - 线程ID: {self.thread_id}")
            
            # 启动MCP服务器
            logger.info(f"开始启动MCP服务器 - 线程ID: {self.thread_id}")
            if not await session_manager.start_all_servers():
                logger.error(f"启动MCP服务器失败 - 线程ID: {self.thread_id}")
                return None
            logger.info(f"MCP服务器启动成功 - 线程ID: {self.thread_id}")
            
            # 初始化连接
            logger.info(f"开始初始化连接 - 线程ID: {self.thread_id}")
            if not await session_manager.initialize_connections():
                logger.error(f"初始化MCP连接失败 - 线程ID: {self.thread_id}")
                return None
            logger.info(f"连接初始化成功 - 线程ID: {self.thread_id}")
            
            return session_manager
            
        except Exception as e:
            logger.error(f"创建SessionManager失败 - 线程ID: {self.thread_id}, 错误: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"完整错误堆栈: {traceback.format_exc()}")
            return None
    
        
    def _debug_memory_call(self, method_name, *args, **kwargs):
        """调试内存方法调用的包装器，使用正确的wasmtime-py API"""
        from .debug_config import debug_config
        
        if debug_config.should_log_debug():
            logger.info(f"[DEBUG] 调用 memory.{method_name} 参数: args={args}, kwargs={kwargs}")
            logger.info(f"[DEBUG] self.memory 类型: {type(self.memory)}")
        
        if not hasattr(self.memory, method_name):
            logger.error(f"[DEBUG] 方法不存在: {method_name}")
            raise AttributeError(f"Memory object has no attribute '{method_name}'")

        method = getattr(self.memory, method_name)
        
        if debug_config.should_log_debug():
            logger.info(f"[DEBUG] 方法存在: {method}")

        # 根据wasmtime-py API签名调用：
        # Memory.write(self, store, value, start=None) -> int
        # Memory.read(self, store, start=0, stop=None) -> bytearray
        try:
            if method_name == 'write':
                # write(store, value, start)
                if len(args) >= 2:
                    value = args[0]  # 第一个参数是value
                    start = args[1] if len(args) > 1 else None  # 第二个参数是start偏移量
                    if debug_config.should_log_debug():
                        logger.info(f"[DEBUG] 调用 write: store={self.store}, value={value}, start={start}")
                    result = method(self.store, value, start)
                else:
                    raise ValueError(f"write方法需要至少2个参数，得到{len(args)}个")
            elif method_name == 'read':
                # read(store, start, stop)
                start = args[0] if len(args) > 0 else 0
                stop = args[1] if len(args) > 1 else None
                if debug_config.should_log_debug():
                    logger.info(f"[DEBUG] 调用 read: store={self.store}, start={start}, stop={stop}")
                result = method(self.store, start, stop)
            else:
                # 其他方法，尝试带store参数
                result = method(self.store, *args, **kwargs)
            
            if debug_config.should_log_debug():
                logger.info(f"[DEBUG] 方法调用成功，返回类型: {type(result)}")
            return result
        except Exception as e:
            logger.error(f"[DEBUG] 方法调用失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise e

    def is_available(self) -> bool:
        try:
            # 确保 Engine 和 Store 已初始化
            if self.engine is None or self.store is None:
                logger.info("Engine 或 Store 未初始化，开始初始化...")
                self._initialize_core_components()
                
            # 直接用最小 WASM 模块的字节码
            wasm_bytes = (
                b"\x00asm\x01\x00\x00\x00"  # WASM 魔数和版本
                b"\x01\x07\x01\x60\x02\x7f\x7f\x01\x7f"  # 函数类型：两个i32参数，返回i32
                b"\x03\x02\x01\x00"  # 函数段：1个函数，类型索引0
                b"\x07\x07\x01\x03add\x00\x00"  # 导出段：导出函数"add"
                b"\x0a\x09\x01\x07\x00\x20\x00\x20\x01\x6a\x0b"  # 代码段：函数体
            )

            module = wasmtime.Module(self.engine, wasm_bytes)
            instance = wasmtime.Instance(self.store, module, [])

            return True
        except Exception as e:
            logger.error(f"Wasm runtime 不可用: {e}")
            return False

    def instantiate_module(self, module_id: str, wasm_bytes: bytes) -> bool:
        """实例化 Wasm 模块"""
        try:
            logger.info(f"开始实例化模块: {module_id}, WASM大小: {len(wasm_bytes)} 字节")
            
            # 确保 Engine 和 Store 已初始化
            if self.engine is None or self.store is None:
                logger.info("Engine 或 Store 未初始化，开始初始化...")
                self._initialize_core_components()

            # 创建模块
            module = wasmtime.Module(self.engine, wasm_bytes)
            logger.info(f"模块创建成功: {module_id}")

            # 获取模块的导入信息
            imports_info = module.imports
            logger.info(f"模块需要 {len(imports_info)} 个导入")

            # 打印导入信息用于调试
            for i, import_info in enumerate(imports_info):
                logger.info(f"导入 {i}: {import_info}")

            # 创建必要的导入函数
            imports = self._create_imports_for_module(imports_info)
            logger.info(f"创建了 {len(imports)} 个导入函数")

            # 尝试实例化
            instance = wasmtime.Instance(self.store, module, imports)
            self.instances[module_id] = instance
            
            # 修复：获取内存引用
            self._setup_memory_for_module(module_id)
            
            # 添加类型检查日志确认
            logger.info(f"模块实例化后 memory 类型: {type(self.memory)}")
            
            logger.info(f"成功实例化模块: {module_id}")
            return True
        except Exception as e:
            logger.error(f"实例化模块失败 {module_id}: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return False

    def _create_imports_for_module(self, imports_info) -> List[Any]:
        """根据模块的导入信息创建导入函数"""
        imports = []

        for import_info in imports_info:
            logger.info(f"处理导入: {import_info.module}.{import_info.name}")

            if import_info.module == "env":
                if import_info.name == "memory":
                    # 创建内存导入
                    self.memory = wasmtime.Memory(self.store, wasmtime.MemoryType(wasmtime.Limits(1, None)))
                    imports.append(self.memory)
                    logger.info("添加内存导入")
                elif import_info.name == "malloc":
                    # 创建malloc函数
                    def malloc(size: int) -> int:
                        """分配内存 - 线程安全的内存分配器"""
                        try:
                            logger.info(f"malloc被调用: size={size}")
                            
                            # 输入验证
                            if size <= 0:
                                logger.error(f"无效的内存分配大小: {size}")
                                return 0
                            
                            if size > 1024 * 1024:  # 限制单次分配不超过1MB
                                logger.error(f"内存分配过大: {size} 字节")
                                return 0
                            
                            if not self.memory:
                                logger.error("内存未初始化")
                                return 0
                            
                            # 线程安全的内存分配
                            with self._memory_lock:
                                # 确保分配器已初始化
                                if not hasattr(self, '_allocated_memory'):
                                    self._allocated_memory = 0x1000  # 起始偏移量
                                    self._allocations = {}  # 跟踪分配的内存 {address: {size, allocated_at, thread_id}}
                                    self._free_list = []  # 空闲内存列表 [(address, size), ...]
                                
                                # 内存对齐（8字节对齐）
                                aligned_size = (size + 7) & ~7
                                
                                # 检查是否有足够的内存
                                memory_size = self.memory.size(self.store) * 65536  # 页大小
                                required_memory = self._next_memory_address + aligned_size
                                
                                # 边界检查和内存扩展
                                if required_memory > memory_size:
                                    pages_needed = (required_memory + 65535) // 65536
                                    current_pages = self.memory.size(self.store)
                                    
                                    if pages_needed > current_pages:
                                        pages_to_add = pages_needed - current_pages
                                        self.memory.grow(self.store, pages_to_add)
                                        logger.info(f"内存扩展成功: {current_pages} -> {pages_needed} 页")
                                
                                # 分配内存地址（使用线程安全的地址分配器）
                                allocated_address = self._next_memory_address
                                self._next_memory_address += aligned_size
                                
                                # 记录分配信息用于调试和释放
                                self._allocations[allocated_address] = {
                                    'size': aligned_size,
                                    'requested_size': size,
                                    'allocated_at': time.time(),
                                    'thread_id': threading.current_thread().ident,
                                    'status': 'allocated'
                                }
                                
                                logger.info(f"内存分配成功: 地址=0x{allocated_address:04x}, 大小={aligned_size} 字节")
                                return allocated_address
                        except Exception as e:
                            logger.error(f"malloc失败: {e}")
                            import traceback
                            logger.error(f"malloc详细错误: {traceback.format_exc()}")
                            return 0

                    malloc_func = wasmtime.Func(self.store,
                                                wasmtime.FuncType([wasmtime.ValType.i32()], [wasmtime.ValType.i32()]),
                                                malloc)
                    imports.append(malloc_func)
                    logger.info("添加malloc函数")
                    logger.info(f"malloc函数类型: {malloc_func.type(self.store)}")
                elif import_info.name == "free":
                    # 创建free函数
                    def free(ptr: int) -> None:
                        """释放内存 - 线程安全的内存释放"""
                        try:
                            logger.info(f"free被调用: ptr={ptr}")
                            
                            # 输入验证
                            if ptr == 0:
                                logger.warning("尝试释放空指针")
                                return
                            
                            if not hasattr(self, '_allocations'):
                                logger.error("内存分配表未初始化")
                                return
                            
                            #  关键修复：对整个释放过程加锁保护
                            with self._memory_lock:
                                if ptr in self._allocations:
                                    #  修复：正确获取分配信息和尺寸
                                    allocation_info = self._allocations[ptr]
                                    size = allocation_info['size']
                                    logger.info(f"free释放内存: 偏移={ptr}, 大小={size}, 分配信息: {allocation_info}")
                                    
                                    # 将内存清零以防止数据泄露
                                    try:
                                        memory_data = self.memory.data(self.store)
                                        if ptr + size <= len(memory_data):
                                            memory_data[ptr:ptr + size] = b'\x00' * size
                                    except Exception as e:
                                        logger.warning(f"内存清零失败: {e}")
                                    
                                    # 从分配表中移除
                                    del self._allocations[ptr]
                                    
                                    # 添加到空闲列表（简单的内存回收策略）
                                    if not hasattr(self, '_free_list'):
                                        self._free_list = []
                                    self._free_list.append((ptr, size))
                                    
                                    logger.debug(f"内存已释放并添加到空闲列表: ptr={ptr}, size={size}")
                                    
                                    # 内存使用监控
                                    if hasattr(self, '_allocations'):
                                        #  修复：正确计算总分配内存，迭代分配信息字典
                                        total_allocated = sum(allocation['size'] for allocation in self._allocations.values())
                                        memory_size = self.memory.size(self.store) * 65536
                                        logger.info(f"释放后内存使用: {total_allocated} 字节, 总内存: {memory_size} 字节, 使用率: {total_allocated/memory_size*100:.1f}%")
                                else:
                                    logger.warning(f"尝试释放未分配的内存: {ptr}")
                                    # 检查是否在空闲列表中
                                    if hasattr(self, '_free_list'):
                                        for i, (free_ptr, free_size) in enumerate(self._free_list):
                                            if free_ptr == ptr:
                                                logger.warning(f"尝试重复释放已释放的内存: {ptr}")
                                                return
                                
                        except Exception as e:
                            logger.error(f"free失败: {e}")
                            import traceback
                            logger.error(f"free详细错误: {traceback.format_exc()}")

                    free_func = wasmtime.Func(self.store, wasmtime.FuncType([wasmtime.ValType.i32()], []), free)
                    imports.append(free_func)
                    logger.info("添加free函数")
                elif import_info.name == "call_mcp_tool_host":
                    # 创建MCP工具调用函数
                    def call_mcp_tool(tool_name_ptr: int, tool_name_len: int, parameters_ptr: int, parameters_len: int,
                                     response_ptr: int, response_len_ptr: int) -> int:
                        return self._handle_mcp_tool_call(tool_name_ptr, tool_name_len, parameters_ptr, parameters_len, response_ptr, response_len_ptr)
                    
                    call_mcp_tool_func = wasmtime.Func(self.store, 
                                                     wasmtime.FuncType([wasmtime.ValType.i32(), wasmtime.ValType.i32(), 
                                                                     wasmtime.ValType.i32(), wasmtime.ValType.i32(),
                                                                     wasmtime.ValType.i32(), wasmtime.ValType.i32()], 
                                                                     [wasmtime.ValType.i32()]), 
                                                     call_mcp_tool)
                    imports.append(call_mcp_tool_func)
                    logger.info("添加call_mcp_tool_host函数")
                else:
                    # 为其他未知导入创建占位符函数
                    logger.warning(f"未知导入: {import_info.name}")
                    # 根据导入类型创建相应的占位符函数
                    if hasattr(import_info, 'ty') and hasattr(import_info.ty, 'params'):
                        param_types = [wasmtime.ValType.i32() for _ in import_info.ty.params]
                        result_types = [wasmtime.ValType.i32() for _ in import_info.ty.results] if hasattr(
                            import_info.ty, 'results') else []

                        def placeholder_func(caller, *args):
                            return 0 if result_types else None

                        placeholder = wasmtime.Func(self.store, wasmtime.FuncType(param_types, result_types),
                                                    placeholder_func)
                        imports.append(placeholder)
                        logger.info(f"添加占位符函数: {import_info.name}")
            else:
                logger.warning(f"未知模块: {import_info.module}")

        return imports

    def _handle_mcp_tool_call(self, tool_name_ptr: int, tool_name_len: int, 
                             parameters_ptr: int, parameters_len: int, response_ptr: int, 
                             response_len_ptr: int) -> int:
        """处理MCP工具调用的通用方法"""
        try:
            logger.info(f"开始处理MCP工具调用")
            logger.info(f"参数: tool_name_ptr={tool_name_ptr}, tool_name_len={tool_name_len}, parameters_ptr={parameters_ptr}, parameters_len={parameters_len}")
            logger.info(f"response_ptr={response_ptr}, response_len_ptr={response_len_ptr}")
            
            # 检查内存对象类型
            if not hasattr(self.memory, "read"):
                logger.error("self.memory 不是 Memory 对象，无法读取。可能被赋值为 int。")
                raise RuntimeError(f"Invalid memory object for reading: {type(self.memory)}")
            
            # 从WASM内存中读取工具名称
            logger.info(f"[DEBUG] 调用 memory.read 前 (tool_name): tool_name_ptr={tool_name_ptr} (type: {type(tool_name_ptr)}), tool_name_len={tool_name_len} (type: {type(tool_name_len)})")
            tool_name_bytes = self._debug_memory_call('read', tool_name_ptr, tool_name_ptr + tool_name_len)
            tool_name = tool_name_bytes.decode('utf-8')
            logger.info(f"读取工具名称: {tool_name}")
            
            # 从WASM内存中读取参数
            parameters = {}
            if parameters_len > 0:
                logger.info(f"[DEBUG] 调用 memory.read 前 (parameters): parameters_ptr={parameters_ptr} (type: {type(parameters_ptr)}), parameters_len={parameters_len} (type: {type(parameters_len)})")
                parameters_bytes = self._debug_memory_call('read', parameters_ptr, parameters_ptr + parameters_len)
                parameters_str = parameters_bytes.decode('utf-8')
                logger.info(f"读取参数: {parameters_str}")
                if parameters_str.strip():
                    try:
                        parameters = json.loads(parameters_str)
                        logger.info(f"解析参数成功: {parameters}")
                    except json.JSONDecodeError:
                        logger.warning(f"无法解析参数JSON: {parameters_str}")
            
            # 执行MCP工具调用
            logger.info(f"开始执行MCP工具调用: {tool_name}")
            # 开始wasm_api阶段统计
            api_start_time = start_stage_tracking("wasm_api")
            response_data = self._execute_mcp_tool_call(tool_name, parameters)
            # 结束wasm_api阶段统计
            request_bytes = len(json.dumps({"tool": tool_name, "parameters": parameters}).encode('utf-8'))
            response_bytes = len(response_data.encode('utf-8'))
            logger.info(f"wasm_api阶段统计: 请求字节={request_bytes}, 响应字节={response_bytes}")
            end_stage_tracking("wasm_api", api_start_time, request_bytes, response_bytes)
            logger.info(f"MCP工具调用响应: {response_data}")
            
            # 将响应写入WASM内存
            response_bytes = response_data.encode('utf-8')
            response_len = len(response_bytes)
            logger.info(f"响应数据长度: {response_len}")
            
            # 确保有足够的内存空间
            if response_ptr + response_len > self.memory.size(self.store) * 65536:  # 65536是页大小
                logger.error("响应数据太大，无法写入WASM内存")
                return 0
            
            # 检查内存对象类型
            if not hasattr(self.memory, "write"):
                logger.error("self.memory 不是 Memory 对象，无法写入。可能被赋值为 int。")
                raise RuntimeError(f"Invalid memory object for writing: {type(self.memory)}")
            
            logger.info(f"[DEBUG] 调用 memory.write 前 (response): response_ptr={response_ptr} (type: {type(response_ptr)}), response_bytes_len={len(response_bytes)} (type: {type(response_bytes)})")
            self._debug_memory_call('write', response_bytes, response_ptr)
            logger.info(f"响应数据已写入内存位置: {response_ptr}")
            
            # 写入响应长度
            response_len_bytes = response_len.to_bytes(4, byteorder='little')
            logger.info(f"[DEBUG] 调用 memory.write 前 (response_len): response_len_ptr={response_len_ptr} (type: {type(response_len_ptr)}), response_len_bytes_len={len(response_len_bytes)} (type: {type(response_len_bytes)})")
            self._debug_memory_call('write', response_len_bytes, response_len_ptr)
            logger.info(f"响应长度已写入内存位置: {response_len_ptr}")
            
            logger.info(f"MCP工具调用成功: {tool_name}")
            return 1  # 成功
            
        except Exception as e:
            logger.error(f"MCP工具调用失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return 0  # 失败

    def _execute_mcp_tool_call_with_q_history(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """执行MCP工具调用 - 重构版本：支持Q_history缓存和增量执行"""
        try:
            logger.info(f"执行MCP工具调用: {tool_name}")
            
            # 检查是否有修复后的API参数（增量执行模式）
            fixed_params = self.get_fixed_api_params()
            if fixed_params and tool_name in fixed_params:
                logger.info(f"🔧 使用修复后的API参数: {tool_name}")
                # 使用修复后的参数覆盖原始参数
                parameters = fixed_params[tool_name]
                logger.info(f"修复后的参数: {parameters}")
            
            # 检查Q_history中是否有匹配的未执行记录
            if hasattr(self, 'history_manager') and self.history_manager:
                if self.execution_mode == "write_mode":
                    denied = self.write_replay_policy_denied_json(tool_name, parameters)
                    if denied is not None:
                        logger.warning(
                            "WRITE replay 策略拒绝(with_q_history): tool=%s",
                            tool_name,
                        )
                        return denied
                cached_record = self.history_manager.find_in_q_history(tool_name, parameters)
                if cached_record:
                    logger.info(f"从Q_history获取缓存结果: {tool_name}")
                    self.history_manager.mark_as_executed(cached_record)
                    return json.dumps(cached_record.result, ensure_ascii=False)
            
            # 执行实际的MCP调用
            result = self._perform_actual_mcp_call(tool_name, parameters)
            
            # 如果是@WRITE操作，添加到Q_working
            if self.execution_mode == "write_mode" and hasattr(self, 'history_manager') and self.history_manager:
                self.history_manager.add_to_q_working(tool_name, parameters, result)
            
            return json.dumps(result, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"执行MCP工具调用失败: {e}")
            
            # 如果是MCP工具调用错误，尝试调试
            if not hasattr(self, 'mcp_debug_manager'):
                self.mcp_debug_manager = None
                
            if self.mcp_debug_manager and self.execution_mode == "write_mode":
                logger.info(f"开始MCP调试: {tool_name}")
                try:
                    debug_response = self.event_loop.run_until_complete(
                        self.mcp_debug_manager.debug_mcp_call(
                            tool_name, parameters, str(e), ""
                        )
                    )
                    
                    if debug_response and debug_response.get("success", True):
                        logger.info(f"MCP调试成功: {tool_name}")
                        # 记录调试成功的调用到Q_working
                        if hasattr(self, 'history_manager') and self.history_manager:
                            self.history_manager.add_to_q_working(tool_name, parameters, debug_response)
                        result = json.dumps(debug_response, ensure_ascii=False)
                        return result
                    else:
                        logger.error(f"MCP调试失败: {tool_name}")
                except Exception as debug_error:
                    logger.error(f"MCP调试过程异常: {debug_error}")
            
            error_response = json.dumps({
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "parameters": parameters
            })
            return error_response
    
    def _execute_mcp_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """执行MCP工具调用 - 重构版本：支持Q_history缓存复用"""
        try:
            logger.info(f"🔍 准备执行MCP工具调用: {tool_name}")
            
            if not hasattr(self, 'execution_mode') or self.execution_mode is None:
                logger.warning("ExecutionMode未初始化，设置为read_only")
                self.execution_mode = "read_only"
            
            # 关键修复：在write_mode下，优先检查Q_history缓存
            if self.execution_mode == "write_mode":
                denied = self.write_replay_policy_denied_json(tool_name, parameters)
                if denied is not None:
                    logger.warning(
                        "WRITE replay 策略拒绝: tool=%s (在 Q_history 查找前短路)",
                        tool_name,
                    )
                    return denied
                logger.info(f"🔍 检查Q_history缓存: {tool_name}")
                cached_record = self.history_manager.find_in_q_history(tool_name, parameters)
                if cached_record:
                    logger.info(f"✅ 从Q_history获取缓存结果: {tool_name} (避免重复API调用)")
                    logger.info(f"📊 缓存记录状态: executed={cached_record.executed}")
                    
                    # 标记为已执行
                    self.history_manager.mark_as_executed(cached_record)
                    
                    # 返回缓存的结果
                    cached_result = json.dumps(cached_record.result, ensure_ascii=False)
                    logger.info(f"🔄 使用缓存结果: {cached_result[:100]}...")
                    return cached_result
                else:
                    logger.info(f"❌ Q_history中未找到缓存记录: {tool_name}")
            
            # 执行实际的MCP工具调用
            logger.info(f"🚀 执行新的MCP工具调用: {tool_name}")
            response_data = self._perform_actual_mcp_call(tool_name, parameters)
            
            # 如果是写入模式且调用成功，记录到Q_working
            if self.execution_mode == "write_mode" and response_data and response_data.get("success", True):
                logger.info(f"📝 记录MCP工具调用到Q_working: {tool_name}")
                self.history_manager.add_to_q_working(tool_name, parameters, response_data)
                
                # 获取Q_working状态用于调试
                q_status = self.history_manager.get_q_history_status()
                logger.info(f"📊 Q_working状态: {q_status}")
            
            result = json.dumps(response_data, ensure_ascii=False)
            return result
                
        except Exception as e:
            logger.error(f"❌ 执行MCP工具调用失败: {e}")
            
            # 如果是MCP工具调用错误，尝试调试
            if not hasattr(self, 'mcp_debug_manager'):
                self.mcp_debug_manager = None
                
            if self.mcp_debug_manager and self.execution_mode == "write_mode":
                logger.info(f"🔧 开始MCP调试: {tool_name}")
                try:
                    debug_response = self.event_loop.run_until_complete(
                        self.mcp_debug_manager.debug_mcp_call(
                            tool_name, parameters, str(e), ""
                        )
                    )
                    
                    if debug_response and debug_response.get("success", True):
                        logger.info(f"✅ MCP调试成功: {tool_name}")
                        # 记录调试成功的调用到Q_working
                        if hasattr(self, 'history_manager') and self.history_manager:
                            self.history_manager.add_to_q_working(tool_name, parameters, debug_response)
                        result = json.dumps(debug_response, ensure_ascii=False)
                        return result
                    else:
                        logger.error(f"❌ MCP调试失败: {tool_name}")
                except Exception as debug_error:
                    logger.error(f"❌ MCP调试过程异常: {debug_error}")
            
            error_response = json.dumps({
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "parameters": parameters
            })
            return error_response
    
    def _perform_actual_mcp_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行实际的MCP工具调用"""
        try:
            # 检查SessionManager是否可用，如果不可用则尝试重新初始化
            if not self.is_session_manager_available():
                logger.warning(f"SessionManager不可用，尝试重新初始化 - 线程ID: {self.thread_id}")
                init_success = self.initialize_session_manager_if_needed()
                if not init_success:
                    logger.error(
                        "SessionManager 不可用且重试失败，拒绝 MCP 占位成功 "
                        "(tool=%s) - 线程ID: %s",
                        tool_name,
                        self.thread_id,
                    )
                    return {
                        "success": False,
                        "error": "session_manager_unavailable_after_retry",
                        "tool": tool_name,
                        "parameters": parameters,
                        "note": "MCP 不可用；禁止返回伪成功以免 Guest 误判已写库",
                    }
                else:
                    logger.info(f"SessionManager重新初始化成功 - 线程ID: {self.thread_id}")
            
            # 异步调用
            async def call_mcp_tool_async():
                try:
                    logger.info(f"开始调用MCP工具: {tool_name}")
                    
                    # 防护性检查：确保SessionManager可用（在异步函数内部再次检查）
                    if not self.is_session_manager_available():
                        logger.warning("异步函数内SessionManager不可用，无法执行MCP工具调用")
                        # 注意：这里无法调用initialize_session_manager_if_needed，因为在异步函数内部
                        # 主要的重新初始化应该在调用异步函数之前完成
                        raise AttributeError("SessionManager未初始化")
                    
                    # 检查SessionManager的健康状态
                    if hasattr(self.session_manager, 'is_healthy'):
                        try:
                            health_status = await self.session_manager.is_healthy()
                            logger.debug(f"SessionManager健康状态: {health_status}")
                        except Exception as health_error:
                            logger.warning(f"检查SessionManager健康状态失败: {health_error}")
                    
                    # 执行MCP工具调用 - 增加超时时间，添加连接状态检查
                    start_time = time.time()
                    
                    # 检查服务器进程状态
                    if hasattr(self.session_manager, 'servers') and 'local_apis' in self.session_manager.servers:
                        client_core = self.session_manager.servers['local_apis']
                        if hasattr(client_core, 'process') and client_core.process and client_core.process.poll() is not None:
                            logger.error(f"MCP服务器进程已退出，退出码: {client_core.process.returncode}")
                            return {
                                "error": "MCP服务器进程已退出",
                                "success": False,
                                "tool": tool_name,
                                "process_exit": True
                            }
                    
                    _to = mcp_call_tool_timeout_seconds()
                    mcp_result = await asyncio.wait_for(
                        self.session_manager.call_tool("local_apis", tool_name, parameters),
                        timeout=_to,
                    )
                    
                    duration = time.time() - start_time
                    logger.info(f"MCP工具调用成功: {tool_name}, 耗时: {duration:.2f}秒")
                    
                    return mcp_result
                    
                except asyncio.TimeoutError:
                    logger.error(f"MCP工具调用超时: {tool_name}")
                    return {
                        "error": "调用超时",
                        "success": False,
                        "tool": tool_name,
                        "timeout": True
                    }
                except Exception as e:
                    logger.error(f"MCP工具调用失败: {tool_name}, 错误: {e}")
                    return {
                        "error": str(e),
                        "success": False,
                        "tool": tool_name,
                        "error_type": type(e).__name__
                    }
            
            # 使用统一的事件循环执行异步代码
            el = self.event_loop
            if el is None or (hasattr(el, "is_closed") and el.is_closed()):
                logger.warning(
                    "MCP 调用前 event_loop 不可用，尝试重建 SessionManager "
                    f"- 线程ID: {self.thread_id}"
                )
                self.session_manager = None
                self.mcp_debug_manager = None
                self.event_loop = None
                if not self.initialize_session_manager_if_needed():
                    return {
                        "error": "event_loop_invalid_and_session_reinit_failed",
                        "success": False,
                        "tool": tool_name,
                    }
                el = self.event_loop
            if el and not (hasattr(el, "is_closed") and el.is_closed()):
                result = el.run_until_complete(call_mcp_tool_async())
                return result
            logger.error(f"没有可用事件循环 - 线程ID: {self.thread_id}")
            return {
                "error": "没有事件循环可用",
                "success": False,
                "tool": tool_name
            }
                
        except Exception as e:
            logger.error(f"实际MCP调用异常: {e}")
            return {
                "error": str(e),
                "success": False,
                "tool": tool_name,
                "error_type": type(e).__name__
            }

    def _setup_memory_for_module(self, module_id: str):
        """为模块设置内存引用"""
        try:
            instance = self.instances[module_id]
            exports = instance.exports(self.store)
            
            # 检查是否有内存导出
            if "memory" in exports:
                self.memory = exports["memory"]
                logger.info(f"已设置内存引用: {module_id}")
                # 通过 debug 确认 type(self.memory) 是 wasmtime.Memory
                logger.info(f"内存对象类型: {type(self.memory)}")
            else:
                logger.warning(f"模块 {module_id} 没有导出内存")
        except Exception as e:
            logger.error(f"设置内存引用失败 {module_id}: {e}")

    def execute_with_mode_detection(self, module_id: str, function_name: str, 
                                   args: List[Any] = None, source_code: str = None) -> Dict[str, Any]:
        """简化版的执行模式检测（移除模拟执行逻辑）"""
        try:
            # 分析代码中的读写操作
            if source_code:
                analysis = self.analyze_code_for_read_write_operations(source_code)
                self.execution_mode = analysis["execution_mode"]
                logger.info(f"检测到执行模式: {self.execution_mode}")
            else:
                # 如果没有源代码，默认使用读取模式
                self.execution_mode = "read_only"
            
            # 直接调用call_function，让MCP工具调用历史缓存机制处理
            return self.call_function(module_id, function_name, args)
                
        except Exception as e:
            logger.error(f"执行模式检测失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_mode": getattr(self, 'execution_mode', 'unknown')
            }
    
    
    def _execute_real(self, module_id: str, function_name: str, args: List[Any] = None) -> Dict[str, Any]:
        """直接真实执行（统一为call_function）"""
        return self.call_function(module_id, function_name, args)

    def call_function(self, module_id: str, function_name: str,
                      args: List[Any] = None) -> Any:
        """调用 Wasm 模块中的函数 -  已集成历史缓存"""
        if module_id not in self.instances:
            raise ValueError(f"模块 {module_id} 未实例化")

        instance = self.instances[module_id]
        
        # 修复：正确获取导出的函数
        try:
            # 调用exports()方法获取InstanceExports对象
            exports = instance.exports(self.store)
            logger.debug(f"exports 类型: {type(exports)}")
            logger.debug(f"可用的导出函数: {list(exports.keys())}")
            
            # 通过字典访问获取函数
            func = exports[function_name]
            logger.debug(f"找到函数: {function_name}, 类型: {type(func)}")
            
        except KeyError as e:
            logger.error(f"函数 {function_name} 不存在")
            logger.error(f"可用的导出: {list(exports.keys())}")
            raise ValueError(f"函数 {function_name} 不存在: {e}")
        except Exception as e:
            logger.error(f"获取导出函数失败: {e}")
            raise

        if args is None:
            args = []

        try:
            if function_name == "execute":
                # 特殊处理execute函数，它需要字符串参数
                if len(args) != 1:
                    raise ValueError("execute函数需要1个字符串参数")

                input_str = str(args[0])
                input_bytes = input_str.encode('utf-8')
                input_len = len(input_bytes)
                
                logger.debug(f"调用execute函数，输入长度: {input_len}")

                # 修复：正确调用execute函数
                # 在wasmtime中，我们需要将字节数组写入内存，然后传递指针和长度
                if not self.memory:
                    raise RuntimeError("内存未初始化")
                
                # 线程安全的内存分配和写入
                memory_offset = self._allocate_thread_safe_memory(len(input_bytes))
                
                # debug: 确保 memory 不是整数
                logger.info(f"[DEBUG] memory object before write: type={type(self.memory)}, repr={repr(self.memory)}")
                if not hasattr(self.memory, "write"):
                    logger.error("self.memory 不是 Memory 对象，无法写入。可能被赋值为 int。")
                    raise RuntimeError(f"Invalid memory object: {type(self.memory)}")
                
                logger.info(f"准备写入内存: memory_offset={memory_offset}, input_len={input_len}, 类型: {type(input_len)}")
                logger.info(f"input_bytes类型: {type(input_bytes)}, 长度: {len(input_bytes)}")
                
                try:
                    logger.info(f"[DEBUG] 调用 memory.write 前: memory_offset={memory_offset} (type: {type(memory_offset)}), input_bytes_len={len(input_bytes)} (type: {type(input_bytes)})")
                    logger.info(f"[DEBUG] self.memory 类型: {type(self.memory)}, 是否有 write 方法: {hasattr(self.memory, 'write')}")
                    self._debug_memory_call('write', input_bytes, memory_offset)
                    logger.info("内存写入成功")
                except Exception as e:
                    logger.error(f"内存写入失败: {e}")
                    logger.error(f"[DEBUG] 错误发生时的参数: memory_offset={memory_offset}, input_bytes_len={len(input_bytes)}")
                    logger.error(f"[DEBUG] self.memory 详细信息: type={type(self.memory)}, repr={repr(self.memory)}")
                    import traceback
                    logger.error(f"[DEBUG] 完整错误堆栈: {traceback.format_exc()}")
                    raise
                
                # 确保参数是整数类型
                if not isinstance(memory_offset, int):
                    memory_offset = int(memory_offset)
                if not isinstance(input_len, int):
                    input_len = int(input_len)
                
                logger.info(f"调用execute函数: memory_offset={memory_offset}, input_len={input_len}")
                logger.info(f"func类型: {type(func)}")
                logger.info(f"store类型: {type(self.store)}")
                
                # 调用execute函数，传递指针和长度作为整数
                try:
                    result_len = func(self.store, memory_offset, input_len)
                    logger.info("execute函数调用成功")
                except Exception as e:
                    logger.error(f"execute函数调用失败: {e}")
                    import traceback
                    logger.error(f"详细错误信息: {traceback.format_exc()}")
                    raise
                logger.info(f"execute函数返回长度: {result_len}, 类型: {type(result_len)}")
                
                # 确保 result_len 是整数
                if hasattr(result_len, 'value'):
                    result_len = result_len.value
                elif not isinstance(result_len, int):
                    result_len = int(result_len) if result_len else 0
                
                logger.info(f"处理后的result_len: {result_len}, 类型: {type(result_len)}")

                if result_len and result_len > 0:
                    # 使用get_result函数获取结果字符串
                    try:
                        # 获取get_result函数
                        exports = instance.exports(self.store)
                        get_result_func = exports.get("get_result")
                        
                        if get_result_func:
                            result_ptr = get_result_func(self.store)
                            logger.info(f"get_result返回指针: {result_ptr}, 类型: {type(result_ptr)}")
                            
                            # 确保 result_ptr 是整数
                            if hasattr(result_ptr, 'value'):
                                result_ptr = result_ptr.value
                            elif not isinstance(result_ptr, int):
                                result_ptr = int(result_ptr) if result_ptr else 0
                            
                            logger.info(f"处理后的result_ptr: {result_ptr}, 类型: {type(result_ptr)}")
                            
                            if result_ptr == 0:
                                logger.error("get_result返回空指针")
                                return "{}"
                            
                            if result_ptr and result_ptr != 0:
                                # 从内存中读取结果字符串，使用实际长度而不是固定长度
                                logger.info(f"准备读取内存: result_ptr={result_ptr}, result_len={result_len}, 类型: {type(result_len)}")
                                
                                # 确保 result_len 是正整数
                                if not isinstance(result_len, int) or result_len <= 0:
                                    logger.error(f"无效的result_len: {result_len}, 类型: {type(result_len)}")
                                    return "{}"
                                
                                # 检查内存对象类型
                                if not hasattr(self.memory, "read"):
                                    logger.error("self.memory 不是 Memory 对象，无法读取结果。可能被赋值为 int。")
                                    raise RuntimeError(f"Invalid memory object for reading result: {type(self.memory)}")
                                
                                logger.info(f"[DEBUG] 调用 memory.read 前 (result): result_ptr={result_ptr} (type: {type(result_ptr)}), result_len={result_len} (type: {type(result_len)})")
                                result_bytes = self._debug_memory_call('read', result_ptr, result_ptr + result_len)
                                logger.info(f"从内存读取的原始字节类型: {type(result_bytes)}")
                                logger.info(f"从内存读取的原始字节长度: {len(result_bytes) if hasattr(result_bytes, '__len__') else 'N/A'}")
                                
                                # 安全地显示前100字节
                                try:
                                    if hasattr(result_bytes, '__getitem__'):
                                        preview = result_bytes[:100] if len(result_bytes) > 100 else result_bytes
                                        logger.info(f"从内存读取的原始字节: {preview}...")
                                    else:
                                        logger.info(f"从内存读取的原始字节: {result_bytes}")
                                except Exception as e:
                                    logger.error(f"显示字节预览失败: {e}")
                                    logger.info(f"从内存读取的原始字节: {result_bytes}")
                                
                                # 查找字符串结束位置
                                try:
                                    if hasattr(result_bytes, 'find'):
                                        null_pos = result_bytes.find(b'\0')
                                        if null_pos != -1:
                                            if hasattr(result_bytes, '__getitem__'):
                                                result_bytes = result_bytes[:null_pos]
                                            logger.info(f"找到null终止符，位置: {null_pos}")
                                        else:
                                            logger.info(f"未找到null终止符，使用全部字节")
                                    else:
                                        logger.info(f"result_bytes不支持find操作，使用全部字节")
                                except Exception as e:
                                    logger.error(f"处理null终止符时出错: {e}")
                                    logger.info(f"使用全部字节")
                                
                                try:
                                    result_str = result_bytes.decode('utf-8')
                                    logger.info(f"解码后的字符串长度: {len(result_str)}")
                                    logger.info(f"成功调用函数 {function_name}，参数: {args}")
                                    logger.info(f"执行结果: {result_str}")
                                    
                                    # 尝试解析为JSON，如果成功则返回解析后的数据
                                    try:
                                        import json
                                        parsed_result = json.loads(result_str)
                                        logger.info(f"解析为JSON成功，数据类型: {type(parsed_result)}")
                                        return parsed_result
                                    except json.JSONDecodeError:
                                        logger.info("结果不是有效的JSON，返回原始字符串")
                                        return result_str
                                except UnicodeDecodeError as e:
                                    logger.error(f"字符串解码失败: {e}")
                                    logger.error(f"原始字节: {result_bytes}")
                                    return "{}"
                            else:
                                logger.error("get_result函数返回空指针")
                                return "{}"
                        else:
                            logger.error("未找到get_result函数")
                            return "{}"
                    except Exception as e:
                        logger.error(f"获取结果失败: {e}")
                        return "{}"
                else:
                    logger.error(f"execute函数返回无效长度: {result_len}")
                    return "{}"
            else:
                # 其他函数的常规调用
                result = func(self.store, *args)
                logger.info(f"成功调用函数 {function_name}，参数: {args}")
                return result
        except Exception as e:
            logger.error(f"调用函数失败 {function_name}: {e}")
            raise

    def get_exported_functions(self, module_id: str) -> List[str]:
        """获取模块导出的函数列表"""
        if module_id not in self.instances:
            return []

        instance = self.instances[module_id]
        
        try:
            # 调用exports()方法获取InstanceExports对象
            exports = instance.exports(self.store)
            return list(exports.keys())
        except Exception as e:
            logger.error(f"获取导出函数列表失败: {e}")
            return []

    def cleanup_module(self, module_id: str) -> bool:
        """清理指定的模块"""
        if module_id in self.instances:
            del self.instances[module_id]
            logger.info(f"已清理模块: {module_id}")
            return True
        return False
    
    def cleanup_memory(self):
        """ 清理内存分配信息 - 完善版本"""
        try:
            with self._memory_lock:
                #  修复：安全计算总分配内存，防止KeyError
                total_allocated = sum(allocation.get('size', 0) for allocation in self._allocations.values()) if self._allocations else 0
                logger.info(f"清理前内存使用: {total_allocated} 字节")
                
                #  修复：使用_free_list确保高效清理
                total_free_space = sum(size for _, size in self._free_list) if self._free_list else 0
                logger.info(f"清理前自由内存: {total_free_space} 字节")
                
                # 清零所有分配的内存
                if self.memory and self._allocations:
                    memory_data = self.memory.data(self.store)
                    for ptr, allocation_info in self._allocations.items():
                        try:
                            #  修复：安全获取size，防止KeyError
                            size = allocation_info.get('size', 0)
                            if size > 0 and ptr + size <= len(memory_data):
                                memory_data[ptr:ptr + size] = b'\x00' * size
                                logger.debug(f"清零内存块: ptr=0x{ptr:04x}, 大小={size} 字节")
                        except Exception as e:
                            logger.warning(f"清理内存块失败: ptr={ptr}, allocation_info={allocation_info}, error={e}")
                
                #  修复：完善内存清理流程
                # 1. 清空分配表
                self._allocations.clear()
                
                # 2. 清空自由列表
                if hasattr(self, '_free_list'):
                    self._free_list.clear()
                
                # 3. 重置内存分配器状态
                self._next_memory_address = 0x1000
                
                # 4. 记录清理统计
                cleanup_total = total_allocated + total_free_space
                logger.info(f"🧹 WASM内存清理完成")
                logger.info(f"📊 清理统计: 分配内存={total_allocated}字节, 自由内存={total_free_space}字节, 总计={cleanup_total}字节")
                
        except Exception as e:
            logger.error(f"清理WASM内存失败: {e}")
            import traceback
            logger.error(f"内存清理详细错误: {traceback.format_exc()}")


    def cleanup_session_manager(self):
        """完全清理SessionManager实例"""
        try:
            if hasattr(self, 'session_manager') and self.session_manager:
                logger.info(f"开始清理SessionManager - 线程ID: {self.thread_id}")
                
                # 在事件循环中关闭SessionManager
                if self.event_loop and not self.event_loop.is_closed():
                    try:
                        if not self.event_loop.is_running():
                            # 如果事件循环没有运行，可以安全地使用run_until_complete
                            self.event_loop.run_until_complete(self.session_manager.shutdown())
                            logger.info(f"SessionManager在事件循环中关闭成功 - 线程ID: {self.thread_id}")
                    except Exception as e:
                        logger.warning(f"在事件循环中关闭SessionManager失败: {e}，尝试其他方式")
                
                # 清理引用
                self.session_manager = None
                self.mcp_debug_manager = None
                
                logger.info(f"SessionManager清理完成 - 线程ID: {self.thread_id}")
            else:
                logger.info(f"SessionManager不需要清理（已经是None） - 线程ID: {self.thread_id}")
                
        except Exception as e:
            logger.error(f"清理SessionManager失败: {e}")
            
    def cleanup_all(self):
        """清理所有模块和SessionManager"""
        try:
            logger.info(f"开始完整清理WasmRuntime - 线程ID: {self.thread_id}")
            
            # 清理WASM实例和内存
            self.instances.clear()
            self.cleanup_memory()
            
            # 清理SessionManager
            self.cleanup_session_manager()
            
            # 关闭事件循环
            if self.event_loop and not self.event_loop.is_closed():
                try:
                    logger.info(f"正在关闭事件循环 - 线程ID: {self.thread_id}")
                    self.event_loop.close()
                    logger.info(f"事件循环已关闭 - 线程ID: {self.thread_id}")
                except Exception as e:
                    logger.error(f"关闭事件循环失败: {e}")
                self.event_loop = None
            
            logger.info(f"WasmRuntime完整清理完成 - 线程ID: {self.thread_id}")
            
        except Exception as e:
            logger.error(f"WasmRuntime清理过程中发生异常: {e}")
            import traceback
            logger.error(f"清理异常详情: {traceback.format_exc()}")
    
    def reset_for_new_transaction(self):
        """为新事务重置状态"""
        try:
            logger.info(f"为新事务重置WasmRuntime状态 - 线程ID: {self.thread_id}")
            
            # 清理当前事务状态
            self.current_transaction_id = None
            self.execution_mode = "unknown"
            
            # 清理内存但不清理SessionManager（保留复用）
            self.cleanup_memory()
            
            # 可选择性地清理WASM模块实例
            # 注释：通常保留模块实例，因为重新编译成本较高
            # self.instances.clear()
            
            logger.info(f"WasmRuntime事务状态重置完成 - 线程ID: {self.thread_id}")
            
        except Exception as e:
            logger.error(f"重置WasmRuntime状态失败: {e}")
            import traceback
            logger.error(f"状态重置异常详情: {traceback.format_exc()}")
    
    def _allocate_thread_safe_memory(self, size: int) -> int:
        """线程安全的内存分配方法 - 确保整个方法都是线程安全的"""
        #  关键修复：确保整个方法都在锁保护下
        with self._memory_lock:
            try:
                # 内存对齐（8字节对齐）
                aligned_size = (size + 7) & ~7
                
                # 检查是否有足够的内存
                memory_size = self.memory.size(self.store) * 65536
                required_memory = self._next_memory_address + aligned_size
                
                # 如果需要，扩展内存
                if required_memory > memory_size:
                    pages_needed = (required_memory + 65535) // 65536
                    current_pages = self.memory.size(self.store)
                    
                    if pages_needed > current_pages:
                        pages_to_add = pages_needed - current_pages
                        self.memory.grow(self.store, pages_to_add)
                        logger.info(f"内存扩展成功: {current_pages} -> {pages_needed} 页")
                
                # 分配内存地址
                allocated_address = self._next_memory_address
                self._next_memory_address += aligned_size
                
                logger.debug(f"线程安全内存分配: 地址=0x{allocated_address:04x}, 大小={aligned_size} 字节")
                return allocated_address
                
            except Exception as e:
                logger.error(f"线程安全内存分配失败: {e}")
                raise
