"""
单个智能体实现 - Single Agent
使用与 cot_agentv2.py 完全相同的推理流程
"""

import json
import os
import base64
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AgentOpinion:
    """智能体的观点"""
    agent_id: int
    epoch: int
    verdict: str  # 'buyer' or 'seller'
    reasoning: str


class SingleAgent:
    """
    单个智能体 - 使用与 cot_agentv2.py 完全相同的推理流程
    
    决策流程分为5个步骤：
    1. 理解案件文本
    2. 买方视角迭代分析（多轮）
    3. 卖方视角迭代分析（多轮）
    4. 深度分析
    5. 最终裁决（结合平均场和社会共识）
    """
    
    def __init__(self, agent_id: int, model, config: Dict, agent_profile: Optional[Dict] = None):
        """
        初始化智能体
        
        Args:
            agent_id: 智能体ID (0-16)
            model: 多模态模型实例
            config: 配置
            agent_profile: 智能体画像（可选）
        """
        self.agent_id = agent_id
        self.model = model
        self.config = config
        self.agent_profile = agent_profile or {}
        self.history_opinions = []  # 历史观点
        
        # CoT配置
        self.max_iterations_buyer = config.get('max_iterations_buyer', 3)
        self.max_iterations_seller = config.get('max_iterations_seller', 3)
        
        # 临时目录
        self.temp_frames_dir = Path(f'temp_frames/agent_{agent_id}')
        self.temp_frames_dir.mkdir(parents=True, exist_ok=True)
        self._temp_frame_counter = 0
        
    def run_in_thread(self, case_data: Dict, mean_field, 
                     social_consensus: Optional[str],
                     neighbor_opinions: Optional[List['AgentOpinion']] = None) -> AgentOpinion:
        """在线程中运行（同步调用模型）
        
        Args:
            case_data: 案件数据
            mean_field: 平均场（MeanField 对象）
            social_consensus: 社会共识文本
            neighbor_opinions: 邻居智能体的上一轮观点
            
        Returns:
            AgentOpinion: 智能体观点
        """
        return self._full_cot_reasoning(case_data, mean_field, social_consensus, neighbor_opinions)
    
    def _full_cot_reasoning(self, case_data: Dict, mean_field,
                            social_consensus: Optional[str],
                            neighbor_opinions: Optional[List['AgentOpinion']] = None) -> AgentOpinion:
        """
        完整的思维链推理流程（与 cot_agentv2.py 一致）
        """
        # 步骤1: 理解案件
        step1_output = self._step1_understand_case(case_data)
        
        # 步骤2: 买方视角迭代分析
        step2_output = self._step2_buyer_perspective(
            step1_output,
            case_data.get('buyer_evidence', []),
            case_data
        )
        
        # 步骤3: 卖方视角迭代分析
        step3_output = self._step3_seller_perspective(
            step1_output,
            case_data.get('seller_evidence', []),
            case_data
        )
        
        # 步骤4: 深度分析
        step4_output = self._step4_deep_analysis(step1_output, step2_output, step3_output)
        
        # 步骤5: 最终裁决（结合平均场、社会共识和邻居观点）
        step5_output = self._step5_final_verdict({
            'step1': step1_output,
            'step2': step2_output,
            'step3': step3_output,
            'step4': step4_output
        }, case_data, mean_field, social_consensus, neighbor_opinions)
        
        # 创建观点
        opinion = AgentOpinion(
            agent_id=self.agent_id,
            epoch=len(self.history_opinions),
            verdict=step5_output['verdict'].lower(),
            reasoning='; '.join(step5_output.get('reasoning', []))
        )
        
        self.history_opinions.append(opinion)
        return opinion
    
    # ==================== 5步思维链实现 ====================
    
    def _step1_understand_case(self, case_data: Dict) -> Dict:
        """步骤1: 理解案件文本"""
        buyer_desc = "\n".join(case_data.get('buyer_descriptions', [])) if case_data.get('buyer_descriptions') else "无"
        seller_desc = "\n".join(case_data.get('seller_descriptions', [])) if case_data.get('seller_descriptions') else "无"
        
        product_info = case_data.get('product_info', {})
        product_info_text = product_info.get('text', '无') if product_info else '无'
        
        prompt = f"""根据案件文本，理解买卖双方的诉求和纠纷原因。

案件信息：
- 案件编号：{case_data.get('id', 'N/A')}
- 商品：{case_data.get('product', 'N/A')}
- 争议点：{case_data.get('dispute', 'N/A')}
- 买家主张：{case_data.get('buyer_claim', 'N/A')}
- 卖家主张：{case_data.get('seller_claim', 'N/A')}

商品信息：
{product_info_text}

买家详细描述：
{buyer_desc}

卖家详细描述：
{seller_desc}

请分析：
1. 买家的核心诉求是什么？
2. 卖家的核心诉求是什么？
3. 双方争议的焦点是什么？

请以JSON格式输出：
{{
  "buyer_core_claim": "买家核心诉求",
  "seller_core_claim": "卖家核心诉求",
  "dispute_focus": "争议焦点"
}}
"""
        
        response = self.model.generate(prompt)
        return self._parse_json_response(response)
    
    def _step2_buyer_perspective(self, step1_output: Dict, buyer_evidence: List[Dict], case_data: Dict) -> List[Dict]:
        """步骤2: 买方视角迭代分析（多轮，两阶段）"""
        analyzed_evidence = []
        available_evidence_ids = [f"买家证据{i+1}" for i in range(len(buyer_evidence))]
        
        for iteration in range(self.max_iterations_buyer):
            # 阶段1: 选择证据
            selection_prompt = self._build_evidence_selection_prompt(
                step1_output, buyer_evidence, analyzed_evidence, available_evidence_ids, "买家"
            )
            
            if selection_prompt is None:
                break
            
            selection_response = self.model.generate(selection_prompt)
            selection_result = self._parse_json_response(selection_response)
            
            selected_id = selection_result.get('selected_evidence_id')
            if not selected_id or selected_id not in available_evidence_ids:
                break
            
            evidence_idx = int(selected_id.replace('买家证据', '')) - 1
            selected_evidence = buyer_evidence[evidence_idx]
            
            # 阶段2: 分析视觉内容
            images = selected_evidence.get('image_paths', []) or []
            videos = selected_evidence.get('video_paths', []) or []
            
            # 获取上一轮的关键媒体
            prev_crops = []
            if analyzed_evidence:
                last = analyzed_evidence[-1]
                prev_crops = last.get('useful_media_paths', [])
            
            prev_product_desc = case_data.get('product_info', {}).get('text', '') if case_data.get('product_info') else ''
            
            analysis_prompt = self._build_visual_analysis_prompt(
                step1_output, selected_evidence, selected_id, "买家", case_data,
                prev_crops, prev_product_desc
            )
            
            analysis_response = self.model.generate(analysis_prompt, images=images, videos=videos)
            analysis_result = self._parse_json_response(analysis_response)
            
            # 重建关键媒体路径
            useful_media_paths = self._extract_useful_media_paths(
                analysis_result.get('visual_findings', []),
                images, videos
            )
            
            result = {
                'iteration': iteration + 1,
                'selected_evidence_id': selected_id,
                'selection_reason': selection_result.get('reason', ''),
                'evidence_data': selected_evidence,
                'useful_media_paths': useful_media_paths,
                **analysis_result
            }
            
            analyzed_evidence.append(result)
            available_evidence_ids.remove(selected_id)
            
            if result.get('is_sufficient', False) or not available_evidence_ids:
                break
        
        return analyzed_evidence
    
    def _step3_seller_perspective(self, step1_output: Dict, seller_evidence: List[Dict], case_data: Dict) -> List[Dict]:
        """步骤3: 卖方视角迭代分析（多轮，两阶段）"""
        analyzed_evidence = []
        available_evidence_ids = [f"卖家证据{i+1}" for i in range(len(seller_evidence))]
        
        for iteration in range(self.max_iterations_seller):
            # 阶段1: 选择证据
            selection_prompt = self._build_evidence_selection_prompt(
                step1_output, seller_evidence, analyzed_evidence, available_evidence_ids, "卖家"
            )
            
            if selection_prompt is None:
                break
            
            selection_response = self.model.generate(selection_prompt)
            selection_result = self._parse_json_response(selection_response)
            
            selected_id = selection_result.get('selected_evidence_id')
            if not selected_id or selected_id not in available_evidence_ids:
                break
            
            evidence_idx = int(selected_id.replace('卖家证据', '')) - 1
            selected_evidence = seller_evidence[evidence_idx]
            
            # 阶段2: 分析视觉内容
            images = selected_evidence.get('image_paths', []) or []
            videos = selected_evidence.get('video_paths', []) or []
            
            prev_crops = []
            if analyzed_evidence:
                last = analyzed_evidence[-1]
                prev_crops = last.get('useful_media_paths', [])
            
            prev_product_desc = case_data.get('product_info', {}).get('text', '') if case_data.get('product_info') else ''
            
            analysis_prompt = self._build_visual_analysis_prompt(
                step1_output, selected_evidence, selected_id, "卖家", case_data,
                prev_crops, prev_product_desc
            )
            
            analysis_response = self.model.generate(analysis_prompt, images=images, videos=videos)
            analysis_result = self._parse_json_response(analysis_response)
            
            useful_media_paths = self._extract_useful_media_paths(
                analysis_result.get('visual_findings', []),
                images, videos
            )
            
            result = {
                'iteration': iteration + 1,
                'selected_evidence_id': selected_id,
                'selection_reason': selection_result.get('reason', ''),
                'evidence_data': selected_evidence,
                'useful_media_paths': useful_media_paths,
                **analysis_result
            }
            
            analyzed_evidence.append(result)
            available_evidence_ids.remove(selected_id)
            
            if result.get('is_sufficient', False) or not available_evidence_ids:
                break
        
        return analyzed_evidence
    
    def _step4_deep_analysis(self, step1_output: Dict, step2_output: List[Dict], step3_output: List[Dict]) -> Dict:
        """步骤4: 深度分析"""
        # 收集关键媒体路径
        buyer_media_paths = []
        for analysis in step2_output:
            buyer_media_paths.extend(analysis.get('useful_media_paths', []))
        
        seller_media_paths = []
        for analysis in step3_output:
            seller_media_paths.extend(analysis.get('useful_media_paths', []))
        
        # 转换为data URL
        def path_to_data_url(path):
            try:
                ext = os.path.splitext(path)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    mime_type = 'image/jpeg'
                elif ext == '.png':
                    mime_type = 'image/png'
                else:
                    mime_type = 'image/jpeg'
                
                with open(path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                return f"data:{mime_type};base64,{encoded}"
            except:
                return None
        
        buyer_images = [path_to_data_url(p) for p in buyer_media_paths if p]
        seller_images = [path_to_data_url(p) for p in seller_media_paths if p]
        buyer_images = [img for img in buyer_images if img]
        seller_images = [img for img in seller_images if img]
        
        prompt = f"""基于双方提供的关键视觉证据，进行深度逻辑分析。

案件理解：
{json.dumps(step1_output, ensure_ascii=False, indent=2)}

买方提供的关键媒体路径：
{json.dumps(buyer_media_paths, ensure_ascii=False, indent=2)}

卖方提供的关键媒体路径：
{json.dumps(seller_media_paths, ensure_ascii=False, indent=2)}

【说明】
- 我已经将买家的 {len(buyer_images)} 个媒体和卖家的 {len(seller_images)} 个媒体传入。
- 请将所有媒体视为一个列表，买家媒体在前，卖家媒体在后。

【分析任务】请深入分析以下内容：

1. **纠纷根源分析**：
   - 这个纠纷的根本原因是什么？
   - 是商品质量问题、描述不符、服务问题还是其他？

2. **买方的纠纷立场**：
   - 买方为什么不满？具体诉求是什么？
   - 买方提供的证据（文本+视觉）支持其诉求吗？
   - 买方的主张有什么优势和弱点？

3. **卖方的纠纷立场**：
   - 卖方的辩解理由是什么？
   - 卖方提供的证据（文本+视觉）支持其辩解吗？
   - 卖方的主张有什么优势和弱点？

4. **冲突焦点**：
   - 双方最核心的分歧点在哪里？
   - 双方的证据是否存在矛盾？
   - 从视觉证据中能看出什么关键信息？

请以JSON格式输出：
{{
  "dispute_root_cause": "纠纷的根本原因",
  "buyer_position": {{
    "main_complaint": "买方的主要不满",
    "demands": "具体诉求",
    "key_evidence": ["关键证据1", "关键证据2"],
    "visual_support": "视觉证据是否支持买方",
    "strengths": ["买方立场的优势1", "优势2"],
    "weaknesses": ["买方立场的弱点1", "弱点2"]
  }},
  "seller_position": {{
    "main_defense": "卖方的主要辩解",
    "counter_arguments": "反驳论点",
    "key_evidence": ["关键证据1", "关键证据2"],
    "visual_support": "视觉证据是否支持卖方",
    "strengths": ["卖方立场的优势1", "优势2"],
    "weaknesses": ["卖方立场的弱点1", "弱点2"]
  }},
  "conflict_focus": {{
    "core_disagreement": "核心分歧点",
    "evidence_contradictions": ["证据矛盾1", "矛盾2"],
    "visual_evidence_insights": "从视觉证据中发现的关键信息",
    "critical_facts": ["关键事实1", "事实2"]
  }}
}}
"""
        
        all_images = buyer_images + seller_images
        response = self.model.generate(prompt, images=all_images)
        return self._parse_json_response(response)
    
    def _step5_final_verdict(self, all_previous_outputs: Dict, case_data: Dict,
                             mean_field, social_consensus: Optional[str],
                             neighbor_opinions: Optional[List['AgentOpinion']] = None) -> Dict:
        """步骤5: 最终裁决（结合平均场、社会共识和邻居观点）"""

        buyer_analyses = all_previous_outputs.get('step2', [])
        seller_analyses = all_previous_outputs.get('step3', []) 
        # 提取买家证据分析中所有的visual_findings
        buyer_visual_findings = []  
        for analysis in buyer_analyses:
            findings = analysis.get('visual_findings', [])
            buyer_visual_findings.extend(findings)
        # 提取卖家证据分析中所有的visual_findings
        seller_visual_findings = []
        for analysis in seller_analyses:
            findings = analysis.get('visual_findings', [])
            seller_visual_findings.extend(findings)
        
        prompt_parts = [
            f"你是智能体#{self.agent_id}，现在要对二手电商交易纠纷做出最终裁决。\n"
        ]
        
        # 添加社会共识
        if social_consensus:
            prompt_parts.append(f"【社会共识】\n{social_consensus}\n")
        
        # 添加平均场
        if mean_field:
            prompt_parts.append(
                f"【讨论氛围】\n"
                f"- 支持买家: {mean_field.buyer_support_ratio:.1%}\n"
                f"- 支持卖家: {mean_field.seller_support_ratio:.1%}\n"
                f"- 共识度: {mean_field.consensus_level:.1%}\n"
                )
        
        # 添加邻居观点（基于社交网络）
        if neighbor_opinions and len(neighbor_opinions) > 0:
            prompt_parts.append(f"\n【你关注的邻居智能体的上一轮裁决】\n")
            for op in neighbor_opinions:
                reasoning_preview = op.reasoning[:150] if op.reasoning else "无理由"
                prompt_parts.append(
                    f"- 智能体#{op.agent_id}: 支持 {op.verdict.upper()}, "
                    # f"得分[买{op.buyer_score}:卖{op.seller_score}], "
                    f"理由摘要: {reasoning_preview}...\n"
                )
        
        prompt_parts.append(f"""
买方陈述：
{json.dumps(case_data.get('buyer_descriptions', ''), ensure_ascii=False, indent=2)}

卖方陈述：
{json.dumps(case_data.get('seller_descriptions', ''), ensure_ascii=False, indent=2)}

买方证据分析：
{buyer_visual_findings}

卖方证据分析：
{seller_visual_findings}

深度分析：
{json.dumps(all_previous_outputs['step4'], ensure_ascii=False, indent=2)}

【判断规则】

- 只有买家在收到商品后，商品严重不符合卖家描述，或存在严重质量问题、拍a发b、或卖家刻意隐瞒实情等类似的情况，买家证据确凿，可以退货退款。\n
- 若商品符合卖家的描述，且卖家已经履行告知买家的义务，没有刻意隐瞒瑕疵及质量问题，则非特殊情况买家不能退货退款。
- 相比于商品展示图，聊天记录的商品描述、或者商品质检报告是判断商品状态的更为重要依据。
- 二手商品存在一定瑕疵或使用痕迹属于正常现象，除商品存在重大质量问题，或瑕疵及使用痕迹明显但卖家并未告知，否则几乎全新等商品描述不构成描述不符的问题
- 如果交易前，卖家已经展示商品信息，聊天记录中提供商品视觉信息，则证明买家下单时已经认可和了解商品及其描述，收到货后再以相关理由申请退货，非必要情况应该驳回买家退款申请。\n
- 买家因未仔细阅读商品展示图、聊天记录导致的事后退货诉求（无论商品描述详细与否），表示买家收到的商品与预期存在严重偏差，非必要情况应该驳回买家诉求。\n
- 仔细检查买卖双方证据和辩驳的合理性，判断买卖双方是否从视频图片中虚构了证据言论。全面考量证据，兼顾买卖双方可能的举证与过失。\n
- 买卖双方的纠纷讨论应该建立在卖方发货和买方收货的状态。买方应该保留拆开商品前的商品状态，拆开快递后，有严重痕迹 或 使用购买商品后的视觉证据需要审视合理性。


【判断要求】
- 综合考虑所有信息、平均场、社会共识、邻居观点
- 给出独立判断（不要盲目跟随邻居）
- 为买卖双方打分（总分17分）

请以JSON格式输出：
{{
  "verdict": "buyer/seller",
  "votes": {{
    "buyer": x,
    "seller": y
  }},
  "reasoning": [
    "理由1",
    "理由2",
    "理由3"
  ]
}}
""")
        
        prompt = "".join(prompt_parts)
        response = self.model.generate(prompt)
        return self._parse_json_response(response)
    
    # ==================== 辅助方法 ====================
    
    def _build_evidence_selection_prompt(self, step1_output: Dict, evidence_list: List[Dict],
                                        analyzed_evidence: List[Dict], available_ids: List[str],
                                        perspective: str) -> Optional[str]:
        """构建证据选择prompt"""
        evidence_texts = []
        for i, ev in enumerate(evidence_list, 1):
            ev_id = f"{perspective}证据{i}"
            if ev_id in available_ids:
                num_images = len(ev.get('image_paths', []) or [])
                num_videos = len(ev.get('video_paths', []) or [])
                
                if num_images > 0 or num_videos > 0:
                    text = ev.get('text', '无文本描述')
                    visual_info = []
                    if num_images > 0:
                        visual_info.append(f"{num_images}张图片")
                    if num_videos > 0:
                        visual_info.append(f"{num_videos}个视频")
                    visual_desc = "、".join(visual_info)
                    evidence_texts.append(f"{ev_id}: {text[:200]}... [包含: {visual_desc}]")
        
        if not evidence_texts:
            return None
        
        analyzed_summary = []
        for analyzed in analyzed_evidence:
            ev_id = analyzed.get('selected_evidence_id', '未知')
            summary = analyzed.get('evidence_summary', '无摘要')
            analyzed_summary.append(f"  - {ev_id}: {summary[:100]}...")
        
        analyzed_text = "\n".join(analyzed_summary) if analyzed_summary else "  （尚未分析任何证据）"
        
        prompt = f"""你正在从【{perspective}】视角分析案件。现在需要根据证据的文本描述，选择一个最值得查看视觉内容的证据。

案件理解：
{json.dumps(step1_output, ensure_ascii=False, indent=2)}

已分析过的证据：
{analyzed_text}

可用证据的文本描述：
{chr(10).join(evidence_texts)}

请根据文本描述和视觉内容类型，选择一个最可能包含关键视觉信息的证据进行深入分析。

请以JSON格式输出：
{{
  "selected_evidence_id": "{perspective}证据X",
  "reason": "选择该证据的理由"
}}
"""
        return prompt
    
    def _build_visual_analysis_prompt(self, step1_output: Dict, selected_evidence: Dict,
                                     evidence_id: str, perspective: str, case_data: Dict,
                                     previous_crops: List[str], previous_product_desc: str) -> str:
        """构建视觉分析prompt"""
        target = "买家" if perspective == "买家" else "卖家"
        
        product_info = case_data.get('product_info', {})
        product_info_text = product_info.get('text', '无') if product_info else '无'
        
        image_paths = selected_evidence.get('image_paths', []) or []
        video_paths = selected_evidence.get('video_paths', []) or []
        
        visual_info = []
        if len(image_paths) > 0:
            visual_info.append(f"{len(image_paths)}张图片")
        if len(video_paths) > 0:
            visual_info.append(f"{len(video_paths)}个视频")
        visual_desc = "、".join(visual_info)
        
        prompt = f"""你正在从【{perspective}】视角分析证据的视觉内容。

案件理解：
{json.dumps(step1_output, ensure_ascii=False, indent=2)}

商品信息：
{product_info_text}

当前分析的证据：{evidence_id}
证据文本描述：{selected_evidence.get('text', '无')}
视觉内容：{visual_desc}

现在请分析这些视觉内容，找出对【{target}】有利的证据：
1. 仔细观察图片/视频中的关键细节
2. 返回包含关键信息的图片或视频帧的路径
3. 描述该媒体为什么对{target}有利
4. 评估该证据的支持力度

请以JSON格式输出：
{{
  "visual_findings": [
    {{
      "media_type": "image/video",
      "media_index": 0,
      "timestamp": "00:05",
      "description": "该媒体的详细描述",
      "benefit_analysis": "为什么这对{target}有利",
      "importance": "高/中/低"
    }}
  ],
  "evidence_summary": "该证据的整体评估",
  "support_strength": "强/中/弱",
  "is_sufficient": true/false,
  "sufficiency_reason": "当前证据链是否充分的判断理由"
}}
"""
        return prompt
    
    def _extract_useful_media_paths(self, visual_findings: List[Dict], images: List[str], videos: List[str]) -> List[str]:
        """从visual_findings重建关键媒体路径"""
        useful_media_paths = []
        for finding in visual_findings:
            media_type = finding.get('media_type')
            media_index = finding.get('media_index')
            timestamp = finding.get('timestamp')
            
            if media_type is not None and media_index is not None:
                if media_type == 'image':
                    if media_index < len(images):
                        useful_media_paths.append(images[media_index])
                elif media_type == 'video':
                    if media_index < len(videos) and timestamp and timestamp != "0":
                        frame_path = self._extract_video_frame(videos[media_index], timestamp)
                        if frame_path:
                            useful_media_paths.append(frame_path)
                    elif media_index < len(videos):
                        useful_media_paths.append(videos[media_index])
        
        return sorted(list(set(useful_media_paths)))
    
    def _extract_video_frame(self, video_path: str, timestamp: str) -> Optional[str]:
        """从视频中提取指定时间戳的帧"""
        try:
            import cv2
            
            parts = timestamp.split(':')
            if len(parts) != 2:
                return None
            
            minutes = int(parts[0])
            seconds = int(parts[1])
            time_in_seconds = minutes * 60 + seconds
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                fps = 30
            
            frame_number = int(time_in_seconds * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return None
            
            self._temp_frame_counter += 1
            frame_filename = self.temp_frames_dir / f"frame_{self._temp_frame_counter}.jpg"
            cv2.imwrite(str(frame_filename), frame)
            
            return str(frame_filename)
        except Exception as e:
            return None
    
    def _parse_json_response(self, response: str) -> Dict:
        """解析JSON格式的响应"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return {
                "error": "JSON parsing failed",
                "raw_response": response[:500]
            }

