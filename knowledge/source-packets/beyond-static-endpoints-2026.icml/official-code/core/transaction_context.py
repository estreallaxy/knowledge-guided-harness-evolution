"""
线程安全的事务上下文管理器
确保事务状态的一致性和原子性
"""

import logging
import threading
import time
import asyncio
import uuid
from typing import Dict, Any, Optional, ContextManager
from contextlib import contextmanager
from .atomicity_manager import AtomicityManager, TransactionState
from config import Config

logger = logging.getLogger(__name__)


class TransactionContextManager:
    """线程安全的事务上下文管理器"""
    
    def __init__(self, atomicity_manager: AtomicityManager):
        self.atomicity_manager = atomicity_manager
        self._lock = threading.Lock()
        self._active_context = threading.local()
        #  新增加：事务成功后的回调机制
        self._post_commit_callbacks = {}
    
    def create_unified_transaction_id(self) -> str:
        """创建统一的事务ID，与历史管理器保持一致"""
        return str(uuid.uuid4())
    
    @contextmanager
    def transaction(self, source_code: str, user_input: str = "", wasm_runtime=None) -> ContextManager[Dict[str, Any]]:
        """事务上下文管理器 - 确保事务的原子性（统一事务管理：以WasmRuntime为主）"""
        
        transaction_id = None
        transaction_data = {}
        
        try:
            # 线程安全的创建事务
            with self._lock:
                # 让WasmRuntime先创建事务ID，然后同步到其他管理器
                if wasm_runtime:
                    # 让WasmRuntime创建事务ID
                    transaction_id = wasm_runtime._start_new_transaction_for_context(source_code)
                    logger.info(f"使用WasmRuntime创建的统一事务ID: {transaction_id}")
                else:
                    # 如果没有WasmRuntime，fallback到原来的方法
                    transaction_id = self.create_unified_transaction_id()
                    logger.warning("没有WasmRuntime实例，使用fallback事务ID创建方法")
                
                # 确保原子性管理器和历史管理器使用相同ID
                self.atomicity_manager.create_transaction_with_id(transaction_id, source_code, user_input)
                self.atomicity_manager.start_transaction(transaction_id)
            
            transaction_data = {
                "transaction_id": transaction_id,
                "wasm_runtime": wasm_runtime,
                "start_time": time.time(),
                "success": False,
                #  新增加：事务成功后的回调列表
                "post_commit_callbacks": []
            }
            
            logger.info(f"事务 {transaction_id} 开始")
            
            # 初始化WASM运行时事务状态（简化：因为WasmRuntime已经创建了事务）
            if wasm_runtime:
                self._sync_wasm_transaction_state(wasm_runtime, transaction_id)
            
            yield transaction_data
            
            # 如果没有发生异常，提交事务
            if wasm_runtime:
                self._commit_wasm_transaction(wasm_runtime, transaction_id)
            
            # 关键修复：使用安全的事务提交机制
            try:
                with self._lock:
                    # 预检查：如果事务已经完成，直接返回成功
                    if self.atomicity_manager.is_transaction_completed(transaction_id):
                        logger.info(f"事务 {transaction_id} 已处于最终状态，跳过提交")
                        transaction_data["success"] = True
                    else:
                        self.safe_commit_transaction(transaction_id)
                        
            except Exception as commit_error:
                logger.error(f"提交事务失败: {commit_error}")
                raise
            
            transaction_data["success"] = True
            logger.info(f"事务 {transaction_id} 成功提交")
            
            #  新增加：执行事务成功后的回调
            self._execute_post_commit_callbacks(transaction_data["post_commit_callbacks"])
            
        except Exception as e:
            # 发生异常时回滚事务
            logger.error(f"事务 {transaction_id} 失败: {e}")
            
            try:
                if wasm_runtime:
                    self._rollback_wasm_transaction(wasm_runtime, transaction_id)
                
                with self._lock:
                    # 异步回滚操作需要被正确等待
                    try:
                        transaction_config = Config.get_transaction_config()
                        rollback_timeout = transaction_config["rollback_timeout"]
                        
                        # 使用线程池执行异步回滚，避免事件循环冲突
                        import concurrent.futures
                        
                        def run_async_rollback():
                            """在线程池的新事件循环中运行异步回滚"""
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(
                                    asyncio.wait_for(
                                        self.atomicity_manager.rollback_transaction(transaction_id, str(e)),
                                        timeout=rollback_timeout
                                    )
                                )
                            finally:
                                loop.close()
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(run_async_rollback)
                            try:
                                result = future.result(timeout=rollback_timeout + 5)  # 额外5秒缓冲
                                logger.info(f"事务回滚完成: {transaction_id}")
                            except concurrent.futures.TimeoutError:
                                future.cancel()
                                logger.error(f"事务回滚超时: {transaction_id}")
                            except Exception as rollback_error:
                                logger.error(f"事务回滚异常: {transaction_id}, 错误: {rollback_error}")
                                
                    except Exception as rollback_error:
                        logger.error(f"事务回滚异常: {transaction_id}, 错误: {rollback_error}")
                    
            except Exception as rollback_error:
                logger.error(f"事务 {transaction_id} 回滚失败: {rollback_error}")
                
            # 重新抛出原始异常
            raise
            
        finally:
            # 清理资源
            try:
                if wasm_runtime and transaction_id:
                    self._cleanup_wasm_transaction(wasm_runtime, transaction_id)
            except Exception as cleanup_error:
                logger.error(f"事务 {transaction_id} 清理失败: {cleanup_error}")
    
    def _sync_wasm_transaction_state(self, wasm_runtime, transaction_id: str):
        """同步WASM运行时事务状态（简化版：因为WasmRuntime已经创建了事务）"""
        try:
            # 验证事务ID是否一致
            if hasattr(wasm_runtime, 'current_transaction_id') and wasm_runtime.current_transaction_id:
                if wasm_runtime.current_transaction_id != transaction_id:
                    logger.warning(f"事务ID不一致：WasmRuntime={wasm_runtime.current_transaction_id}, Expected={transaction_id}")
                else:
                    logger.debug(f"事务ID验证一致: {transaction_id}")
            else:
                logger.warning("WasmRuntime缺少当前事务ID")
            
            # 同步历史管理器状态（确保历史管理器也知道这个事务ID）
            if hasattr(wasm_runtime, 'history_manager') and wasm_runtime.history_manager:
                if hasattr(wasm_runtime.history_manager, 'current_transaction_id'):
                    wasm_runtime.history_manager.current_transaction_id = transaction_id
            
        except Exception as e:
            logger.error(f"同步WASM事务状态失败: {e}")
    
    def _commit_wasm_transaction(self, wasm_runtime, transaction_id: str):
        """提交WASM运行时事务"""
        try:
            if hasattr(wasm_runtime, '_end_transaction'):
                wasm_runtime._end_transaction(success=True)
            
            logger.info(f"WASM事务 {transaction_id} 已提交")
            
        except Exception as e:
            logger.error(f"提交WASM事务失败: {e}")
            raise
    
    def _rollback_wasm_transaction(self, wasm_runtime, transaction_id: str):
        """回滚WASM运行时事务"""
        try:
            # 防护性检查：确保WasmRuntime具有必要的属性和方法
            if not hasattr(wasm_runtime, '_end_transaction'):
                logger.warning(f"WasmRuntime缺少_end_transaction方法")
                return
            
            # 尝试回滚事务
            wasm_runtime._end_transaction(success=False)
            
            # 安全地清理执行模式
            if hasattr(wasm_runtime, 'current_transaction_id'):
                wasm_runtime.current_transaction_id = None
            
            logger.info(f"WASM事务 {transaction_id} 已回滚")
            
        except AttributeError as attr_error:
            logger.error(f"回滚WASM事务时属性错误: {attr_error}")
            # 尝试修复属性问题
            try:
                if hasattr(wasm_runtime, '_ensure_transaction_id'):
                    wasm_runtime._ensure_transaction_id()
                elif not hasattr(wasm_runtime, 'current_transaction_id'):
                    wasm_runtime.current_transaction_id = None
                logger.info(f"WASM事务属性已修复")
            except Exception as fix_error:
                logger.error(f"修复WASM事务属性失败: {fix_error}")
        except Exception as e:
            logger.error(f"回滚WASM事务失败: {e}")
            # 不要重新抛出异常，避免影响主事务回滚流程
    
    def _cleanup_wasm_transaction(self, wasm_runtime, transaction_id: str):
        """清理WASM运行时事务状态"""
        try:
            if hasattr(wasm_runtime, 'current_transaction_id'):
                wasm_runtime.current_transaction_id = None
            
            logger.debug(f"WASM事务 {transaction_id} 状态已清理")
            
        except Exception as e:
            logger.error(f"清理WASM事务状态失败: {e}")
    
    def get_current_transaction_id(self) -> Optional[str]:
        """获取当前线程的事务ID"""
        return getattr(self._active_context, 'current_transaction_id', None)
    
    def set_current_transaction_id(self, transaction_id: str):
        """设置当前线程的事务ID"""
        self._active_context.current_transaction_id = transaction_id
    
    def clear_current_transaction_id(self):
        """清除当前线程的事务ID"""
        if hasattr(self._active_context, 'current_transaction_id'):
            delattr(self._active_context, 'current_transaction_id')
    
    def _execute_post_commit_callbacks(self, callbacks: list):
        """执行事务成功后的回调函数"""
        for callback in callbacks:
            try:
                if callable(callback):
                    callback()
                elif isinstance(callback, dict) and 'func' in callback:
                    # 支持回调带参数的格式：{"func": function, "args": [...], "kwargs": {...}}
                    func = callback['func']
                    args = callback.get('args', [])
                    kwargs = callback.get('kwargs', {})
                    func(*args, **kwargs)
            except Exception as callback_error:
                logger.error(f"执行事务成功后回调失败: {callback_error}")
                # 回调失败不应该影响事务的成功状态
    
    def safe_commit_transaction(self, transaction_id: str, max_retries: int = None) -> bool:
        """安全的事务提交方法，包含重试机制和状态预检查"""
        # 预检查：如果事务已经完成，直接返回成功
        if self.atomicity_manager.is_transaction_completed(transaction_id):
            logger.info(f"事务 {transaction_id} 已处于最终状态，跳过提交")
            return True
        
        if max_retries is None:
            transaction_config = Config.get_transaction_config()
            max_retries = transaction_config["max_retries"]
        
        # 简化实现：避免事件循环冲突，使用线程池
        import concurrent.futures
        
        def run_async_commit():
            """在线程池的新事件循环中运行异步提交"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.atomicity_manager.commit_transaction(transaction_id))
            finally:
                loop.close()
        
        for attempt in range(max_retries):
            try:
                # 获取配置
                transaction_config = Config.get_transaction_config()
                commit_timeout = transaction_config["commit_timeout"]
                
                # 再次检查状态（可能在其他线程中已改变）
                if self.atomicity_manager.is_transaction_completed(transaction_id):
                    logger.info(f"事务 {transaction_id} 在重试期间已完成，跳过提交")
                    return True
                
                # 使用线程池执行异步任务，避免事件循环冲突
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(run_async_commit)
                    try:
                        result = future.result(timeout=commit_timeout)
                        if result:
                            logger.info(f"事务 {transaction_id} 安全提交成功 (尝试 {attempt + 1})")
                            return True
                        else:
                            logger.warning(f"事务提交返回失败 (尝试 {attempt + 1}/{max_retries}): {transaction_id}")
                            if attempt == max_retries - 1:
                                raise Exception("事务提交返回失败")
                            time.sleep(1.0)  # 等待后重试
                            continue
                    except concurrent.futures.TimeoutError:
                        future.cancel()
                        logger.warning(f"事务提交超时 (尝试 {attempt + 1}/{max_retries}): {transaction_id}")
                        if attempt == max_retries - 1:
                            raise asyncio.TimeoutError("事务提交超时")
                        time.sleep(1.0)  # 等待后重试
                        continue
                        
            except Exception as e:
                logger.error(f"事务 {transaction_id} 提交异常 (尝试 {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1.0)
        
        return False
