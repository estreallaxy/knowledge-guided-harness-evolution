"""
多模态大模型API接口 - 云雾API版本
通过云雾API调用不同的多模态模型
支持图片和视频
"""

import os
import base64
import json
import threading
from datetime import datetime
from typing import List, Optional, Union, Tuple, Dict
from pathlib import Path
from openai import OpenAI, AsyncOpenAI
import time
import cv2
import numpy as np
from io import BytesIO
from PIL import Image


class YunwuModel:
    """云雾API多模态模型"""
    
    # 支持原生视频的模型列表
    NATIVE_VIDEO_MODELS = set([
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-pro-vision',
        'gpt-4o',
        'gpt-4o-mini',

    ])
    
    # 类级别的文件锁，用于保护 token 日志文件写入
    _token_log_lock = threading.Lock()
    
    def __init__(self, 
                 model_name: str = "gpt-4-vision-preview",
                 client: Optional[OpenAI] = None,
                 api_key: Optional[str] = None,
                 base_url: str = "https://yunwu.ai/v1",
                 **kwargs):
        """
        初始化云雾模型
        
        Args:
            model_name: 模型名称，如 gpt-4-vision-preview, claude-3-opus-20240229 等
            client: OpenAI client, 优先级高于 api_key 和 base_url
            api_key: 云雾API密钥
            base_url: 云雾API地址
            **kwargs: 其他配置参数
        """

        self.model_name = model_name
        self.api_key = api_key or os.getenv('YUNWU_API_KEY')
        self.base_url = base_url
        self.config = kwargs
        
        # 统计 token 使用情况的容器
        self.token_stats = {
            'in_tokens': 0,
            'out_tokens': 0,
            'total_tokens': 0,
            'calls': 0
        }

        # 最近一次调用的 usage（方便外部读取）
        self.last_call_usage = None

        # token 日志文件路径（JSON 列表）。可通过 kwargs 传入 'token_log_path'
        self.token_log_path = Path(self.config.get('token_log_path', Path.cwd() / 'token_usage.json'))
        
        # 是否启用自动写文件（用于批量场景下的性能优化）
        self.auto_write_log = self.config.get('auto_write_log', True)
        
        # 内存中累积的 token 使用记录（当 auto_write_log=False 时使用）
        self.token_usage_buffer = []


        # 判断模型是否支持原生视频
        self.supports_native_video = any(
            model in model_name.lower() 
            for model in self.NATIVE_VIDEO_MODELS
        )
        
        if not self.api_key:
            raise ValueError("请设置 YUNWU_API_KEY 环境变量或传入 api_key 参数")
        

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    
    def _load_image(self, image_path: Union[str, Path]) -> bytes:

        """加载图片为字节"""
        if isinstance(image_path, str) and image_path.startswith('http'):
            # URL图片
            import requests
            image_path = image_path.replace('https:\\', 'https://')
            image_path = image_path.replace('\\', '/')
            response = requests.get(image_path, timeout=30)
            return response.content
        else:
            # 本地图片
            with open(image_path, 'rb') as f:
                return f.read()
    
    def _encode_image_base64(self, image_path: Union[str, Path]) -> str:
        """将图片编码为base64"""
        image_bytes = self._load_image(image_path)
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _extract_video_frames(self, video_path: Union[str, Path], max_frames: int = 30) -> List[str]:
        """
        从视频中提取关键帧并转换为base64
        策略：每0.5秒取一帧，最多取20帧
        
        Args:
            video_path: 视频路径
            max_frames: 最多提取的帧数（默认30）
            
        Returns:
            base64编码的帧列表
        """

        # 打开视频
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)  # 获取视频帧率
        
        if total_frames == 0:
            print(f"⚠️ 视频无法读取: {video_path}")
            cap.release()
            raise Exception(f"视频无法读取: {video_path}")
        
        if fps <= 0:
            fps = 30  # 默认帧率
        
        # 计算采样策略：每0.5秒取一帧
        frame_interval = int(fps * 0.5)  # 0.5秒对应的帧数
        frame_interval = max(1, frame_interval)  # 至少间隔1帧
        
        # 计算实际能提取的帧数
        num_frames = min(max_frames, total_frames // frame_interval)
        
        video_duration = total_frames / fps
        # print(f"  视频信息: 时长={video_duration:.1f}秒, 帧率={fps:.1f}fps, 总帧数={total_frames}")
        # print(f"  采样策略: 每0.5秒取一帧(间隔{frame_interval}帧), 最多{max_frames}帧")
        # print(f"  实际提取: {num_frames}帧")
        
        frames_base64 = []
        for i in range(num_frames):
            frame_idx = i * frame_interval
            if frame_idx >= total_frames:
                break
                
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                # 转换BGR到RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # 转换为PIL Image
                pil_image = Image.fromarray(frame_rgb)
                # 转换为base64
                buffered = BytesIO()
                pil_image.save(buffered, format="JPEG", quality=85)
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                frames_base64.append(img_base64)
        
        cap.release()
        # print(f"  ✓ 成功提取 {len(frames_base64)} 帧")
        return frames_base64

    # def _extract_video_frames(self, video_path: Union[str, Path], num_frames: int = 8) -> List[str]:
    #     """
    #     从视频中提取关键帧并转换为base64
        
    #     Args:
    #         video_path: 视频路径
    #         num_frames: 提取的帧数
            
    #     Returns:
    #         base64编码的帧列表
    #     """
    #     try:
    #         import cv2
    #         import numpy as np
    #         from io import BytesIO
    #         from PIL import Image
            
    #         # 打开视频
    #         cap = cv2.VideoCapture(str(video_path))
    #         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
    #         if total_frames == 0:
    #             print(f"⚠️ 视频无法读取: {video_path}")
    #             return []
            
    #         # 计算采样间隔
    #         interval = max(1, total_frames // num_frames)
            
    #         frames_base64 = []
    #         for i in range(num_frames):
    #             frame_idx = min(i * interval, total_frames - 1)
    #             cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    #             ret, frame = cap.read()
                
    #             if ret:
    #                 # 转换BGR到RGB
    #                 frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #                 # 转换为PIL Image
    #                 pil_image = Image.fromarray(frame_rgb)
    #                 # 转换为base64
    #                 buffered = BytesIO()
    #                 pil_image.save(buffered, format="JPEG", quality=85)
    #                 img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    #                 frames_base64.append(img_base64)
            
    #         cap.release()
    #         print(f"✓ 从视频提取了 {len(frames_base64)} 帧")
    #         return frames_base64
    #     except ImportError:
    #         print("❌ 需要安装 opencv-python: pip install opencv-python")
    #         return []
    #     except Exception as e:
    #         print(f"❌ 视频处理失败: {e}")
    #         return []
            
    def _encode_video_base64(self, video_path: Union[str, Path]) -> str:

        """将视频文件编码为base64（用于支持原生视频的模型）"""

        try:
            video_bytes = self._load_image(video_path)  # 复用_load_image方法
            return base64.b64encode(video_bytes).decode('utf-8')
            
        except Exception as e:
            print(f"❌ 视频编码失败: {e}")
            return ""
    
    def get_file_format(self, file_path):
        """获取文件格式"""
        extension = file_path.lower().split('.')[-1]
        if extension in ['png', 'jpg', 'jpeg']:
            return extension if extension != 'jpg' else 'jpeg'
        return 'jpeg'  # 默认格式
    
    def build_content(self, prompt: str, images: Optional[List[Union[str, Path]]] = None, 
                      videos: Optional[List[Union[str, Path]]] = None) -> list:
        
        content = [{"type": "text", "text": prompt}]
        
        # 处理图片（统一转换为base64，避免URL图片读取失败）
        if images:
            for img_path in images:
                if isinstance(img_path, str) and img_path.startswith('data:image'):
                    # 已经是base64格式
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": img_path}
                    })
                elif isinstance(img_path, str) and img_path.startswith('http'):
                    # URL图片 - 下载并转换为base64（更稳定）
                    # print(f"  -> 下载URL图片: {img_path[:80]}...")
                    # try:
                    #     base64_image = self._encode_image_base64(img_path)
                    #     content.append({
                    #         "type": "image_url",
                    #         "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}
                    #     })
                    # except Exception as e:
                    #     print(f"  ⚠️ URL图片下载失败: {e}")
                    #     continue

                    raise Exception(f"URL图片: {img_path} 下载失败")
                else:

                    # 本地图片转base64
                    base64_image = self._encode_image_base64(img_path)
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url":
                        f"data:image/{self.get_file_format(img_path)};base64,{base64_image}"}
                    })
        
        # 处理视频
        if videos:
            if self.supports_native_video:
                # 模型支持原生视频，直接传视频
                print(f"✓ 模型 {self.model_name} 支持原生视频，直接传输视频文件")
                for video_path in videos:
                    # 本地视频转base64
                    base64_video = self._encode_video_base64(video_path)
                    if base64_video:
                        content.append({
                            "type": "video_url",
                            "video_url": {"url": f"data:video/mp4;base64,{base64_video}"}
                        })
            else:
                # 模型不支持原生视频，提取关键帧

                # print(f"⚠️ 模型 {self.model_name} 不支持原生视频，将提取关键帧")
                for video_path in videos:
                    frames = self._extract_video_frames(video_path, max_frames=30)
                    for frame_base64 in frames:
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{frame_base64}"}
                        })

        return content
        
    def generate(self, prompt: Optional[str] = None, images: Optional[List[Union[str, Path]]] = None, 
                 videos: Optional[List[Union[str, Path]]] = None,
                 messages: Optional[List[Dict]] = None) -> str:
        """
        生成响应
        
        Args:
            prompt: 文本提示词（如果提供messages则忽略此参数）
            images: 图片路径列表或图片URL列表（如果提供messages则忽略此参数）
            videos: 视频路径列表（如果提供messages则忽略此参数）
            messages: 多轮对话消息列表，格式：
                     [
                         {"role": "user", "content": [...]},
                         {"role": "assistant", "content": "..."},
                         {"role": "user", "content": [...]}
                     ]
                     如果提供此参数，则忽略prompt/images/videos
            
        Returns:
            模型生成的文本响应
        """

        try:
            # 如果提供了messages，直接使用；否则构建单轮对话
            if messages:
                final_messages = messages
            else:
                if prompt is None:
                    raise ValueError("必须提供 prompt 或 messages 参数")
                content = self.build_content(prompt, images, videos)
                final_messages = [{"role": "user", "content": content}]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=final_messages,
                max_tokens=self.config.get('max_tokens', 4096),
                temperature=self.config.get('temperature', 0.7)
            )

            # 尝试读取 usage 并更新统计（支持 dict 或对象形式）
            usage = None

            usage = getattr(response, 'usage', None) or (response.get('usage') if isinstance(response, dict) else None)


            prompt_t = 0
            comp_t = 0
            total_t = 0


            if isinstance(usage, dict):
                prompt_t = int(usage.get('prompt_tokens', 0) or 0)
                comp_t = int(usage.get('completion_tokens', 0) or 0)
                total_t = int(usage.get('total_tokens', prompt_t + comp_t) or (prompt_t + comp_t))
            else:
                prompt_t = int(getattr(usage, 'prompt_tokens', 0) or 0)
                comp_t = int(getattr(usage, 'completion_tokens', 0) or 0)
                total_t = int(getattr(usage, 'total_tokens', prompt_t + comp_t) or (prompt_t + comp_t))

            
            # 更新实例统计
            self.token_stats['in_tokens'] += prompt_t
            self.token_stats['out_tokens'] += comp_t
            self.token_stats['total_tokens'] += total_t
            self.token_stats['calls'] += 1

            # 保存最近一次调用的 usage 到实例
            self.last_call_usage = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'model': self.model_name,
                'prompt_tokens': prompt_t,
                'completion_tokens': comp_t,
                'total_tokens': total_t
            }
            
            # 根据配置决定是立即写文件还是累积到内存
            if self.auto_write_log:
                # 立即写文件（原有行为，使用线程锁保护）
                try:
                    with self._token_log_lock:
                        # 读取已有数据（若不存在或解析失败则新建列表）
                        if self.token_log_path.exists():
                            try:
                                content = self.token_log_path.read_text(encoding='utf-8')
                                existing = json.loads(content) if content.strip() else []
                                if not isinstance(existing, list):
                                    existing = []
                            except (json.JSONDecodeError, Exception) as e:
                                print(f"[token_log] 读取失败，重新创建: {e}")
                                existing = []
                        else:
                            existing = []
                        
                        existing.append(self.last_call_usage)
                        self.token_log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
                except Exception as e:
                    print(f"[token_log] 写入失败: {e}")
            else:
                # 累积到内存（性能优化模式）
                self.token_usage_buffer.append(self.last_call_usage)


            # debug输出prompt的token数
            # print(f"  ➡️ Prompt Tokens: {prompt_t}, Completion Tokens: {comp_t}, Total Tokens: {total_t}")
            
            

            return response.choices[0].message.content
        
        except Exception as e:
            print(f"❌ 云雾API生成失败: {e}")
            import traceback
            traceback.print_exc()
            return "{}"
    
    def flush_token_log(self):
        """将内存中累积的 token 使用记录批量写入文件（性能优化）"""
        if not self.token_usage_buffer:
            return  # 没有待写入的数据
        
        try:
            with self._token_log_lock:
                # 读取已有数据
                if self.token_log_path.exists():
                    try:
                        content = self.token_log_path.read_text(encoding='utf-8')
                        existing = json.loads(content) if content.strip() else []
                        if not isinstance(existing, list):
                            existing = []
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"[token_log] 读取失败，重新创建: {e}")
                        existing = []
                else:
                    existing = []
                
                # 批量追加
                existing.extend(self.token_usage_buffer)
                self.token_log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
                
                # 清空缓冲区
                self.token_usage_buffer = []
        except Exception as e:
            print(f"[token_log] 批量写入失败: {e}")
    
    def clear_token_buffer(self):
        """清空内存中的 token 使用记录缓冲区"""
        self.token_usage_buffer = []

class AsyncModel(YunwuModel):
    def __init__(self, model_name = "gpt-4-vision-preview", client: Optional[AsyncOpenAI] = None, api_key = 'your_key', base_url = "https://yunwu.ai/v1", **kwargs):
        """
                初始化云雾模型
                
                Args:
                    model_name: 模型名称，如 gpt-4-vision-preview, claude-3-opus-20240229 等
                    client: OpenAI client, 优先级高于 api_key 和 base_url
                    api_key: 云雾API密钥
                    base_url: 云雾API地址
                    **kwargs: 其他配置参数
        """
        
        # super().__init__(model_name, client, api_key, base_url, **kwargs)

       
        self.model_name = model_name
        self.api_key = api_key or os.getenv('YUNWU_API_KEY')
        self.base_url = base_url
        self.config = kwargs


        # 统计 token 使用情况的容器
        self.token_stats = {
            'in_tokens': 0,
            'out_tokens': 0,
            'total_tokens': 0,
            'calls': 0
        }
        # 最近一次调用的 usage（方便外部读取）
        self.last_call_usage = None

        # token 日志文件路径（JSON 列表）。可通过 kwargs 传入 'token_log_path'
        self.token_log_path = Path(self.config.get('token_log_path', Path.cwd() / 'token_usage.json'))
        
        # 是否启用自动写文件（用于批量场景下的性能优化）
        self.auto_write_log = self.config.get('auto_write_log', True)
        
        # 内存中累积的 token 使用记录（当 auto_write_log=False 时使用）
        self.token_usage_buffer = []


        
        # 判断模型是否支持原生视频
        self.supports_native_video = model_name.lower() in self.NATIVE_VIDEO_MODELS
        
        # any(
        #     model in model_name.lower() 
        #     for model in self.NATIVE_VIDEO_MODELS
        # )
        
        if not self.api_key:
            raise ValueError("请设置 YUNWU_API_KEY 环境变量或传入 api_key 参数")
        

        # 云雾使用OpenAI兼容接口
        if client is not None:
            self.client = client
        else:
            self.client = AsyncOpenAI(
                api_key=api_key, 
                base_url=base_url,
                timeout=180.0,      # 超时时间180秒（默认60秒）
                max_retries=5       # 最大重试5次（默认2次）
            )

    
    async def generate(self, content):
        """
        生成响应
        Returns:
            模型生成的文本响应
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": content}],
                max_tokens=self.config.get('max_tokens', 4096),
                temperature=self.config.get('temperature', 0.7)
            )

            # 读取 usage 并更新统计
            usage = None
            try:
                usage = getattr(response, 'usage', None) or (response.get('usage') if isinstance(response, dict) else None)
            except Exception:
                usage = None

            prompt_t = 0
            comp_t = 0
            total_t = 0
            if usage:
                try:
                    if isinstance(usage, dict):
                        prompt_t = int(usage.get('prompt_tokens', 0) or 0)
                        comp_t = int(usage.get('completion_tokens', 0) or 0)
                        total_t = int(usage.get('total_tokens', prompt_t + comp_t) or (prompt_t + comp_t))
                    else:
                        prompt_t = int(getattr(usage, 'prompt_tokens', 0) or 0)
                        comp_t = int(getattr(usage, 'completion_tokens', 0) or 0)
                        total_t = int(getattr(usage, 'total_tokens', prompt_t + comp_t) or (prompt_t + comp_t))
                except Exception:
                    prompt_t = 0
                    comp_t = 0
                    total_t = 0

            # 更新实例统计
            self.token_stats['in_tokens'] += prompt_t
            self.token_stats['out_tokens'] += comp_t
            self.token_stats['total_tokens'] += total_t
            self.token_stats['calls'] += 1

             # 保存最近一次调用的 usage 到实例
            self.last_call_usage = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'model': self.model_name,
                'prompt_tokens': prompt_t,
                'completion_tokens': comp_t,
                'total_tokens': total_t
            }
            
            # 根据配置决定是立即写文件还是累积到内存
            if self.auto_write_log:
                # 立即写文件（原有行为）
                try:
                    # 读取已有数据（若不存在或解析失败则新建列表）
                    if self.token_log_path.exists():
                        try:
                            existing = json.loads(self.token_log_path.read_text(encoding='utf-8') or '[]')
                            if not isinstance(existing, list):
                                existing = []
                        except Exception:
                            existing = []
                    else:
                        existing = []
                    existing.append(self.last_call_usage)
                    self.token_log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
                except Exception as e:
                    print(f"[token_log] 写入失败: {e}")
            else:
                # 累积到内存（性能优化模式）
                self.token_usage_buffer.append(self.last_call_usage)

            # debug输出prompt的token数
            # print(f"  ➡️ Prompt Tokens: {prompt_t}, Completion Tokens: {comp_t}, Total Tokens: {total_t}")
            

            answer = response.choices[0].message.content.strip()
            return answer
        
        except Exception:
            raise
    
    def flush_token_log(self):
        """将内存中累积的 token 使用记录批量写入文件（性能优化）"""
        if not self.token_usage_buffer:
            return  # 没有待写入的数据
        
        try:
            with self._token_log_lock:
                # 读取已有数据
                if self.token_log_path.exists():
                    try:
                        content = self.token_log_path.read_text(encoding='utf-8')
                        existing = json.loads(content) if content.strip() else []
                        if not isinstance(existing, list):
                            existing = []
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"[token_log] 读取失败，重新创建: {e}")
                        existing = []
                else:
                    existing = []
                
                # 批量追加
                existing.extend(self.token_usage_buffer)
                self.token_log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
                
                # 清空缓冲区
                self.token_usage_buffer = []
        except Exception as e:
            print(f"[token_log] 批量写入失败: {e}")
    
    def clear_token_buffer(self):
        """清空内存中的 token 使用记录缓冲区"""
        self.token_usage_buffer = []


# ==================== 常用模型配置 ====================

SUPPORTED_MODELS = {
    # OpenAI模型
    'gpt4v': 'gpt-4-vision-preview',
    'gpt4-turbo': 'gpt-4-turbo',
    'gpt4': 'gpt-4-vision-preview',
    
    # Claude模型
    'claude-opus': 'claude-3-opus-20240229',
    'claude-sonnet': 'claude-3-sonnet-20240229',
    'claude': 'claude-3-opus-20240229',
    
    # Gemini模型
    'gemini': 'gemini-pro-vision',
    'gemini-pro': 'gemini-pro-vision',
}


def get_model_name(alias: str) -> str:
    """
    根据别名获取完整的模型名称
    
    Args:
        alias: 模型别名，如 'gpt4v', 'claude', 'gemini'
    
    Returns:
        完整的模型名称
    """
    return SUPPORTED_MODELS.get(alias.lower(), alias)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    print("✅ 云雾API多模态模型接口已就绪")
    print("\n支持的模型:")
    print("  1. GPT-4 Vision (gpt-4-vision-preview)")
    print("  2. GPT-4 Turbo (gpt-4-turbo)")
    print("  3. Claude 3 Opus (claude-3-opus-20240229)")
    print("  4. Claude 3 Sonnet (claude-3-sonnet-20240229)")
    print("  5. Gemini Pro Vision (gemini-pro-vision)")
    print("\n使用示例:")
    print("  # 方式1: 使用完整模型名")
    print("  model = create_model('gpt-4-vision-preview')")
    print("  # 方式2: 使用别名")
    print("  model = create_model('gpt4v')")
    print("  # 生成响应")
    print("  response = model.generate(prompt='描述图片', images=['image.jpg'])")
