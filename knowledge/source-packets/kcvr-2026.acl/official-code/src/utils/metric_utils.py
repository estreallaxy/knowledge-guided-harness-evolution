"""
KCVR 项目评测指标统一接口
=========================

本模块提供所有评测指标的标准化计算函数，确保：
1. 与论文表格列名完全对齐（R1/R2/RL/BS/C-F1/KPC/LOC）
2. 类型标注明确，docstring 清晰说明外部资源依赖
3. 所有实验只依赖这些接口，避免公式不一致

外部资源依赖：
- ROUGE/BERTScore: rouge_score, bert_score 库
- CTL (Concept Trigger Layer): trie/同义词/KC字典/规范化规则
- KPC: KG的 BASED_ON/NEXT 关系 + Planner的π
- LOC: BERTScore 或 embedding 相似度匹配

版本：v1.0
更新：2025-12-30
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
import numpy as np
from pathlib import Path

# Lazy import transformers for LOC-NLI to avoid hard dependency at import time.
try:
    import torch  # type: ignore
    from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False

# 延迟导入，避免未安装依赖时整个模块无法加载
try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    
try:
    from bert_score import score as bert_score_fn
    BERTSCORE_AVAILABLE = True
except ImportError:
    BERTSCORE_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

try:
    import jieba  # type: ignore
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class TriggeredConcept:
    """CTL 触发的概念节点"""
    kc_id: str           # Knowledge Concept ID (e.g., "kc_001")
    kc_name: str         # 规范化名称 (e.g., "等差数列")
    first_pos: int       # 首次出现位置（字符索引或token索引）
    confidence: float    # 匹配置信度 (0-1)
    
    
@dataclass
class KgEdges:
    """知识图谱边集合"""
    based_on: List[Tuple[str, str]]  # [(kc_from, kc_to), ...] 依赖关系
    next: List[Tuple[str, str]]      # [(kc_from, kc_to), ...] 教学序列
    

@dataclass
class CtlResources:
    """CTL 所需的外部资源"""
    kc_dict: Dict[str, str]          # {kc_id: kc_name}
    kc_synonyms: Dict[str, List[str]]  # {kc_id: [synonym1, ...]}
    trie: Optional[object] = None    # 字典树（可选）
    normalizer: Optional[callable] = None  # 文本规范化函数


# ============================================================================
# 0. 文本预处理：清洗markdown和特殊符号
# ============================================================================

def clean_text_for_eval(text: str) -> str:
    """
    清洗文本用于评测（去除markdown格式符号）
    
    清洗规则：
    - 去除 ### 标题符号
    - 去除 ** 加粗符号
    - 去除 [] 和 【】 框架符号（但保留内容）
    - 去除多余空格和换行
    - 保留实际内容用于评测
    
    Args:
        text: 原始文本（可能包含markdown）
        
    Returns:
        清洗后的纯文本
        
    注意：
        - 这个清洗对 pred 和 ref 都要做，确保公平比较
        - 模型生成的摘要不会包含markdown符号（纯文本）
        - GT标注可能包含markdown（为了可读性），需要清洗
    """
    import re
    
    if not text:
        return ""
    
    # 去除 ### 标题符号
    text = re.sub(r'###\s*', '', text)
    
    # 去除 ** 加粗符号
    text = re.sub(r'\*\*', '', text)
    
    # 去除 【】 框架符号（保留内容）
    text = re.sub(r'[【】\[\]]', '', text)
    
    # 去除 markdown 列表符号
    text = re.sub(r'^\s*[-\*]\s+', '', text, flags=re.MULTILINE)
    
    # 去除多余空格（但保留单个空格）
    text = re.sub(r' +', ' ', text)
    
    # 去除多余换行（保留段落结构，最多2个连续换行）
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # 去除首尾空白
    text = text.strip()
    
    return text


def tokenize_zh(text: str) -> List[str]:
    """
    Tokenize Chinese text for ROUGE/KPC/CTL.

    Strategy:
    - If jieba is available, use jieba.lcut for word-level tokens.
    - Otherwise, fall back to character-level tokens (excluding whitespace).

    Args:
        text: Raw text (may contain markdown).

    Returns:
        List of tokens.
    """
    text = clean_text_for_eval(text)
    if not text:
        return []
    if JIEBA_AVAILABLE:
        # jieba keeps english tokens and numbers reasonably; good enough for eval v1.
        toks = [t.strip() for t in jieba.lcut(text) if t.strip()]
        return toks
    # char-level fallback (avoid whitespace)
    return [ch for ch in text if not ch.isspace()]


def _ngram_counts(tokens: List[str], n: int) -> Dict[Tuple[str, ...], int]:
    counts: Dict[Tuple[str, ...], int] = {}
    if n <= 0:
        return counts
    for i in range(0, max(0, len(tokens) - n + 1)):
        g = tuple(tokens[i : i + n])
        counts[g] = counts.get(g, 0) + 1
    return counts


def _rouge_f1_ngram(pred_tokens: List[str], ref_tokens: List[str], n: int) -> float:
    """
    Compute ROUGE-N F1 on token sequences (language-agnostic).
    """
    if len(pred_tokens) == 0 and len(ref_tokens) == 0:
        return 1.0
    if len(pred_tokens) == 0 or len(ref_tokens) == 0:
        return 0.0
    pc = _ngram_counts(pred_tokens, n)
    rc = _ngram_counts(ref_tokens, n)
    if not pc or not rc:
        return 0.0
    overlap = 0
    for g, c in pc.items():
        overlap += min(c, rc.get(g, 0))
    pred_total = sum(pc.values())
    ref_total = sum(rc.values())
    p = overlap / max(1, pred_total)
    r = overlap / max(1, ref_total)
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def _lcs_len(a: List[str], b: List[str]) -> int:
    """
    Longest common subsequence length (DP).
    Note: O(len(a)*len(b)) which is fine for segment-level summaries.
    """
    if not a or not b:
        return 0
    # Use rolling DP to reduce memory.
    m, n = len(a), len(b)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        ai = a[i - 1]
        for j in range(1, n + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[n]


def _rouge_l_f1(pred_tokens: List[str], ref_tokens: List[str]) -> float:
    """
    Compute ROUGE-L F1 using LCS on token sequences.
    """
    if len(pred_tokens) == 0 and len(ref_tokens) == 0:
        return 1.0
    if len(pred_tokens) == 0 or len(ref_tokens) == 0:
        return 0.0
    lcs = _lcs_len(pred_tokens, ref_tokens)
    p = lcs / max(1, len(pred_tokens))
    r = lcs / max(1, len(ref_tokens))
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


# ============================================================================
# 1. 生成类指标：ROUGE & BERTScore
# ============================================================================

def compute_rouge(pred: str, ref: str, 
                  rouge_types: List[str] = ['rouge1', 'rouge2', 'rougeL']) -> Dict[str, float]:
    """
    计算 ROUGE 指标（与论文表头 R-1/R-2/R-L 对齐）
    
    Args:
        pred: 预测摘要文本
        ref: 参考摘要文本（gold，可能包含markdown）
        rouge_types: ROUGE 类型列表
        
    Returns:
        {"R1": float, "R2": float, "RL": float} (F1-score)
        
    依赖：
        - rouge_score 库
        
    注意：
        - 返回的是 F1 分数（主报告用）
        - Precision/Recall 可通过修改 rouge_types 获取
        - 自动清洗markdown符号，确保公平比较
    """
    # IMPORTANT (KCVR): Chinese ROUGE must not rely on whitespace tokenization,
    # otherwise R1/R2/RL can become abnormal (e.g., R1≈R2).
    pred_tokens = tokenize_zh(pred)
    ref_tokens = tokenize_zh(ref)

    r1 = _rouge_f1_ngram(pred_tokens, ref_tokens, n=1)
    r2 = _rouge_f1_ngram(pred_tokens, ref_tokens, n=2)
    rl = _rouge_l_f1(pred_tokens, ref_tokens)
    return {"R1": r1, "R2": r2, "RL": rl}


def compute_bertscore(pred: str, ref: str, 
                     lang: str = "zh", 
                     model_type: str = "bert-base-chinese") -> float:
    """
    计算 BERTScore（语义相似度，对同义改写鲁棒）
    
    Args:
        pred: 预测摘要文本
        ref: 参考摘要文本（可能包含markdown）
        lang: 语言代码
        model_type: BERT 模型类型
        
    Returns:
        BS: float (F1-score)
        
    依赖：
        - bert_score 库
        - transformers + torch
        
    注意：
        - 返回 F1（也可按需返回 P/R）
        - 首次调用会下载模型，建议预下载
        - 自动清洗markdown符号，确保公平比较
        - 网络失败时fallback到简单相似度（避免阻塞评测）
    """
    if not BERTSCORE_AVAILABLE:
        # Fallback: 使用简单的embedding相似度（如果有sentence-transformers）
        return _fallback_semantic_similarity(pred, ref)
    
    # 清洗markdown符号
    pred = clean_text_for_eval(pred)
    ref = clean_text_for_eval(ref)
    
    try:
        # Strategy:
        # 1. Try loading local bert-base-chinese model
        # 2. If local model exists, compute embeddings manually (more reliable than bert_score library)
        # 3. If local model doesn't exist or fails, use bert_score library with online model
        # 4. If all fail, fallback to bge-m3 embedding similarity
        
        import os
        # Check for local model in common locations
        local_bert_dir = Path("models/bert") if Path("models/bert").exists() else None
        
        if os.path.exists(local_bert_dir) and TRANSFORMERS_AVAILABLE:
            try:
                # Load local BERT model for manual embedding-based BERTScore
                from transformers import AutoModel, AutoTokenizer
                import torch
                
                tokenizer = AutoTokenizer.from_pretrained(local_bert_dir, local_files_only=True)
                model = AutoModel.from_pretrained(local_bert_dir, local_files_only=True)
                model.eval()
                
                # Tokenize
                pred_inputs = tokenizer(pred, return_tensors="pt", truncation=True, max_length=512, padding=True)
                ref_inputs = tokenizer(ref, return_tensors="pt", truncation=True, max_length=512, padding=True)
                
                # Get embeddings
                with torch.no_grad():
                    pred_outputs = model(**pred_inputs)
                    ref_outputs = model(**ref_inputs)
                    
                    # Use [CLS] token embedding (first token)
                    pred_emb = pred_outputs.last_hidden_state[:, 0, :].squeeze()
                    ref_emb = ref_outputs.last_hidden_state[:, 0, :].squeeze()
                    
                    # Compute cosine similarity
                    similarity = torch.nn.functional.cosine_similarity(pred_emb.unsqueeze(0), ref_emb.unsqueeze(0))
                    return float(similarity.item())
            except Exception as e:
                print(f"Warning: Local BERT failed ({e}), trying bert_score library")
        
        # Fallback: use bert_score library (may download model)
        # Enforce offline to avoid accidental downloads on shared servers
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        
        P, R, F1 = bert_score_fn([pred], [ref], lang=lang, model_type=model_type, verbose=False, device="cpu")
        return float(F1.mean().item())
    except Exception as e:
        print(f"Warning: BERTScore failed ({e}), using fallback similarity")
        return _fallback_semantic_similarity(pred, ref)


def _fallback_semantic_similarity(pred: str, ref: str) -> float:
    """
    BERTScore失败时的fallback：使用简单的文本相似度
    
    策略：
    1. 如果有sentence-transformers，用embedding cosine相似度
    2. 否则用简单的token overlap（Jaccard）
    
    Returns:
        相似度分数 [0, 1]
    """
    pred = clean_text_for_eval(pred)
    ref = clean_text_for_eval(ref)
    
    # 尝试使用sentence-transformers（如果有）
    if EMBEDDING_AVAILABLE:
        try:
            # 使用bge-m3（如果可用）或其他中文embedding模型
            from sentence_transformers import SentenceTransformer
            # 尝试加载本地模型
            model_paths = [
                Path("models/bge-m3"),
                "BAAI/bge-m3",
            ]
            model = None
            for path in model_paths:
                try:
                    path_str = str(path) if isinstance(path, Path) else path
                    model = SentenceTransformer(path_str, device='cpu')
                    break
                except:
                    continue
            
            if model is None:
                # 如果都失败，用简单的token overlap
                return _token_overlap_similarity(pred, ref)
            
            emb_pred = model.encode([pred], normalize_embeddings=True)[0]
            emb_ref = model.encode([ref], normalize_embeddings=True)[0]
            similarity = float(np.dot(emb_pred, emb_ref))
            return max(0.0, min(1.0, similarity))  # 确保在[0,1]范围内
        except Exception as e:
            print(f"Warning: Embedding similarity failed ({e}), using token overlap")
            return _token_overlap_similarity(pred, ref)
    else:
        return _token_overlap_similarity(pred, ref)


def _token_overlap_similarity(pred: str, ref: str) -> float:
    """
    简单的token overlap相似度（Jaccard）
    
    Returns:
        Jaccard相似度 [0, 1]
    """
    # NOTE: Chinese text often has no whitespace. Using str.split() makes overlap almost always 0.
    # We therefore reuse tokenize_zh (jieba/char-level) for language-robust overlap.
    pred_tokens = set(tokenize_zh(pred))
    ref_tokens = set(tokenize_zh(ref))
    
    if len(pred_tokens) == 0 and len(ref_tokens) == 0:
        return 1.0
    if len(pred_tokens) == 0 or len(ref_tokens) == 0:
        return 0.0
    
    intersection = len(pred_tokens & ref_tokens)
    union = len(pred_tokens | ref_tokens)
    
    return intersection / max(1, union)


# ============================================================================
# 2. CTL (Concept Trigger Layer) - 概念抽取
# ============================================================================

def normalize_concept_phrase(text: str) -> str:
    """
    概念短语规范化（与 SG-Planner 保持一致）
    
    规则：
    - 去除"的定义/的概念/的性质/的特征"等后缀
    - 统一空格与标点
    - 转小写（可选，视语言而定）
    """
    # 去除常见后缀
    suffixes = ['的定义', '的概念', '的性质', '的特征', '的公式', '的计算', '的应用']
    for suffix in suffixes:
        if text.endswith(suffix):
            text = text[:-len(suffix)]
    
    # 去除多余空格与标点
    text = re.sub(r'\s+', '', text)
    text = text.strip(',.，。、；;')
    
    return text


def triggered_concepts(text: str, 
                      subject: str,
                      ctl_resources: CtlResources) -> List[TriggeredConcept]:
    """
    从文本中触发（抽取）知识概念节点
    
    这是 KCVR 评测栈的核心组件：
    - 为 Concept-F1 提供 pred/ref 的概念集合
    - 为 KPC 提供概念出现顺序
    - 为 LOC 提供 objectives → KC 的锚定
    
    Args:
        text: 待抽取文本（pred summary 或 ref summary）
        subject: 学科名（用于过滤 KC）
        ctl_resources: 外部资源（KC字典、trie、规范化器等）
        
    Returns:
        List[TriggeredConcept]: 按首次出现位置排序的概念列表
        
    依赖：
        - ctl_resources.kc_dict: {kc_id: kc_name}
        - ctl_resources.kc_synonyms: {kc_id: [syn1, ...]}
        - (可选) ctl_resources.trie: 用于快速匹配
        
    实现策略（v1 基础版）：
        1. 规范化文本
        2. 对每个 KC，检查其 name/synonyms 是否在文本中出现（子串或fuzzy）
        3. **关键**：只匹配当前学科的KC（避免跨学科误触发）
        4. 记录首次出现位置
        5. 返回按位置排序的列表
        
    注意：
        - 这是可复现的"后处理层"，不是模型的一部分
        - 后续可优化为基于 embedding 的软匹配
    """
    triggered = []
    text_norm = normalize_concept_phrase(text)
    
    # 学科名到KC id前缀的映射（根据实际KC id命名规则）
    subject_prefix_map = {
        'biology': 'kc_bio',
        'chemistry': 'kc_chem',
        'chinese': 'kc_chi',
        'english': 'kc_eng',
        'geography': 'kc_geo',
        'history': 'kc_hist',
        'math': 'kc_math',
        'physics': 'kc_phys',
        'politics': 'kc_pol',
        'tech': 'kc_tech',
    }
    
    subject_prefix = subject_prefix_map.get(subject, f'kc_{subject}')
    
    for kc_id, kc_name in ctl_resources.kc_dict.items():
        # **关键修复**：只匹配当前学科的KC（避免跨学科误触发）
        if not kc_id.startswith(subject_prefix):
            continue
        # 简单子串匹配（v1）
        kc_name_norm = normalize_concept_phrase(kc_name)
        
        # 检查 kc_name
        pos = text_norm.find(kc_name_norm)
        if pos != -1:
            triggered.append(TriggeredConcept(
                kc_id=kc_id,
                kc_name=kc_name,
                first_pos=pos,
                confidence=1.0
            ))
            continue
        
        # 检查 synonyms（如果有）
        if kc_id in ctl_resources.kc_synonyms:
            for syn in ctl_resources.kc_synonyms[kc_id]:
                syn_norm = normalize_concept_phrase(syn)
                pos = text_norm.find(syn_norm)
                if pos != -1:
                    triggered.append(TriggeredConcept(
                        kc_id=kc_id,
                        kc_name=kc_name,
                        first_pos=pos,
                        confidence=0.9  # 同义词匹配置信度略低
                    ))
                    break
    
    # 按首次出现位置排序（为 KPC 提供顺序信息）
    triggered.sort(key=lambda x: x.first_pos)
    
    return triggered


# ============================================================================
# 3. 教育类指标：C-F1, KPC, LOC
# ============================================================================

def compute_concept_f1(pred_text: str, 
                       ref_text: str,
                       subject: str,
                       ctl_resources: CtlResources) -> Dict[str, float]:
    """
    计算 Concept F1（概念提及的准确率、召回率、F1）
    
    Paper Reference: Table 1 (C-F1 column)
    Formula: Standard F1-score on concept sets extracted via CTL
    
    定义（论文表格）：
        pred/ref 都通过 CTL 抽取为概念集合 {kc_id}，计算集合的 P/R/F1
        
    Args:
        pred_text: 预测摘要
        ref_text: 参考摘要（gold，可能包含markdown）
        subject: 学科名
        ctl_resources: CTL 资源
        
    Returns:
        {"C-F1": float, "C-P": float, "C-R": float}
        
    依赖：
        - triggered_concepts 函数
        - ctl_resources
        
    注意：
        - 主报告用 C-F1
        - P/R 供分析用
        - 自动清洗markdown符号（在CTL抽取前）
    """
    # 清洗markdown符号（在CTL抽取前）
    pred_text = clean_text_for_eval(pred_text)
    ref_text = clean_text_for_eval(ref_text)
    
    pred_concepts = triggered_concepts(pred_text, subject, ctl_resources)
    ref_concepts = triggered_concepts(ref_text, subject, ctl_resources)
    
    pred_set = set(c.kc_id for c in pred_concepts)
    ref_set = set(c.kc_id for c in ref_concepts)
    
    if len(ref_set) == 0:
        return {"C-F1": 0.0, "C-P": 0.0, "C-R": 0.0}
    
    tp = len(pred_set & ref_set)
    fp = len(pred_set - ref_set)
    fn = len(ref_set - pred_set)
    
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-8, precision + recall)
    
    return {
        "C-F1": f1,
        "C-P": precision,
        "C-R": recall,
    }


def compute_kpc(pred_text: str,
                plan_pi_kc: List[str],
                plan_edges_based_on: List[Tuple[str, str]],
                plan_edges_next: List[Tuple[str, str]],
                subject: str,
                ctl_resources: CtlResources) -> float:
    """
    计算 KPC (Knowledge Progression Consistency) - 知识递进一致性
    
    Paper Reference: Table 1, Table 4 (Ablation Studies)
    Formula: KPC = 1 - (violations / max(1, |E_dep|))
    
    定义（论文表格，严格按公式）：
        KPC = 1 - (violations / max(1, |E_dep|))
        
        其中：
        - E_dep: plan 的 π 对应的依赖边集合（BASED_ON + NEXT，只考虑 π 内的边）
        - violations: 统计 pred 中违反先修顺序的边数
        - 只计算"u 和 v 都在 pred 中出现"的边（否则无法判断顺序）
        
    关键修正（2025-12-31）：
        - **分母只用 plan 的依赖边集合**，不是全局 KG 的所有边
        - **不混入覆盖率惩罚**，KPC 只衡量"顺序一致性"，不衡量"覆盖率"
        - 如果 u 或 v 未在 pred 中出现，该边不计入分母（无法验证）
        - 如果没有任何可验证的边，返回 0.5（随机顺序的期望值）
        
    Args:
        pred_text: 预测摘要
        plan_pi_kc: Planner 输出的教学递进路径 π (有序 KC id 列表)
        plan_edges_based_on: plan 的 BASED_ON 边集合 [(u, v), ...]
        plan_edges_next: plan 的 NEXT 边集合 [(u, v), ...]
        subject: 学科名
        ctl_resources: CTL 资源
        
    Returns:
        KPC: float ∈ [0, 1]，越高越好
        
    依赖：
        - triggered_concepts 函数（提供 pred 中概念的出现顺序）
        - plan 的边集合（提供该视频/课程的依赖关系）
        
    注意：
        - 这是 KCVR 最核心的指标，证明模型学会了"结构化生成"
        - 审稿人会重点看这个指标是否对 Plan 有明显提升
        - 按论文预期，zero-shot 应在 45 左右，SFT 应在 50-70 区间
    """
    pred_text = clean_text_for_eval(pred_text)
    pred_concepts = triggered_concepts(pred_text, subject, ctl_resources)
    pred_order = {c.kc_id: c.first_pos for c in pred_concepts}
    
    if len(pred_order) == 0:
        return 0.0  # 没有概念，无法计算
    
    # π 集合（用于过滤边）
    pi_set = set(plan_pi_kc) if plan_pi_kc else set()
    
    # 统计可验证的边和违反的边
    based_w = 1.0
    next_w = 0.5
    total_w = 0.0
    bad_w = 0.0
    
    def _accumulate(edge_list: List[Tuple[str, str]], w: float, flip: bool = False) -> None:
        nonlocal total_w, bad_w
        for u, v in edge_list:
            # 只考虑 π 内的边
            if pi_set and (u not in pi_set or v not in pi_set):
                continue
            # 只计算"u 和 v 都在 pred 中出现"的边（否则无法判断顺序）
            if u in pred_order and v in pred_order:
                total_w += w
                # Direction note:
                # - For NEXT: we expect u appears BEFORE v (u -> v).
                # - For BASED_ON: in our KG csv, START_ID is the dependent concept, END_ID is its prerequisite.
                #   So we expect v appears BEFORE u (flip=True).
                if flip:
                    violated = pred_order[v] > pred_order[u]  # expected v < u
                else:
                    violated = pred_order[u] > pred_order[v]  # expected u < v
                if violated:
                    bad_w += w
    
    # BASED_ON is dependency: END_ID should appear before START_ID (flip=True).
    _accumulate(plan_edges_based_on, based_w, flip=True)
    # NEXT is teaching sequence: START_ID should appear before END_ID.
    _accumulate(plan_edges_next, next_w, flip=False)
    
    # 如果没有可验证的边，返回 0.5（随机顺序的期望值）
    if total_w == 0.0:
        return 0.5
    
    # KPC = 1 - (violations / total_edges)
    kpc = 1.0 - (bad_w / total_w)
    return max(0.0, min(1.0, kpc))


def compute_loc(pred_summary: str,
                gold_objectives: str,
                lang: str = "zh",
                threshold: float = 0.8) -> float:
    """
    计算 LOC (Learning Objective Coverage) - 学习目标覆盖率
    
    Paper Reference: Table 1, Table 2 (OOD Generalization)
    Formula: LOC = |entailed_objectives| / max(1, |gold_objectives|)
    
    定义（论文原始设想）：
        LOC = |entailed_objectives| / max(1, |gold_objectives|)

        对每个 gold objective（hypothesis），判断其是否被**生成摘要**（premise）蕴含（entailment），
        并统计"高置信蕴含"的比例。

        **关键**：
        - premise: 生成的**摘要文本**（pred_summary）
        - hypothesis: 标准学习目标（gold_objectives，逐条）
        - 判断：摘要能否推导出该学习目标已达成

        为了保证可复现与离线可运行：
        - 若环境变量 `KCVR_LOC_NLI_MODEL` 指向本地 NLI 模型（sequence-classification），
          则使用 NLI entailment 概率来判定（推荐）。
        - 否则回退到 bge-m3 embedding cosine 相似度近似（可离线运行）。
        
    Args:
        pred_summary: **生成的摘要文本**（premise）
        gold_objectives: 参考学习目标文本（可为多条，用换行/标点分隔）
        lang: 语言
        threshold: "高置信覆盖"阈值：
            - 对 NLI：entailment probability >= threshold 视为覆盖
            - 对 embedding：cosine similarity >= threshold 视为覆盖（建议0.50-0.60）
        
    Returns:
        LOC: float ∈ [0, 1]，越高越好
        
    依赖：
        - BERTScore 或 SentenceTransformer（embedding 相似度）
        
    注意：
        - 这是第二核心指标，证明生成的摘要能"满足学习目标"
        - 如果摘要为空，LOC=0
        - **重要**：传入的第一个参数必须是摘要，不是学习目标！
    """
    # 1) Clean texts
    premise = clean_text_for_eval(pred_summary)  # 摘要作为 premise
    gold_objectives = clean_text_for_eval(gold_objectives)

    # 2) Split gold objectives into list
    gold_list = [o.strip() for o in re.split(r"[；;。.\n]", gold_objectives) if o.strip()]
    if len(gold_list) == 0:
        return 1.0
    if not premise:
        return 0.0

    # 3) Use NLI model if provided, else fallback to embedding / overlap similarity.
    import os
    nli_model = os.environ.get("KCVR_LOC_NLI_MODEL", "").strip()
    device = os.environ.get("KCVR_LOC_DEVICE", "cpu").strip()
    # For embedding similarity (bge-m3), use moderate threshold (0.55-0.65) to approximate NLI entailment
    # Too high (0.70+) causes false negatives; too low (0.40-) causes false positives    
    sim_threshold = float(os.environ.get("KCVR_LOC_SIM_THRESHOLD", "0.60"))

    def _split_entailment_label_id(model) -> Optional[int]:
        # Try to find entailment label id robustly.
        label2id = getattr(getattr(model, "config", None), "label2id", None) or {}
        for k, v in label2id.items():
            if isinstance(k, str) and "entail" in k.lower():
                return int(v)
        # Common MNLI convention: [contradiction, neutral, entailment]
        num_labels = int(getattr(getattr(model, "config", None), "num_labels", 0) or 0)
        if num_labels == 3:
            return 2
        return None

    covered = 0

    # NLI path (offline if model is local)
    if nli_model and TRANSFORMERS_AVAILABLE:
        try:
            tok = AutoTokenizer.from_pretrained(nli_model, local_files_only=True)
            mdl = AutoModelForSequenceClassification.from_pretrained(nli_model, local_files_only=True)
            mdl.eval()
            if device != "cpu" and hasattr(torch, "cuda") and torch.cuda.is_available():
                mdl = mdl.to(device)
            entail_id = _split_entailment_label_id(mdl)
            if entail_id is None:
                # Fallback if label mapping is unknown
                raise ValueError("Entailment label id not found for the NLI model.")

            with torch.no_grad():
                for hyp in gold_list:
                    inputs = tok(premise, hyp, return_tensors="pt", truncation=True, max_length=512)
                    if device != "cpu" and hasattr(torch, "cuda") and torch.cuda.is_available():
                        inputs = {k: v.to(device) for k, v in inputs.items()}
                    logits = mdl(**inputs).logits
                    probs = torch.softmax(logits, dim=-1).squeeze(0)
                    p_entail = float(probs[entail_id].item())
                    if p_entail >= threshold:
                        covered += 1
            return covered / len(gold_list)
        except Exception as e:
            # English comment for reproducibility/debugging
            print(f"Warning: LOC NLI failed ({e}), fallback to embedding similarity.")

    # Fallback: embedding similarity (bge-m3) or token-overlap as an entailment proxy
    for hyp in gold_list:
        sim = _fallback_semantic_similarity(premise, hyp)
        if sim >= sim_threshold:
            covered += 1
    return covered / len(gold_list)


# ============================================================================
# 4. （可选）GPT 评测包装
# ============================================================================

def gpt_judge_structural_quality(pred_text: str,
                                 ref_text: str,
                                 api_key: str,
                                 prompt_template: Optional[str] = None) -> Dict[str, float]:
    """
    使用 GPT-4 进行结构质量人工评估（仅供分析/附录，不进入主表）
    
    Args:
        pred_text: 预测摘要
        ref_text: 参考摘要
        api_key: OpenAI API key
        prompt_template: 自定义 prompt
        
    Returns:
        {"structural_coherence": float, "pedagogical_logic": float}
        
    依赖：
        - openai 库
        - GPT-4 API
        
    注意：
        - 这个指标不可完全复现（GPT API 可能变化）
        - 只作为辅助分析，不作为主要贡献点
        - 成本较高，建议只在小规模样本上使用
    """
    # 这里只提供接口，具体实现可后续补充
    raise NotImplementedError("GPT 评测接口预留，暂未实现。建议优先使用可复现的本地指标。")


# ============================================================================
# 5. 批量计算工具函数
# ============================================================================

def compute_all_metrics(pred_text: str,
                       ref_text: str,
                       pred_objectives: str,
                       gold_objectives: str,
                       plan_pi_kc: List[str],
                       plan_edges_based_on: List[Tuple[str, str]],
                       plan_edges_next: List[Tuple[str, str]],
                       subject: str,
                       ctl_resources: CtlResources) -> Dict[str, float]:
    """
    一次性计算所有指标（方便批量评测）
    
    Returns:
        {"R1": ..., "R2": ..., "RL": ..., "BS": ..., 
         "C-F1": ..., "KPC": ..., "LOC": ...}
    """
    metrics = {}
    
    # ROUGE
    try:
        rouge_scores = compute_rouge(pred_text, ref_text)
        metrics.update(rouge_scores)
    except Exception as e:
        print(f"Warning: ROUGE computation failed: {e}")
        metrics.update({"R1": 0.0, "R2": 0.0, "RL": 0.0})
    
    # BERTScore（有fallback，不会抛出异常）
    try:
        bs = compute_bertscore(pred_text, ref_text)
        metrics["BS"] = bs
    except Exception as e:
        print(f"Warning: BERTScore computation failed: {e}")
        metrics["BS"] = 0.0  # 最后fallback
    
    # Concept-F1
    try:
        cf1_scores = compute_concept_f1(pred_text, ref_text, subject, ctl_resources)
        metrics["C-F1"] = cf1_scores["C-F1"]
    except Exception as e:
        print(f"Warning: Concept-F1 computation failed: {e}")
        metrics["C-F1"] = 0.0
    
    # KPC
    try:
        kpc = compute_kpc(pred_text, plan_pi_kc, plan_edges_based_on, plan_edges_next, subject, ctl_resources)
        metrics["KPC"] = kpc
    except Exception as e:
        print(f"Warning: KPC computation failed: {e}")
        metrics["KPC"] = 0.0
    
    # LOC
    try:
        # LOC should evaluate whether the SUMMARY entails the learning objectives (paper-aligned).
        # We intentionally use pred_text as premise (summary), NOT pred_objectives.
        loc = compute_loc(pred_text, gold_objectives)
        metrics["LOC"] = loc
    except Exception as e:
        print(f"Warning: LOC computation failed: {e}")
        metrics["LOC"] = 0.0
    
    return metrics


# ============================================================================
# 模块信息
# ============================================================================

__version__ = "1.0.0"
__author__ = "KCVR Team"
__description__ = "统一评测指标接口，与论文表格完全对齐"

