#!/usr/bin/env python3
"""
启动 Client 服务
"""

import uvicorn
import logging
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("启动 ToolPro Client 服务 (端口 8000)...")
    uvicorn.run(
        "client_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
