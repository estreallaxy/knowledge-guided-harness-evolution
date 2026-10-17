#!/usr/bin/env python3
"""
启动 Server 服务
"""

import uvicorn
import logging
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("启动 ToolPro Server 服务 (端口 8001)...")
    uvicorn.run(
        "server_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
