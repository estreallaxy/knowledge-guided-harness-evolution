"""
MCP工具函数，实现与三个API的HTTP通信
"""
import httpx
import json
import toml
import psutil
import time
import threading
from typing import Dict, Any, Optional, List
from minio import Minio
from minio.error import S3Error
from models import (
    DirectusArticle, DirectusArticlesResponse,
    MemosResponse, MemosMemo, MemosUpdateRequest,
    MinioObjectInfo, ApiError
)


class SimpleTrafficMonitor:
    """简化的流量监控器，与Monkey Patching兼容"""
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # API流量统计（与Monkey Patching兼容）
        self.api_requests = 0
        self.api_bytes_sent = 0
        self.api_bytes_received = 0
        self.api_total_time = 0.0
        
        # 详细记录
        self.api_details = []
        
        # 监控状态
        self.monitoring_active = False
        
        # 系统级网络流量监控
        self.net_io_before = None
        self.net_io_after = None
        self.request_count = 0
        
        # 本地API流量统计
        self.local_api_bytes_sent = 0
        self.local_api_bytes_recv = 0
        self.local_api_request_count = 0
    
    def record_api_traffic(self, api_name: str, request_size: int, response_size: int, duration: float):
        """记录API流量数据"""
        with self._lock:
            self.api_requests += 1
            self.api_bytes_sent += request_size
            self.api_bytes_received += response_size
            self.api_total_time += duration
            
            detail = {
                "timestamp": time.time(),
                "api_name": api_name,
                "request_size": request_size,
                "response_size": response_size,
                "duration": duration,
                "request_data_preview": f"API调用: {api_name}",
                "response_data_preview": f"API响应: {api_name}"
            }
            self.api_details.append(detail)
            
            print(f"[API流量] {api_name}: 请求{request_size}B, 响应{response_size}B, 耗时{duration:.3f}s")
    
    def get_api_stats(self) -> Dict[str, Any]:
        """获取API流量统计（与Monkey Patching兼容）"""
        with self._lock:
            return {
                "requests": self.api_requests,
                "bytes_sent": self.api_bytes_sent,
                "bytes_received": self.api_bytes_received,
                "total_time": self.api_total_time,
                "avg_time": self.api_total_time / max(self.api_requests, 1),
                "details": self.api_details.copy()
            }
    
    def reset_stats(self):
        """重置统计数据"""
        with self._lock:
            self.api_requests = 0
            self.api_bytes_sent = 0
            self.api_bytes_received = 0
            self.api_total_time = 0.0
            self.api_details = []
            print("[流量监控] 统计数据已重置")
    
    def start_monitoring(self):
        """开始系统级网络流量监控"""
        with self._lock:
            self.net_io_before = psutil.net_io_counters()
            self.monitoring_active = True
            print(f"[流量监控] 开始监控 - 初始状态: {self.net_io_before}")
    
    def stop_monitoring(self):
        """停止系统级网络流量监控"""
        with self._lock:
            if self.monitoring_active:
                self.net_io_after = psutil.net_io_counters()
                self.monitoring_active = False
                print(f"[流量监控] 停止监控 - 最终状态: {self.net_io_after}")
    
    def get_system_traffic_stats(self) -> Dict[str, int]:
        """获取系统级网络流量统计"""
        with self._lock:
            if not self.net_io_before or not self.net_io_after:
                return {"error": "监控未启动或未停止"}
            
            bytes_sent = self.net_io_after.bytes_sent - self.net_io_before.bytes_sent
            bytes_recv = self.net_io_after.bytes_recv - self.net_io_before.bytes_recv
            packets_sent = self.net_io_after.packets_sent - self.net_io_before.packets_sent
            packets_recv = self.net_io_after.packets_recv - self.net_io_before.packets_recv
            
            return {
                "system_bytes_sent": bytes_sent,
                "system_bytes_recv": bytes_recv,
                "system_total_bytes": bytes_sent + bytes_recv,
                "system_packets_sent": packets_sent,
                "system_packets_recv": packets_recv,
                "system_total_packets": packets_sent + packets_recv
            }
    
    
    def get_local_api_stats(self) -> Dict[str, int]:
        """获取本地API流量统计"""
        with self._lock:
            return {
                "local_api_bytes_sent": self.local_api_bytes_sent,
                "local_api_bytes_recv": self.local_api_bytes_recv,
                "local_api_total_bytes": self.local_api_bytes_sent + self.local_api_bytes_recv,
                "local_api_request_count": self.local_api_request_count
            }
    
    def get_combined_stats(self) -> Dict[str, Any]:
        """获取综合流量统计"""
        system_stats = self.get_system_traffic_stats()
        local_api_stats = self.get_local_api_stats()
        
        return {
            **system_stats,
            **local_api_stats,
            "monitoring_active": self.monitoring_active,
            "request_count": self.request_count
        }
    
    def reset(self):
        """重置所有统计"""
        with self._lock:
            self.net_io_before = None
            self.net_io_after = None
            self.request_count = 0
            self.monitoring_active = False
            self.local_api_bytes_sent = 0
            self.local_api_bytes_recv = 0
            self.local_api_request_count = 0
    
    def add_local_api_traffic(self, request_size: int, response_size: int):
        """添加本地API流量统计"""
        with self._lock:
            self.local_api_bytes_sent += request_size
            self.local_api_bytes_recv += response_size
            self.local_api_request_count += 1
            print(f"[本地API流量] 请求: {request_size}字节, 响应: {response_size}字节")
    


# 全局流量监控实例
traffic_monitor = SimpleTrafficMonitor()




class DirectusTools:
    """Directus API工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config["base_url"]
        self.admin_email = config["admin_email"]
        self.admin_password = config["admin_password"]
        self.token: Optional[str] = None
    
    async def get_draft_articles(self) -> List[DirectusArticle]:
        """获取所有状态为草稿的文章信息"""
        url = f"{self.base_url}/items/articles"
        params = {
            "filter[status][_eq]": "Draft",
            "fields": "id,title,status,author"
        }
        
        print(f"[DirectusTools] 获取草稿文章:")
        print(f"  基础URL: {self.base_url}")
        print(f"  完整URL: {url}")
        print(f"  查询参数: {params}")
        
        try:
            start_time = time.time()
            
            # 计算请求大小
            request_size = len(str(url).encode('utf-8'))
            if params:
                request_size += len(str(params).encode('utf-8'))
            
            async with httpx.AsyncClient() as client:
                print(f"  发送GET请求...")
                
                response = await client.get(url, params=params)
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"  响应状态码: {response.status_code}")
                print(f"  响应头: {dict(response.headers)}")
                print(f"  响应内容: {response.text}")
                
                # 计算响应大小
                response_size = len(response.text.encode('utf-8'))
                
                # 记录API流量
                traffic_monitor.record_api_traffic("directus_get_draft_articles", request_size, response_size, duration)
                
                if response.status_code == 200:
                    data = response.json()
                    return [DirectusArticle(**article) for article in data["data"]]
                else:
                    raise ApiError(
                        error="Failed to get draft articles",
                        message=response.text,
                        status_code=response.status_code
                    )
        except Exception as e:
            print(f"[DirectusTools] 异常: {e}")
            raise
    
    async def update_articles_author(self, article_ids: List[int], author_id: int) -> List[DirectusArticle]:
        """更改所有状态为草稿的文章作者为指定ID的作者"""
        url = f"{self.base_url}/items/articles"
        data = {
            "keys": article_ids,
            "data": {"author": author_id}
        }
        
        print(f"[DirectusTools] 更新文章作者:")
        print(f"  基础URL: {self.base_url}")
        print(f"  完整URL: {url}")
        print(f"  文章IDs: {article_ids}")
        print(f"  作者ID: {author_id}")
        print(f"  请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        try:
            start_time = time.time()
            
            # 计算请求大小
            request_size = len(str(url).encode('utf-8'))
            request_size += len(json.dumps(data).encode('utf-8'))
            
            async with httpx.AsyncClient() as client:
                print(f"  发送PATCH请求...")
                
                response = await client.patch(
                    url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"  响应状态码: {response.status_code}")
                print(f"  响应头: {dict(response.headers)}")
                print(f"  响应内容: {response.text}")
                
                # 计算响应大小
                response_size = len(response.text.encode('utf-8'))
                
                # 记录API流量
                traffic_monitor.record_api_traffic("directus_update_articles_author", request_size, response_size, duration)
                
                if response.status_code == 200:
                    data = response.json()
                    return [DirectusArticle(**article) for article in data["data"]]
                else:
                    raise ApiError(
                        error="Failed to update articles author",
                        message=response.text,
                        status_code=response.status_code
                    )
        except Exception as e:
            print(f"[DirectusTools] 异常: {e}")
            raise


class MemosTools:
    """Memos API工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config["base_url"]
        self.api_version = config["api_version"]
        self.access_token = config.get("access_token")
    
    async def get_memos(self) -> List[MemosMemo]:
        """获取备忘录列表"""
        url = f"{self.base_url}/api/{self.api_version}/memos"
        
        print(f"[MemosTools] 获取备忘录列表:")
        print(f"  完整URL: {url}")
        
        try:
            start_time = time.time()
            
            # 计算请求大小
            request_size = len(str(url).encode('utf-8'))
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                
                end_time = time.time()
                duration = end_time - start_time
                
                # 计算响应大小
                response_size = len(response.text.encode('utf-8'))
                
                # 记录API流量
                traffic_monitor.record_api_traffic("memos_get_memos", request_size, response_size, duration)
                
                if response.status_code == 200:
                    data = response.json()
                    return [MemosMemo(**memo) for memo in data["memos"]]
                else:
                    raise ApiError(
                        error="Failed to get memos",
                        message=response.text,
                        status_code=response.status_code
                    )
        except Exception as e:
            print(f"[MemosTools] 异常: {e}")
            raise
    
    async def update_memo_visibility(self, memo_name: str, visibility: str = "PUBLIC") -> bool:
        """更新备忘录可见性"""
        update_data = {
            "visibility": visibility
        }
        
        # 处理备忘录名称，去掉可能存在的 "memos/" 前缀
        clean_memo_name = memo_name
        if memo_name.startswith("memos/"):
            clean_memo_name = memo_name[6:]  # 去掉 "memos/" 前缀
        
        # 构建完整的URL
        full_url = f"{self.base_url}/api/{self.api_version}/memos/{clean_memo_name}"
        
        print(f"[MemosTools] 更新备忘录可见性:")
        print(f"  完整URL: {full_url}")
        print(f"  原始备忘录名称: {memo_name}")
        print(f"  清理后名称: {clean_memo_name}")
        print(f"  可见性设置: {visibility}")
        print(f"  请求数据: {json.dumps(update_data, ensure_ascii=False, indent=2)}")
        print(f"  基础URL: {self.base_url}")
        print(f"  API版本: {self.api_version}")
        
        # 准备请求头
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            print(f"  使用认证token: {self.access_token[:20]}...")
        else:
            print(f"  未配置认证token")
        
        try:
            start_time = time.time()
            
            # 计算请求大小
            request_size = len(str(full_url).encode('utf-8'))
            request_size += len(json.dumps(update_data).encode('utf-8'))
            
            async with httpx.AsyncClient() as client:
                print(f"  发送PATCH请求...")
                
                response = await client.patch(
                    full_url,
                    json=update_data,
                    headers=headers
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"  响应状态码: {response.status_code}")
                print(f"  响应头: {dict(response.headers)}")
                print(f"  响应内容: {response.text}")
                
                # 计算响应大小
                response_size = len(response.text.encode('utf-8'))
                
                # 记录API流量
                traffic_monitor.record_api_traffic("memos_update_visibility", request_size, response_size, duration)
                
                if response.status_code == 200:
                    print(f"  更新成功")
                    return True
                else:
                    print(f"  更新失败")
                    raise ApiError(
                        error="Failed to update memo",
                        message=response.text,
                        status_code=response.status_code
                    )
        except Exception as e:
            print(f"[MemosTools] 异常: {e}")
            raise


class MinioTools:
    """MinIO API工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.client = Minio(
            config["endpoint"],
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            secure=config["secure"]
        )
        self.bucket_name = config["bucket_name"]
    
    def upload_object(self, object_name: str, data: str) -> bool:
        """上传对象到MinIO"""
        print(f"[MinioTools] upload_object 开始执行")
        print(f"  参数: object_name={object_name}, data_length={len(data)}")
        print(f"  bucket_name={self.bucket_name}")
        print(f"  client状态: {self.client is not None}")
        
        # 开始流量监控（累积模式，不重置）
        if not traffic_monitor.monitoring_active:
            traffic_monitor.start_monitoring()
        
        try:
            from io import BytesIO
            print(f"  开始编码数据为UTF-8")
            data_bytes = data.encode('utf-8')
            print(f"  数据编码完成，字节长度: {len(data_bytes)}")
            
            data_stream = BytesIO(data_bytes)
            print(f"  创建BytesIO流成功")
            
            # 计算请求大小
            request_size = len(f"PUT /{self.bucket_name}/{object_name}".encode('utf-8')) + len(data_bytes)
            
            print(f"  开始调用MinIO put_object")
            start_time = time.time()
            
            self.client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                length=len(data_bytes)
            )
            
            end_time = time.time()
            duration = end_time - start_time
            print(f"  MinIO put_object 调用成功，耗时: {duration:.3f}s")
            
            # 计算响应大小
            response_size = len('{"etag": "mock-etag", "versionId": "mock-version"}'.encode('utf-8'))
            
            # 添加本地API流量统计（MinIO使用HTTP协议与本地服务器通信）
            traffic_monitor.add_local_api_traffic(request_size, response_size)
            
            # 记录API流量（与Directus和Memos保持一致）
            traffic_monitor.record_api_traffic("minio_upload_object", request_size, response_size, duration)
            
            return True
        except S3Error as e:
            print(f"  S3Error: {e}")
            raise ApiError(
                error="MinIO upload failed",
                message=str(e),
                status_code=500
            )
        except Exception as e:
            print(f"  其他异常: {e}")
            import traceback
            print(f"  异常详情: {traceback.format_exc()}")
            raise
        finally:
            # 不停止监控，保持累积统计
            stats = traffic_monitor.get_combined_stats()
            print(f"[MinioTools] 流量统计: {stats}")
    
    def get_object(self, object_name: str) -> str:
        """从MinIO获取对象"""
        print(f"[MinioTools] get_object 开始执行")
        print(f"  参数: object_name={object_name}")
        print(f"  bucket_name={self.bucket_name}")
        print(f"  client状态: {self.client is not None}")
        
        # 开始流量监控（累积模式，不重置）
        if not traffic_monitor.monitoring_active:
            traffic_monitor.start_monitoring()
        
        try:
            # 计算请求大小
            request_size = len(f"GET /{self.bucket_name}/{object_name}".encode('utf-8'))
            
            print(f"  开始调用MinIO get_object")
            start_time = time.time()
            
            response = self.client.get_object(self.bucket_name, object_name)
            print(f"  MinIO get_object 调用成功，开始读取数据")
            
            data = response.read().decode('utf-8')
            print(f"  数据读取完成，长度: {len(data)}")
            
            end_time = time.time()
            duration = end_time - start_time
            print(f"  MinIO get_object 完成，耗时: {duration:.3f}s")
            
            # 计算响应大小
            response_size = len(data.encode('utf-8'))
            
            # 添加本地API流量统计（MinIO使用HTTP协议与本地服务器通信）
            traffic_monitor.add_local_api_traffic(request_size, response_size)
            
            # 记录API流量（与Directus和Memos保持一致）
            traffic_monitor.record_api_traffic("minio_get_object", request_size, response_size, duration)
            
            response.close()
            response.release_conn()
            print(f"  响应资源已释放")
            return data
        except S3Error as e:
            print(f"  S3Error: {e}")
            raise ApiError(
                error="MinIO get object failed",
                message=str(e),
                status_code=500
            )
        except Exception as e:
            print(f"  其他异常: {e}")
            import traceback
            print(f"  异常详情: {traceback.format_exc()}")
            raise
        finally:
            # 不停止监控，保持累积统计
            stats = traffic_monitor.get_combined_stats()
            print(f"[MinioTools] 流量统计: {stats}")


# 全局工具实例
directus_tools: Optional[DirectusTools] = None
memos_tools: Optional[MemosTools] = None
minio_tools: Optional[MinioTools] = None


def initialize_tools(config_path: str = "settings.toml"):
    """初始化所有工具实例"""
    global directus_tools, memos_tools, minio_tools
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = toml.load(f)
    
    directus_tools = DirectusTools(config["directus"])
    memos_tools = MemosTools(config["memos"])
    minio_tools = MinioTools(config["minio"])


def get_traffic_stats() -> Dict[str, Any]:
    """获取当前流量统计（与Monkey Patching兼容）"""
    api_stats = traffic_monitor.get_api_stats()
    
    return {
        "api_requests": api_stats["requests"],
        "api_bytes_sent": api_stats["bytes_sent"],
        "api_bytes_received": api_stats["bytes_received"],
        "api_total_time": api_stats["total_time"],
        "api_avg_time": api_stats["avg_time"],
        "api_details": api_stats["details"],
        
        # 与Monkey Patching兼容的格式
        "monkey_patching_compatible": {
            "llm": {
                "requests": 0,
                "bytes_sent": 0,
                "bytes_received": 0,
                "total_time": 0.0,
                "avg_time": 0.0
            },
            "api": {
                "requests": api_stats["requests"],
                "bytes_sent": api_stats["bytes_sent"],
                "bytes_received": api_stats["bytes_received"],
                "total_time": api_stats["total_time"],
                "avg_time": api_stats["avg_time"]
            },
            "mcp": {
                "messages_sent": 0,
                "messages_received": 0,
                "bytes_sent": 0,
                "bytes_received": 0
            }
        }
    }


def reset_traffic_stats():
    """重置流量统计"""
    traffic_monitor.reset()

def get_system_traffic_stats() -> Dict[str, int]:
    """获取系统级流量统计"""
    return traffic_monitor.get_system_traffic_stats()


def stop_traffic_monitoring():
    """停止流量监控"""
    traffic_monitor.stop_monitoring()


def get_local_api_traffic_stats() -> Dict[str, int]:
    """获取本地API流量统计"""
    return traffic_monitor.get_local_api_stats()


# MCP工具函数
async def directus_get_draft_articles() -> Dict[str, Any]:
    """获取Directus草稿文章列表"""
    try:
        articles = await directus_tools.get_draft_articles()
        return {
            "success": True,
            "data": [article.dict() for article in articles],
            "count": len(articles)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def directus_update_articles_author(article_ids: List[int], author_id: int) -> Dict[str, Any]:
    """更新Directus文章作者"""
    try:
        articles = await directus_tools.update_articles_author(article_ids, author_id)
        return {
            "success": True,
            "data": [article.dict() for article in articles],
            "count": len(articles),
            "message": f"Updated {len(articles)} articles with author ID {author_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def memos_get_memos() -> Dict[str, Any]:
    """获取Memos备忘录列表"""
    try:
        print(f"调试信息 - memos_get_memos 开始执行")
        print(f"调试信息 - memos_tools 状态: {memos_tools is not None}")
        
        if memos_tools is None:
            print(f"调试信息 - memos_tools 为 None，尝试重新初始化")
            initialize_tools()
        
        print(f"调试信息 - 调用 memos_tools.get_memos()")
        memos = await memos_tools.get_memos()
        print(f"调试信息 - 获取到 {len(memos)} 个备忘录")
        
        return {
            "success": True,
            "data": [memo.dict() for memo in memos],
            "count": len(memos)
        }
    except Exception as e:
        print(f"调试信息 - memos_get_memos 执行出错: {e}")
        import traceback
        print(f"调试信息 - 错误详情: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }


async def memos_update_visibility(memo_name: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
    """更新Memos备忘录可见性"""
    try:
        success = await memos_tools.update_memo_visibility(memo_name, visibility)
        return {
            "success": success,
            "message": f"Memo {memo_name} visibility updated to {visibility}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def minio_upload_object(object_name: str, content: str) -> Dict[str, Any]:
    """上传对象到MinIO"""
    print(f"[MCP工具调试] minio_upload_object 开始执行")
    print(f"[MCP工具调试] 参数: object_name={object_name}, content_length={len(content)}")
    print(f"[MCP工具调试] minio_tools 状态: {minio_tools is not None}")
    
    try:
        if minio_tools is None:
            print(f"[MCP工具调试] minio_tools 为 None，尝试重新初始化")
            initialize_tools()
            print(f"[MCP工具调试] 重新初始化后 minio_tools 状态: {minio_tools is not None}")
        
        print(f"[MCP工具调试] 开始调用 minio_tools.upload_object")
        success = minio_tools.upload_object(object_name, content)
        print(f"[MCP工具调试] upload_object 返回结果: {success}")
        
        result = {
            "success": success,
            "message": f"Object {object_name} uploaded successfully"
        }
        print(f"[MCP工具调试] 最终返回结果: {result}")
        return result
    except Exception as e:
        print(f"[MCP工具调试] minio_upload_object 执行出错: {e}")
        import traceback
        print(f"[MCP工具调试] 错误详情: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }


def minio_get_object(object_name: str) -> Dict[str, Any]:
    """从MinIO获取对象"""
    print(f"[MCP工具调试] minio_get_object 开始执行")
    print(f"[MCP工具调试] 参数: object_name={object_name}")
    print(f"[MCP工具调试] minio_tools 状态: {minio_tools is not None}")
    
    try:
        if minio_tools is None:
            print(f"[MCP工具调试] minio_tools 为 None，尝试重新初始化")
            initialize_tools()
            print(f"[MCP工具调试] 重新初始化后 minio_tools 状态: {minio_tools is not None}")
        
        print(f"[MCP工具调试] 开始调用 minio_tools.get_object")
        content = minio_tools.get_object(object_name)
        print(f"[MCP工具调试] get_object 返回内容长度: {len(content) if content else 0}")
        
        result = {
            "success": True,
            "data": content,
            "object_name": object_name
        }
        print(f"[MCP工具调试] 最终返回结果: success={result['success']}, data_length={len(content) if content else 0}")
        return result
    except Exception as e:
        print(f"[MCP工具调试] minio_get_object 执行出错: {e}")
        import traceback
        print(f"[MCP工具调试] 错误详情: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }
