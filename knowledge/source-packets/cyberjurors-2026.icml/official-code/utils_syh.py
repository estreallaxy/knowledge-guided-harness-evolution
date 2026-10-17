"""
工具函数模块
包含数据加载、格式转换、配置加载等通用功能
"""

import json
import yaml
import os
from typing import Dict, List, Optional
from pathlib import Path


def load_real_cases(dataset_path: str, limit: Optional[int] = None) -> List[Dict]:
    """
    加载真实案件数据
    
    Args:
        dataset_path: 数据集路径
        limit: 限制加载的案件数量，None表示加载全部
    
    Returns:
        案件列表
    """
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if limit:
            data = data[:limit]
        
        print(f"✅ 成功加载 {len(data)} 个真实案件")
        return data
    except Exception as e:
        print(f"❌ 加载数据集失败: {e}")
        return []


def parse_case_to_standard_format(raw_case: Dict) -> Dict:
    """
    将 summary_old.json 的案件格式转换为标准格式
    
    Args:
        raw_case: 原始案件数据
    
    Returns:
        标准格式的案件数据
    """
    case_id = f"CASE_{raw_case['id']:06d}"
    
    # 从 title 和 evidences 中提取商品信息
    title = raw_case.get('title', '')
    product = title.split('是否')[0] if '是否' in title else '商品'  # 商品信息
    
    # 提取争议点
    dispute = raw_case.get('title', '').replace('是否存在', '').replace('的情况？期待你来揭示真相！', '')
    
    # 买卖双方主张
    buyer_claim = raw_case.get('buyer_claim', '')
    seller_claim = raw_case.get('seller_claim', '')
    
    # 提取证据和案例文本描述
    buyer_evidence = []
    seller_evidence = []
    buyer_descriptions = []  # 买家的详细文本描述
    seller_descriptions = []  # 卖家的详细文本描述
    product_info = None  # 商品信息（第一条证据）
    
    evidences = raw_case.get('case_details', {}).get('evidences', [])
    for idx, ev in enumerate(evidences):
        identity = ev.get('identity', '')
        content = ev.get('content', {})
        text = content.get('text', '')
        
        evidence_item = {
            "text": text,
            "image_paths": content.get('image_paths', []),
            "video_paths": content.get('video_paths', [])
        }
        
        # 第一条证据通常是商品信息
        if idx == 0 and identity == '买家':
            product_info = evidence_item
        
        if identity == '买家':
            buyer_evidence.append(evidence_item)
            if text:  # 收集买家的文本描述
                buyer_descriptions.append(text)
        elif identity == '卖家':
            seller_evidence.append(evidence_item)
            if text:  # 收集卖家的文本描述
                seller_descriptions.append(text)
    
    # 裁决结果（ground truth）
    whowins = raw_case.get('whowins', -1)  # 0=买家, 1=卖家
    court_support = raw_case.get('court_support', -1)  # 0=买家, 1=卖家
    
    # 评审意见
    reviewer4buyer = raw_case.get('reviewer4buyer_views', [])
    reviewer4seller = raw_case.get('reviewer4seller_views', [])
    
    return {
        "case_id": case_id,
        "original_id": raw_case['id'],
        "title": title,
        "product": product,
        "dispute": dispute,
        "buyer_claim": buyer_claim,
        "seller_claim": seller_claim,
        "buyer_evidence": buyer_evidence,
        "seller_evidence": seller_evidence,
        "buyer_descriptions": buyer_descriptions,
        "seller_descriptions": seller_descriptions,
        "product_info": product_info,
        "ground_truth": {
            "whowins": whowins,  # 用户投票结果
            "court_support": court_support,  # 法庭裁决
            "votes": raw_case.get('votes', []),  # [买家票数, 卖家票数]
            "reviewer4buyer_views": reviewer4buyer,
            "reviewer4seller_views": reviewer4seller
        }
    }


def load_config(config_path: str = "./court_models_config.yaml") -> Optional[Dict]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        配置字典，失败返回None
    """
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return None


def save_results(results: Dict, output_path: str):
    """
    保存结果到JSON文件
    
    Args:
        results: 结果字典
        output_path: 输出文件路径
    """
    try:
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 结果已保存到: {output_path}")
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")


def load_config(config_path: str = "./court_models_config.yaml") -> Optional[Dict]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        配置字典，如果加载失败返回None
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 如果配置文件中有API Key，设置到环境变量
        if 'api' in config and 'yunwu' in config['api']:
            api_key = config['api']['yunwu'].get('api_key')
            if api_key and not os.getenv('YUNWU_API_KEY'):
                os.environ['YUNWU_API_KEY'] = api_key
                print(f"✅ 从配置文件加载云雾API Key")
        
        return config
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None


def calculate_diversity_metrics(results: List[Dict]) -> Dict:
    """
    计算决策多样性指标
    
    Args:
        results: 多个智能体的决策结果列表
    
    Returns:
        多样性指标字典
    """
    if not results:
        return {}
    
    # 提取裁决
    verdicts = []
    responsibilities = []
    confidences = []
    
    for result in results:
        summary = result.get('summary', {})
        verdict = summary.get('verdict')
        ratio = summary.get('responsibility_ratio', {})
        conf = summary.get('confidence', 0) or 0
        
        if verdict:
            verdicts.append(verdict)
        if ratio and 'seller' in ratio:
            responsibilities.append(ratio['seller'])
        confidences.append(conf)
    
    # 计算指标
    metrics = {}
    
    # 裁决统计
    if verdicts:
        verdict_counts = {}
        for v in verdicts:
            verdict_counts[v] = verdict_counts.get(v, 0) + 1
        metrics['verdict_distribution'] = verdict_counts
        
        # 共识率
        most_common = max(verdict_counts, key=verdict_counts.get)
        consensus_rate = verdict_counts[most_common] / len(verdicts)
        metrics['consensus_rate'] = consensus_rate
        metrics['majority_verdict'] = most_common
    
    # 责任比例统计
    if responsibilities:
        import statistics
        metrics['responsibility'] = {
            'mean': statistics.mean(responsibilities),
            'min': min(responsibilities),
            'max': max(responsibilities),
            'stdev': statistics.stdev(responsibilities) if len(responsibilities) > 1 else 0
        }
    
    # 置信度统计
    if confidences:
        import statistics
        metrics['confidence'] = {
            'mean': statistics.mean(confidences),
            'min': min(confidences),
            'max': max(confidences)
        }
    
    return metrics

