"""
ToolPro 系统配置文件
"""

import os
from pathlib import Path
from typing import Optional

class Config:
    """系统配置"""
    
    # API配置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # Client服务配置
    CLIENT_PORT: int = int(os.getenv("CLIENT_PORT", "8000"))
    SERVER_URL: str = os.getenv("SERVER_URL", "http://13.236.69.67:8001")
    
    # LLM配置
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3-max")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    
    # WebAssembly配置
    WASM_TIMEOUT: int = int(os.getenv("WASM_TIMEOUT", "30"))
    WASM_MAX_MODULES: int = int(os.getenv("WASM_MAX_MODULES", "100"))
    
    # 事务配置
    TRANSACTION_COMMIT_TIMEOUT: float = float(os.getenv("TRANSACTION_COMMIT_TIMEOUT", "30.0"))
    TRANSACTION_ROLLBACK_TIMEOUT: float = float(os.getenv("TRANSACTION_ROLLBACK_TIMEOUT", "10.0"))
    TRANSACTION_EXECUTION_TIMEOUT: float = float(os.getenv("TRANSACTION_EXECUTION_TIMEOUT", "300.0"))
    TRANSACTION_MAX_RETRIES: int = int(os.getenv("TRANSACTION_MAX_RETRIES", "3"))
    
    # 模板配置
    # TEMPLATE_CACHE_SIZE: int = int(os.getenv("TEMPLATE_CACHE_SIZE", "1000"))
    # TEMPLATE_CLEANUP_INTERVAL: int = int(os.getenv("TEMPLATE_CLEANUP_INTERVAL", "3600"))
    
    
    # 维护服务配置
    MAINTENANCE_CHECK_INTERVAL: int = int(os.getenv("MAINTENANCE_CHECK_INTERVAL", "300"))
    MAINTENANCE_API_CHECK_INTERVAL: int = int(os.getenv("MAINTENANCE_API_CHECK_INTERVAL", "3600"))
    
    # 沙盒配置
    SANDBOX_MAX_TEMP_DATA: int = int(os.getenv("SANDBOX_MAX_TEMP_DATA", "1000"))
    SANDBOX_TEMP_DATA_MAX_AGE: int = int(os.getenv("SANDBOX_TEMP_DATA_MAX_AGE", "24"))
    
    # 路径配置
    PROJECT_ROOT: str = os.getenv("PROJECT_ROOT", "")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "temp")
    CACHE_DIR: str = os.getenv("CACHE_DIR", "cache")
    RESULTS_DIR: str = os.getenv("RESULTS_DIR", "results")
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Redis配置（如果使用Redis作为模板存储）
    # REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    # REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    # REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    # REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """获取LLM配置"""
        return {
            "model": cls.LLM_MODEL,
            "base_url": cls.LLM_BASE_URL,
            "api_key": cls.LLM_API_KEY
        }
    
    @classmethod
    def get_wasm_config(cls) -> dict:
        """获取WebAssembly配置"""
        return {
            "timeout": cls.WASM_TIMEOUT,
            "max_modules": cls.WASM_MAX_MODULES
        }
    
    
    @classmethod
    def get_transaction_config(cls) -> dict:
        """获取事务配置"""
        return {
            "commit_timeout": cls.TRANSACTION_COMMIT_TIMEOUT,
            "rollback_timeout": cls.TRANSACTION_ROLLBACK_TIMEOUT,
            "execution_timeout": cls.TRANSACTION_EXECUTION_TIMEOUT,
            "max_retries": cls.TRANSACTION_MAX_RETRIES
        }
    
    @classmethod
    def get_maintenance_config(cls) -> dict:
        """获取维护服务配置"""
        return {
            "check_interval": cls.MAINTENANCE_CHECK_INTERVAL,
            "api_check_interval": cls.MAINTENANCE_API_CHECK_INTERVAL
        }
    
    @classmethod
    def get_project_root(cls) -> Path:
        """获取项目根目录"""
        if cls.PROJECT_ROOT:
            return Path(cls.PROJECT_ROOT)
        return Path(__file__).parent
    
    @classmethod
    def get_temp_dir(cls) -> Path:
        """获取临时目录路径"""
        temp_path = cls.get_project_root() / cls.TEMP_DIR
        temp_path.mkdir(exist_ok=True)
        return temp_path
    
    @classmethod
    def get_cache_dir(cls) -> Path:
        """获取缓存目录路径"""
        cache_path = cls.get_project_root() / cls.CACHE_DIR
        cache_path.mkdir(exist_ok=True)
        return cache_path
    
    @classmethod
    def get_results_dir(cls) -> Path:
        """获取结果目录路径"""
        results_path = cls.get_project_root() / cls.RESULTS_DIR
        results_path.mkdir(exist_ok=True)
        return results_path
    
    @classmethod
    def get_paths_config(cls) -> dict:
        """获取路径配置"""
        return {
            "project_root": str(cls.get_project_root()),
            "temp_dir": str(cls.get_temp_dir()),
            "cache_dir": str(cls.get_cache_dir()),
            "results_dir": str(cls.get_results_dir())
        }
    
    @classmethod
    def get_client_config(cls) -> dict:
        """获取Client服务配置"""
        return {
            "client_port": cls.CLIENT_PORT,
            "server_url": cls.SERVER_URL
        }
