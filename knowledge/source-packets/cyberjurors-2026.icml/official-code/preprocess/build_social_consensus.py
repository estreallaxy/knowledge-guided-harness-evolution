"""
构建社会共识库的主脚本。

该脚本会读取指定的案件数据，为每个案件生成可复用的评审规则，
并动态地使用RAG（检索增强生成）来参考相似历史案例的规则，
最终将原始案例和生成的规则存储到社会共识库JSON文件中。
"""
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from copy import deepcopy
import concurrent.futures
import time


# 动态添加项目根目录到sys.path
try:
    from utils.multimodal_models import create_model, YunwuModel
    from utils_syh import load_real_cases, parse_case_to_standard_format
except ImportError:
    import sys
    repo_root = Path(__file__).resolve().parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from utils.multimodal_models import create_model, YunwuModel
    from utils_syh import load_real_cases, parse_case_to_standard_format

# RAG 功能所需的依赖
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    try:
        from transformers import AutoTokenizer
    except Exception:
        AutoTokenizer = None
except ImportError:
    print("="*80)
    print("⚠️  缺少RAG功能所需的库。请运行: pip install sentence-transformers scikit-learn")
    print("="*80)
    SentenceTransformer = None
    cosine_similarity = None
    np = None


    np = None


def build_rag_source_text(case_like: Dict) -> str:
    """为 RAG 构建用于编码的文本表示，支持传入原始 case 或包含 `case_data` 的条目。

    内容包括：title、buyer_claim、seller_claim、所有证据的文本（buyer/seller）、以及 reviewer 的观点摘要。
    """
    # 支持传入两种形态：如果是 Social_Consensus 条目则取 'case_data'
    case = case_like.get('case_data', case_like) if isinstance(case_like, dict) else case_like
    parts = []
    parts.append(str(case.get('title', '') or ''))
    parts.append(str(case.get('buyer_claim', '') or ''))
    parts.append(str(case.get('seller_claim', '') or ''))

    # 收集买家/卖家证据文本
    for ev in case.get('buyer_evidence', []):
        parts.append(str(ev.get('text', '') or ''))
    for ev in case.get('seller_evidence', []):
        parts.append(str(ev.get('text', '') or ''))


    # 拼接并返回
    return ' \n '.join([p for p in parts if p])


def init_rag(cases_with_reflection: List[Dict], embedding_model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2') -> Optional[Tuple[Any, Any, Any]]:
    """
    根据已有规则的案例初始化RAG模型和索引（使用更丰富的文本表示）。
    """
    # 规范化路径，防止 Windows 路径问题
    try:
        if os.path.exists(embedding_model_name):
            embedding_model_name = os.path.abspath(embedding_model_name)
    except:
        pass

    print(f"ℹ️ 发现 {len(cases_with_reflection)} 个已有规则的案例，正在初始化RAG（模型={embedding_model_name}）...")
    if not cases_with_reflection:
        return None
    try:
        # embedding_model_name 可以是 HF 模型名或本地目录路径
        def _resolve_local_snapshot(path: str) -> Optional[str]:
            # 如果是本地目录，尝试查找 snapshots 子目录或权重文件
            try:
                if os.path.isdir(path):
                    snaps_dir = os.path.join(path, 'snapshots')
                    if os.path.isdir(snaps_dir):
                        snaps = [d for d in os.listdir(snaps_dir) if os.path.isdir(os.path.join(snaps_dir, d))]
                        if snaps:
                            snaps.sort()
                            return os.path.join(snaps_dir, snaps[-1])
                    # 检查目录本身是否包含权重文件
                    for fname in ('pytorch_model.bin','model.safetensors','tf_model.h5','model.ckpt.index','flax_model.msgpack'):
                        if os.path.exists(os.path.join(path, fname)):
                            return path
                    return None
            except Exception:
                return None
            return path

        resolved_path = embedding_model_name
        # 如果用户传入的是本地目录，尝试解析到实际快照目录
        if os.path.exists(embedding_model_name) and os.path.isdir(embedding_model_name):
            candidate = _resolve_local_snapshot(embedding_model_name)
            if candidate:
                resolved_path = candidate
            else:
                # 如果无法解析到有效快照，保留原始输入以便后续报错更清晰
                resolved_path = embedding_model_name

        rag_model = None
        # 如果是 Longformer-like 的模型（需要长上下文处理），优先用 Transformer+Pooling 构建 SentenceTransformer
        if "longformer" in str(resolved_path).lower() or "longformer" in embedding_model_name.lower():
            try:
                from sentence_transformers import models as st_models
                transformer = st_models.Transformer(resolved_path, max_seq_length=4096)
                pooling = st_models.Pooling(transformer.get_word_embedding_dimension(), pooling_mode_mean_tokens=True)
                rag_model = SentenceTransformer(modules=[transformer, pooling])
                rag_model.max_seq_length = 4096
                if hasattr(rag_model, 'tokenizer'):
                    rag_model.tokenizer.model_max_length = 4096
                print(f"  🔧 使用 Transformer+Pooling 构建 Longformer SentenceTransformer（path={resolved_path}）")
            except Exception as e:
                print(f"  ⚠️ 无法用 Transformer+Pooling 构建 Longformer SentenceTransformer: {e}")
                rag_model = None

        # 如果上面未成功构建（或非 Longformer），尝试以常规方式加载 SentenceTransformer
        if rag_model is None:
            try:
                rag_model = SentenceTransformer(resolved_path)
            except Exception as e:
                # 最后给出更友好的错误提示
                raise RuntimeError(f"无法加载 embedding 模型 (尝试: {resolved_path}). 原始错误: {e}")

        case_texts = []
        for item in cases_with_reflection:
            # item 可能是 Social_Consensus 条目：{'case_data': ..., 'reflection': ...}
            raw = item.get('case_data', item) if isinstance(item, dict) else item
            try:
                std = parse_case_to_standard_format(raw)
            except Exception:
                std = raw
            case_texts.append(build_rag_source_text(std))
        
        # 编码时确保使用截断，防止超出模型范围
        rag_index = rag_model.encode(case_texts, show_progress_bar=True, convert_to_numpy=True)
        
        # 存储每个索引对应的规则
        rag_rules = [item.get('reflection', {}).get('reflection_result', []) for item in cases_with_reflection]
        print("✅ RAG初始化完成（使用 title + 证据文本 + reviewer 视角）。")
        return rag_model, rag_index, rag_rules
    except Exception as e:
        print(f"❌ RAG模型加载或索引构建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def find_similar_rules(query_text: str, k: int, rag_bundle: Tuple[Any, Any, Any], cases_with_reflection: List[Dict]) -> List[str]:
    """使用RAG查找相似案例的规则。"""
    rag_model, rag_index, rag_rules = rag_bundle
    if not rag_model or rag_index is None:
        return []
    
    try:
        # 确保 rag_index 是 numpy 数组且形状合理
        rag_index = np.asarray(rag_index)
        # 如果只有一个向量，reshape 为 (1, dim)
        if rag_index.ndim == 1:
            rag_index = rag_index.reshape(1, -1)

        # 计算 query embedding
        query_embedding = rag_model.encode([query_text])

        # 计算相似度，确保结果是一维的相似度数组
        sims = cosine_similarity(query_embedding, rag_index)
        if sims.ndim == 2:
            similarities = sims[0]
        else:
            similarities = np.asarray(sims)

        n_docs = len(rag_rules)
        if similarities.shape[0] != n_docs:
            print(f"⚠️ RAG 索引长度不匹配: similarities={similarities.shape[0]}, rag_rules={n_docs}，跳过RAG检索。")
            return []

        # 如果 k 大于文档数，取文档数
        k_take = min(k, n_docs)
        if k_take <= 0:
            return []

        top_k_indices = np.argsort(similarities)[-k_take:][::-1]

        similar_rules_found = []
        print("\n--- 🔍 RAG检索到相似案例规则 ---")
        for idx in top_k_indices:
            # 索引应当在范围内，额外保护
            if idx < 0 or idx >= n_docs:
                continue
            try:
                rules = rag_rules[int(idx)]
                case_id = cases_with_reflection[int(idx)].get('id', 'N/A')
            except Exception:
                continue
            # 合并规则（可能是列表）
            if isinstance(rules, list):
                similar_rules_found.extend(rules)
            else:
                similar_rules_found.append(str(rules))
            print(f"  - Case {case_id}: {rules}")
        print("---------------------------------")
        return similar_rules_found
    except Exception as e:
        print(f"❌ RAG检索失败: {e}")
        return []

def build_reflection_prompt(case_data: Dict, similar_rules: Optional[List[str]] = None) -> Tuple[str, List[str], List[str]]:
    """构建用于提取规则的提示词。"""
    ground_truth = case_data.get('ground_truth', {})
    buyer_views = "\n".join([f"- {v}" for v in ground_truth.get('reviewer4buyer_views', [])])
    seller_views = "\n".join([f"- {v}" for v in ground_truth.get('reviewer4seller_views', [])])

    product_info_text = case_data.get('product_info', {}).get('text', '无')

    # 2. 收集所有媒体文件路径，并为每张图片/视频分配全局索引
    all_images = []
    all_videos = []
    visual_index_lines = []  # 用于在prompt中说明每个索引对应的文件及所属证据

    buyer_evidence_text = []
    img_idx = 0
    vid_idx = 0
    # 处理买家证据，记录每个证据下的图片/视频索引
    for i, ev in enumerate(case_data.get('buyer_evidence', [])):
        text = ev.get('text', '无文本描述')
        img_paths = ev.get('image_paths', [])
        vid_paths = ev.get('video_paths', [])
        img_indices = []
        vid_indices = []
        for p in img_paths:
            img_idx += 1
            all_images.append(p)
            img_indices.append(f"IMG{img_idx}")
            visual_index_lines.append(f"IMG{img_idx}: {p} (属于 买家证据{i+1})")
        for p in vid_paths:
            vid_idx += 1
            all_videos.append(p)
            vid_indices.append(f"VID{vid_idx}")
            visual_index_lines.append(f"VID{vid_idx}: {p} (属于 买家证据{i+1})")
        buyer_evidence_text.append(f"  - 买家证据{i+1} (含{len(img_paths)}图: {img_indices if img_indices else []}, {len(vid_paths)}视频: {vid_indices if vid_indices else []}): {text}")

    seller_evidence_text = []
    # 处理卖家证据，继续使用同一组全局索引
    for i, ev in enumerate(case_data.get('seller_evidence', [])):
        text = ev.get('text', '无文本描述')
        img_paths = ev.get('image_paths', [])
        vid_paths = ev.get('video_paths', [])
        img_indices = []
        vid_indices = []
        for p in img_paths:
            img_idx += 1
            all_images.append(p)
            img_indices.append(f"IMG{img_idx}")
            visual_index_lines.append(f"IMG{img_idx}: {p} (属于 卖家证据{i+1})")
        for p in vid_paths:
            vid_idx += 1
            all_videos.append(p)
            vid_indices.append(f"VID{vid_idx}")
            visual_index_lines.append(f"VID{vid_idx}: {p} (属于 卖家证据{i+1})")
        seller_evidence_text.append(f"  - 卖家证据{i+1} (含{len(img_paths)}图: {img_indices if img_indices else []}, {len(vid_paths)}视频: {vid_indices if vid_indices else []}): {text}")

    buyer_evidence_summary = "\n".join(buyer_evidence_text)
    seller_evidence_summary = "\n".join(seller_evidence_text)
    visual_index_text = "\n".join(visual_index_lines)
    winner_index = case_data.get('ground_truth', {}).get('whowins', -1)
    # 保证 winner 始终被定义，防止未包含 ground_truth 或值异常导致 UnboundLocalError
    winner = "未知"
    if winner_index == 0:
        winner = "买家"
    elif winner_index == 1:
        winner = "卖家"


    prompt = f"""你是一个资深的电商纠纷分析师，你的任务是从大众评审的意见中提炼出1到3条具有普适性的、可复用到其他相似案例的评审规则或要点。
##本案件详细信息
### 案件背景
- **争议焦点**: {case_data.get('title', 'N/A')}
- **买家主张**: {case_data.get('buyer_claim', 'N/A')}
- **卖家主张**: {case_data.get('seller_claim', 'N/A')}

- **买家证据描述**:{buyer_evidence_summary}
- **卖家证据描述**:{seller_evidence_summary}

视觉信息索引说明:
{visual_index_text}

##以下是大众评审根据案件的详细信息给出的的意见摘要：
### 大众评审意见

**支持买家的意见:**
{buyer_views if buyer_views else "无"}

**支持卖家的意见:**
{seller_views if seller_views else "无"}

##
最终评审结果：获胜者是 【{winner}】。
"""

    if similar_rules:
        rules_text = "\n".join([f"- {rule}" for rule in similar_rules])
        prompt += f"""
### 相似历史案例的规则参考 (RAG)
在分析当前案件时，请参考以下从相似历史案例中总结出的规则，这有助于你形成更具一致性的结论：
{rules_text}
"""

    prompt += """
### 你的任务
请基于上方所有的“大众评审意见”，并结合“相似历史案例的规则参考”（如果有），总结出2至4条核心的、可跨案例复用的评审规则。

**输出要求:**
1.  **高度浓缩**: 规则应该是对一类问题的通用判断标准，而不是只针对本案的细节，且需要简洁凝练。
2.  **中立客观**: 规则应以第三方视角陈述，例如“当商品存在未告知的严重瑕疵时，‘售出不退’条款通常无效。”
3.  **格式严格**: 必须以JSON格式输出，且仅包含一个`reflection_result`字段，其值为一个包含2到4个字符串的数组。

**输出示例:**
{
  "reflection_result": [
    "规则1：...",
    "规则2：..."
  ]
}
"""
    return prompt,all_images, all_videos

def parse_reflection_result(response: str) -> List[str]:
    """从模型响应中解析出规则列表。"""
    import re
    json_str = None
    
    # 优先尝试用正则表达式提取 ```json ... ``` 或 ``` ... ``` 中的内容
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # 如果没有找到Markdown块，尝试寻找第一个 { 和最后一个 } 之间的内容
        match = re.search(r'(\{.*\})', response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # 如果连花括号都找不到，可能整个响应就是JSON
            json_str = response

    if not json_str:
        print(f"    ⚠️  解析规则失败: 响应中未找到有效的JSON结构。")
        return []

    try:
        data = json.loads(json_str)
        rules = data.get("reflection_result", [])
        if isinstance(rules, list) and all(isinstance(r, str) for r in rules):
            return rules
        else:
            print(f"    ⚠️  解析规则失败: 'reflection_result' 字段格式不正确。")
            return []
    except json.JSONDecodeError as e:
        print(f"    ⚠️  解析规则失败: JSON解码错误 - {e}")
        return []

def process_case(
    raw_case: Dict, 
    model: YunwuModel, 
    rag_bundle: Optional[Tuple], 
    cases_with_reflection: List[Dict],
    output_path: Path
) -> Tuple[Optional[str], Optional[Dict]]:
    """
    处理单个案件：如果缺少 'reflection'，则生成规则并立即追加到输出文件中。
    返回 (case_id, new_entry)
    """
    case_id = raw_case.get('id') or raw_case.get('original_id') or raw_case.get('case_id', 'N/A')
    
    print(f"\n🔥 正在为案件生成规则: {case_id}")

    # 创建标准化视图供 prompt 使用
    try:
        standard_case = parse_case_to_standard_format(raw_case)
    except Exception:
        # 若解析失败，仍使用原始数据作为后备
        standard_case = raw_case

    # 1. RAG检索 (如果启用)
    similar_rules = []
    if rag_bundle:
        # 使用更丰富的文本作为查询：title + 买卖双方陈述 + 证据文本（不包含 reviewer 信息）
        query_text = build_rag_source_text(standard_case if standard_case else raw_case)
        similar_rules = find_similar_rules(query_text, k=3, rag_bundle=rag_bundle, cases_with_reflection=cases_with_reflection)

    # 2. 构建并调用模型（使用标准化数据构建 prompt）
    prompt, images, videos = build_reflection_prompt(standard_case, similar_rules)

    print(f"  - 正在调用模型生成评审规则 (Case {case_id})...")
    try:
        response_text = model.generate(prompt, images=images, videos=videos)
    except Exception as e:
        print(f"  ❌ 模型调用失败 (Case {case_id}): {e}")
        return case_id, None
    
    # 3. 解析并验证结果
    reflection_rules = parse_reflection_result(response_text)
    
    if not reflection_rules:
        print(f"  ❌ 未能从模型响应中提取有效规则，案件 {case_id} 本次不更新。")
        return case_id, None

    print(f"  ✅ 成功生成 {len(reflection_rules)} 条规则 (Case {case_id})。")

    # 4. 创建新条目并追加到JSON文件中
    new_entry = {
        "case_data": raw_case,
        "reflection": {
            "reflection_result": reflection_rules
        }
    }

    try:
        # 读取现有数据，追加新条目，然后写回
        # 注意：多线程环境下，文件写入需要加锁，或者改为由主线程统一写入。
        # 这里为了简单起见，我们使用简单的重试机制或假设文件系统锁（不完美但可用），
        # 或者更好的方式是：process_case 只返回结果，由主线程统一写入。
        # 鉴于用户要求多线程，我们将改为：process_case 只负责生成，主线程负责写入。
        return case_id, new_entry
    except Exception as e:
        print(f"  ❌ 处理失败 (Case {case_id}): {e}")
        return case_id, None


def main():
    parser = argparse.ArgumentParser(description="为数据集中的案件生成并补充社会共识规则")
    parser.add_argument('--data_file', type=str, default='dataset/train_new_new.json', help='包含源案例的JSON文件路径（只读）')
    parser.add_argument('--output_file', type=str, default='Social_Consensus.json', help='保存社会共识的输出JSON文件路径')
    parser.add_argument('--model', type=str, default='gemini-2.5-flash-thinking', help='用于分析和总结的大模型')
    parser.add_argument('--limit', type=int, default=None, help='限制本次运行处理的案例数量')
    parser.add_argument('--rag_threshold', type=int, default=10, help='RAG启动的案例数阈值')
    parser.add_argument('--rag_rebuild_interval', type=int, default=20, help='每处理多少个案例后重建一次RAG索引')
    parser.add_argument('--parallel_workers', type=int, default=20, help='并行处理的线程数')
    parser.add_argument('--api_key', type=str, default='REDACTED_UPSTREAM_CREDENTIAL', help='YUNWU API Key（优先于代码中的默认值）')
    parser.add_argument('--base_url', type=str, default='https://yunwu.ai/v1', help='YUNWU Base URL（优先于代码中的默认值）')
    parser.add_argument('--embedding_model', type=str, default=r'C:\Users\artemi154\.cache\huggingface\hub\models--allenai--longformer-base-4096', help='用于RAG的embedding模型名称或本地路径（sentence-transformers 支持的名称或本地目录）')
    args = parser.parse_args()

    # 定义输入和输出文件路径
    data_file_path = Path(args.data_file)
    output_path = Path(args.output_file)

    if not data_file_path.exists():
        print(f"❌ 错误: 数据文件不存在于 {args.data_file}")
        return

    model = create_model(model_name=args.model, api_key=args.api_key, base_url=args.base_url)

    # 1. 加载已有的社会共识数据
    social_consensus_data = []
    if output_path.exists():
        print(f"📂 发现已存在的共识文件，正在加载: {output_path}")
        try:
            social_consensus_data = load_real_cases(dataset_path=str(output_path))
        except json.JSONDecodeError:
            print(f"⚠️  警告: {output_path} 文件格式错误或为空，将作为新文件处理。")
            social_consensus_data = []
    
    processed_case_ids = {
        item['case_data'].get('id') or item['case_data'].get('original_id') or item['case_data'].get('case_id')
        for item in social_consensus_data
    }

    # 2. 加载所有源案例
    print(f"📂 正在加载源数据文件: {args.data_file}")
    all_source_cases = load_real_cases(dataset_path=args.data_file)
    if not all_source_cases:
        print("❌ 未能从源文件加载任何案例，程序退出。")
        return

    # 3. 筛选出需要处理的新案例
    cases_to_process = [
        case for case in all_source_cases 
        if (case.get('id') or case.get('original_id') or case.get('case_id')) not in processed_case_ids
    ]
    
    # 如果设置了limit，则截断待处理列表
    if args.limit is not None:
        cases_to_process = cases_to_process[:args.limit]

    print(f"\n{'='*20} 开始构建社会共识 {'='*20}")
    print(f"  源案例总数: {len(all_source_cases)}")
    print(f"  已处理并保存在 {output_path.name}: {len(social_consensus_data)} 个")
    print(f"  本次将处理 {len(cases_to_process)} 个新案件。")
    print(f"  并行线程数: {args.parallel_workers}")
    print(f"  RAG重建间隔: {args.rag_rebuild_interval}")
    print(f"{'='*60}\n")

    # 4. 获取初始的、已包含规则的案例列表，用于RAG
    cases_with_reflection_for_rag = [
        item for item in social_consensus_data if 'reflection' in item and item['reflection']
    ]

    # 初始化 RAG (如果已有数据足够)
    rag_bundle = None
    if len(cases_with_reflection_for_rag) >= args.rag_threshold:
        rag_bundle = init_rag(cases_with_reflection_for_rag, embedding_model_name=args.embedding_model)

    # 5. 批量处理循环
    batch_size = args.rag_rebuild_interval
    total_processed = 0
    
    # 将待处理案例分批
    batches = [cases_to_process[i:i + batch_size] for i in range(0, len(cases_to_process), batch_size)]

    for batch_idx, batch in enumerate(batches):
        print(f"\n🚀 开始处理第 {batch_idx + 1}/{len(batches)} 批次 (本批 {len(batch)} 个案例)...")
        
        new_entries_in_batch = []
        
        # 使用 ThreadPoolExecutor 并行处理当前批次
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel_workers) as executor:
            # 提交任务
            future_to_case = {
                executor.submit(process_case, case, model, rag_bundle, cases_with_reflection_for_rag, output_path): case 
                for case in batch
            }
            
            # 获取结果
            for future in concurrent.futures.as_completed(future_to_case):
                case_id, new_entry = future.result()
                if new_entry:
                    new_entries_in_batch.append(new_entry)
                    total_processed += 1

        # 批次处理完成后，统一写入文件（避免多线程写入冲突）
        if new_entries_in_batch:
            print(f"💾 正在将本批次 {len(new_entries_in_batch)} 个新结果写入文件...")
            try:
                # 重新读取以防其他进程修改（虽然这里主要是单进程多线程）
                current_data = []
                if output_path.exists():
                    with open(output_path, 'r', encoding='utf-8') as f:
                        current_data = json.load(f)
                
                current_data.extend(new_entries_in_batch)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(current_data, f, ensure_ascii=False, indent=2)
                
                # 更新内存中的 RAG 数据源
                cases_with_reflection_for_rag.extend(new_entries_in_batch)
                print(f"✅ 本批次写入完成。")
            except Exception as e:
                print(f"❌ 批量写入文件失败: {e}")

        # 检查是否需要重建 RAG 索引 (如果本批次有新数据且总数达到阈值)
        if new_entries_in_batch and len(cases_with_reflection_for_rag) >= args.rag_threshold:
            print(f"\n🔄 触发 RAG 索引重建 (当前库大小: {len(cases_with_reflection_for_rag)})...")
            rag_bundle = init_rag(cases_with_reflection_for_rag, embedding_model_name=args.embedding_model)
        
    print(f"\n{'='*20} 构建完成 {'='*20}")
    # 重新加载最终数据以获取最新计数
    final_data = load_real_cases(dataset_path=str(output_path)) if output_path.exists() else []
    print(f"  现在共有 {len(final_data)} 个案件拥有共识规则。")
    print(f"{'='*60}\n")



if __name__ == '__main__':
    main()
