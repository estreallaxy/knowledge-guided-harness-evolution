import json
import os
import sys
import time
from pathlib import Path
from tqdm import tqdm

# 添加项目根目录到 sys.path 以便导入 multimodal_models
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.append(str(PROJECT_ROOT))

from utils.multimodal_models import YunwuModel

# ================= 配置区域 =================
# 请在此处填入您的 API Key
API_KEY = "REDACTED_UPSTREAM_CREDENTIAL" 
MODEL_NAME = "gemini-2.5-flash-lite-nothinking" # 支持视觉的模型名称

# 文件路径配置
# INPUT_FILE = PROJECT_ROOT / "dataset" / "splits" / "train_list.json"
INPUT_FILE = PROJECT_ROOT / "dataset" / "train_new.json"
OUTPUT_FILE = PROJECT_ROOT / "dataset" / "train_new_new.json"
ERROR_LOG_FILE = PROJECT_ROOT / "data_preprocess" / "failed_cases_train.json"
# INPUT_FILE =  "./dataset/splits/val_list.json"
# OUTPUT_FILE = "./dataset/val_new.json"

# 提示词配置
BASE_PROMPT = "这是一起电商纠纷中的证据图片/视频帧。请详细描述画面内容，特别是与商品质量、物流状态、聊天记录或交易细节相关的部分，以作为补充证据。"
# ===========================================

def process_dataset():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    # 初始化多模态模型

    model = YunwuModel(model_name=MODEL_NAME, api_key=API_KEY)
    print(f"Model {MODEL_NAME} initialized successfully.")

    print(f"Reading from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modified_count = 0
    failed_cases = []  # 记录失败的案件
    
    # 遍历所有案例
    for case in tqdm(data, desc="Processing cases"):
        case_modified = False
        
        # 提取案例背景信息
        case_data = case.get("case_data", {})
        title = case_data.get("title", "未知")
        buyer_claim = case_data.get("buyer_claim", "未知")
        seller_claim = case_data.get("seller_claim", "未知")
        
        # 提取第一个买家证据的文本（通常是商品详情）
        product_details = "未知"
        case_details = case.get("case_details", {})
        evidences = case_details.get("evidences", [])
        
        for ev in evidences:
            if ev.get("identity") == "买家":
                content = ev.get("content", {})
                if content and content.get("text"):
                    product_details = content.get("text")
                    break
        
        for ev in evidences:
            content = ev.get("content", {})
            if not content:
                continue
                
            text = content.get("text", "")
            video_paths = content.get("video_paths")
            image_paths = content.get("image_paths")
            
            # 判断逻辑：
            # 1. 文本仅包含系统生成的元数据（身份、操作、时间），没有用户输入的描述
            #    典型格式为3行：
            #    买家
            #    买家提交了凭证
            #    12-02 19:40:34
            # 2. 存在图片或视频路径
            lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
            is_system_text = len(lines) == 3 and "提交了凭证" in text
            
            has_media = (video_paths and len(video_paths) > 0) or (image_paths and len(image_paths) > 0)
            
            if is_system_text and has_media:
                # 收集所有需要识别的图片和视频路径
                valid_image_paths = []
                valid_video_paths = []
                
                # 处理图片路径
                if image_paths:
                    for img_p in image_paths:
                        # 处理路径：移除开头的 ./ 并拼接项目根目录
                        clean_path = img_p.lstrip("./").lstrip(".\\")
                        full_path = PROJECT_ROOT / clean_path
                        
                        if full_path.exists():
                            valid_image_paths.append(str(full_path))
                        else:
                            # 尝试在 dataset 目录下查找（兼容不同路径格式）
                            alt_path = PROJECT_ROOT / "dataset" / clean_path
                            if alt_path.exists():
                                valid_image_paths.append(str(alt_path))
                            else:
                                print(f"Warning: Image not found: {img_p}")

                # 处理视频路径
                if video_paths:
                    for vid_p in video_paths:
                        clean_path = vid_p.lstrip("./").lstrip(".\\")
                        full_path = PROJECT_ROOT / clean_path
                        
                        if not full_path.exists():
                             alt_path = PROJECT_ROOT / "dataset" / clean_path
                             if alt_path.exists():
                                 full_path = alt_path
                        
                        if full_path.exists():
                            valid_video_paths.append(str(full_path))
                        else:
                            print(f"Warning: Video not found: {vid_p}")
                
                # 如果有有效的媒体文件，调用大模型
                if valid_image_paths or valid_video_paths:
                    print(f"\nGenerating description for case {case.get('id', 'unknown')}...")
                    
                    # 构建动态提示词
                    dynamic_prompt = f"""{BASE_PROMPT}

                    案例背景信息：
                    - 纠纷标题：{title}
                    - 买家主张：{buyer_claim}
                    - 卖家主张：{seller_claim}
                    - 商品/交易详情：{product_details}

                    请结合上述背景信息，客观描述画面中呈现的事实。

                    你的回答应当遵循以下格式：
                    {{"description": "这里是对图片/视频内容的详细描述，特别关注与纠纷相关的细节。"}}
                    """

                    # 调用大模型生成描述（带重试机制）
                    # 它会自动处理图片编码和视频抽帧
                    description = None
                    max_retries = 3
                    retry_delay = 1.0
                    last_error = None
                    
                    for attempt in range(max_retries):
                        try:
                            description = model.generate(
                                prompt=dynamic_prompt,
                                images=valid_image_paths if valid_image_paths else None,
                                videos=valid_video_paths if valid_video_paths else None
                            )
                            
                            # 检查是否成功
                            if description and description != "{}":
                                break  # 成功，跳出重试循环
                            else:
                                raise ValueError("模型返回空响应或无效JSON")
                                
                        except Exception as e:
                            last_error = str(e)
                            if attempt < max_retries - 1:
                                print(f"  ⚠️  生成失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                                print(f"  → 等待 {retry_delay}秒后重试...")
                                time.sleep(retry_delay)
                                retry_delay *= 2  # 指数退避
                            else:
                                print(f"  ❌ 生成失败，已达最大重试次数: {e}")
                                description = None
                                
                    if description is  None:
                        # 记录失败信息
                        failed_cases.append({
                            "case_id": case.get('id', 'unknown'),
                            "error": last_error,
                            "image_paths": valid_image_paths,
                            "video_paths": valid_video_paths,
                            "evidence_text": text[:200] + "..." if len(text) > 200 else text
                        })
                
                    
                    if description is not None and description != "{}":
                        # 更新文本：保留原文本，追加描述
                        new_text = text + "\n\n【系统补充视觉描述】：\n" + description
                        content["text"] = new_text
                        modified_count += 1
                        case_modified = True
                        print(f"  ✓ Updated text for evidence in case {case.get('id', 'unknown')}")

        if case_modified:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    # 保存结果
    print(f"\nSaving results to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 保存失败日志
    if failed_cases:
        print(f"\n⚠️  有 {len(failed_cases)} 个案件处理失败")
        print(f"保存失败日志到 {ERROR_LOG_FILE}...")
        
        # 创建详细的失败报告
        error_report = {
            "total_failed": len(failed_cases),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "failed_cases": failed_cases
        }
        
        with open(ERROR_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(error_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n失败案件列表:")
        for i, fail in enumerate(failed_cases, 1):
            print(f"  {i}. 案件ID: {fail['case_id']}")
            print(f"     错误: {fail['error']}")
            print(f"     图片数: {len(fail['image_paths'])}, 视频数: {len(fail['video_paths'])}")
            print()
    else:
        print(f"\n✓ 所有案件处理成功！")
    
    print(f"\n统计信息:")
    print(f"  - 成功更新: {modified_count} 个证据")
    print(f"  - 失败案件: {len(failed_cases)} 个")
    print(f"Done!")

if __name__ == "__main__":
    process_dataset()
