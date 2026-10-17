"""
多智能体讨论系统 - 使用多线程并行
Multi-Agent Debate System with Threading

功能：
1. 17个智能体并行推理和讨论
2. 维护平均场（Mean Field）影响决策
3. 结合社会共识库
4. 多轮讨论后投票决定最终裁决
"""

import json
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import numpy as np

from Social_Consensus import retrieve_consensus_for_case
from utils.multimodal_models import YunwuModel
from utils.network import create_graph
from single_agent import SingleAgent, AgentOpinion
import utils.prompt as prompt


@dataclass
class MeanField:
    """平均场状态"""
    epoch: int
    buyer_support_ratio: float  # 支持买家的比例
    seller_support_ratio: float  # 支持卖家的比例
    consensus_level: float  # 共识程度 0-1 (投票多的一方占总人数的比例)
    mf_text: str  # 平均场文本总结
    
    def to_dict(self):
        return asdict(self)


class MultiAgentDebateSystem:
    """多智能体讨论系统"""
    
    def __init__(self, config: Dict):
        """
        初始化讨论系统
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.num_agents = config.get('num_agents', 17)
        self.max_epochs = config.get('max_epochs', 3)
        self.max_workers = config.get('num_agents', 17)  # 线程池大小
        
        # 平均场生成模型（使用同步模型）
        self.summary_model = YunwuModel(
            model_name=config.get('model_name', 'gemini-2.5-flash-lite-nothinking'),
            api_key=config.get('api_key', config.get('api_key')),
            base_url=config.get('base_url', config.get('base_url')),
            max_tokens=config.get('max_tokens', 2048),
            temperature=config.get('temperature', 0.7)
        )
        
        # ==================== 社交网络配置（每个案例动态生成）====================
        self.use_social_network = config.get('use_social_network', True)
        self.following_network = {}  # 将在deliberate中为每个案例动态生成
        self.social_network_dir = Path(config.get('output_dir', './results/multi_agent_debate')).parent / 'social_networks'
        if self.use_social_network:
            self.social_network_dir.mkdir(parents=True, exist_ok=True)
        
        # ==================== 配置模型（支持异构模型）====================
        self.agent_model_configs = {}
        
        # 检查是否配置了异构模型
        if config.get('agent_diff_model', False):
            print(f"🎨 使用异构模型配置 (每个智能体使用不同模型)")
            for i in range(self.num_agents):
                if i in config['agent_models']:
                    agent_name = config['agent_models'][i]
                    self.agent_model_configs[i] = {
                        'model_name': agent_name,
                        'api_key': config.get('api_key'),
                        'base_url': config.get('base_url'),
                        'max_tokens': config.get('max_tokens', 2048),
                        'temperature': config.get('temperature', 0.7)
                    }
                    print(f"  - 智能体 #{i}: {agent_name}")

        else:
            print(f"🎨 使用统一模型配置: {config.get('model_name', 'gemini-2.5-flash-lite-nothinking')}")
            # 所有智能体使用相同配置
            base_config = {
                'model_name': config.get('model_name', 'gemini-2.5-flash-lite-nothinking'),
                'api_key': config.get('api_key'),
                'base_url': config.get('base_url'),
                'max_tokens': config.get('max_tokens', 2048),
                'temperature': config.get('temperature', 0.7)
            }
            for i in range(self.num_agents):
                self.agent_model_configs[i] = base_config.copy()
        
        # ==================== 创建智能体并预先初始化模型（性能优化）====================
        self.agents = []
        self.agent_models = {}  # 预先创建的模型实例，可复用
        
        for i in range(self.num_agents):
            # 为每个智能体创建专属的模型实例
            model = YunwuModel(**self.agent_model_configs[i])
            self.agent_models[i] = model
            
            # 创建智能体并绑定模型
            agent = SingleAgent(i, model, config)
            self.agents.append(agent)
        
        # 平均场历史
        self.mean_field_history = []
        
        # 实验名称（用于区分不同实验）
        self.experiment_name = config.get('experiment_name', 'default')
        
        # 输出目录（包含实验名子目录）
        base_output_dir = Path(config.get('output_dir', './results/multi_agent_debate'))
        self.output_dir = base_output_dir / self.experiment_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Token 日志目录（每个实验一个子目录）
        base_token_log_dir = base_output_dir.parent / 'token_logs'
        self.token_log_dir = base_token_log_dir / self.experiment_name
        self.token_log_dir.mkdir(parents=True, exist_ok=True)
        
        # print(f"📁 实验名称: {self.experiment_name}")
        # print(f"📁 结果目录: {self.output_dir}")
        # print(f"📁 Token日志: {self.token_log_dir}")
        
        # print(f"✅ 多智能体讨论系统初始化完成")
        # print(f"  - 智能体数量: {self.num_agents}")
        # print(f"  - 最大讨论轮次: {self.max_epochs}")
        # print(f"  - 线程池大小: {self.max_workers}")
        if self.use_social_network:
            avg_following = np.mean([len(v) for v in self.following_network.values()])
            # print(f"  - 社交网络: 启用 (平均关注 {avg_following:.1f} 个邻居)")
    
    def _generate_social_network(self, seed: Optional[int] = None) -> Dict[str, List[int]]:
        """生成随机社交网络（使用 utils/network.py 的方法）
        
        Args:
            seed: 随机种子，用于生成确定性的网络
        """
        # 临时设置随机种子以生成特定的网络
        if seed is not None:
            old_state = np.random.get_state()
            np.random.seed(seed)
        
        # 使用与 save_following_network 完全相同的逻辑
        network = create_graph(num_nodes=self.num_agents, num_edges=3, min_follow_num=1, max_follow_num=3)
        following = {str(node): list(network.successors(node)) for node in network.nodes()}
        
        # 恢复随机状态
        if seed is not None:
            np.random.set_state(old_state)
        
        return following
    
    def deliberate(self, case_data: Dict) -> Dict:
        """
        对一个案件进行多轮讨论
        
        Args:
            case_data: 案件数据
            
        Returns:
            讨论结果
        """
        case_id = case_data.get('case_id', 'unknown')
        
        # ==================== 为当前案例配置 token 日志（性能优化）====================
        # 为该案例创建单独的 token 日志文件
        case_token_log_path = self.token_log_dir / f"token_usage_{case_id}.json"
        
        # 配置所有智能体的模型：禁用自动写文件，改为累积到内存
        for agent in self.agents:
            agent.model.token_log_path = case_token_log_path
            agent.model.auto_write_log = False  # 禁用自动写文件
            agent.model.clear_token_buffer()  # 清空之前的缓冲区
        
        # 配置平均场生成模型
        self.summary_model.token_log_path = case_token_log_path
        self.summary_model.auto_write_log = False
        self.summary_model.clear_token_buffer()
        
        # ==================== 为当前案例生成独特的社交网络 ====================
        if self.use_social_network:
            # 使用case_id作为随机种子，确保每个案例有不同但可复现的社交网络
            import hashlib
            seed = int(hashlib.md5(str(case_id).encode()).hexdigest()[:8], 16) % (2**32)
            self.following_network = self._generate_social_network(seed=seed)
            
            # 保存该案例的社交网络
            network_file = self.social_network_dir / f"network_{case_id}.json"
            with open(network_file, 'w', encoding='utf-8') as f:
                json.dump(self.following_network, f, indent=2, ensure_ascii=False)
        
        # 重置平均场历史
        self.mean_field_history = []
        
        print(f"\n{'='*70}")
        print(f"🏛️  案例 {case_id} 开始讨论 ({self.num_agents} 个智能体 × {self.max_epochs} 轮)")
        print(f"{'='*70}")
        
        
        
        # 多轮讨论
        all_epoch_opinions = []
        
        for epoch in range(self.max_epochs):
            print(f"\n📢 第 {epoch + 1}/{self.max_epochs} 轮讨论")
            print(f"{'─'*70}")

            # 根据轮次决定是否使用社会共识
            if self.config.get('use_social_consensus', False) and epoch > 0:
                social_consensus = self._retrieve_social_consensus(case_data)
                if social_consensus:
                    print(f"  🔗 第 {epoch + 1} 轮已引入社会共识")
            else:
                social_consensus = None
            
            # 获取当前平均场
            if self.config.get('use_mean_field', False):
                current_mean_field = self.mean_field_history[-1] if len(self.mean_field_history) > 0 else None
            else:
                current_mean_field = None

            # 获取上一轮的观点（用于智能体参考邻居裁决）
            previous_opinions = all_epoch_opinions[-1] if all_epoch_opinions else []

            # 并行推理
            epoch_opinions = self._parallel_reasoning(
                case_data, 
                current_mean_field, 
                social_consensus,
                previous_opinions,
                epoch  # 传递当前轮次
            )
            
            all_epoch_opinions.append(epoch_opinions)
            
            # 更新平均场
            if self.config.get('use_mean_field', False):
                mean_field = self._compute_mean_field(epoch, epoch_opinions, case_data)
                self.mean_field_history.append(mean_field)
                
                # 显示讨论状态
                self._print_epoch_summary(epoch, mean_field, epoch_opinions)
                
                # # 检查是否达成共识（共识度 > 阈值 表示超过一定比例的智能体支持同一方）
                early_stop_threshold = self.config.get('early_stop_consensus', 0.9)
                if mean_field.consensus_level > early_stop_threshold:
                    print(f"\n✅ 已达成高度共识！")
                    print(f"   投票: 买家 {int(mean_field.buyer_support_ratio * len(epoch_opinions))} vs 卖家 {int(mean_field.seller_support_ratio * len(epoch_opinions))}")
                    print(f"   提前结束讨论 (第 {epoch + 1}/{self.max_epochs} 轮)")
                    break
            
            # ==================== 每轮结束后批量写入 token 日志（性能优化）====================
            self._flush_all_token_logs(epoch)
        
        # 最终投票
        final_verdict = self._final_vote(all_epoch_opinions[-1])
        
        # ==================== 案例结束后最后一次批量写入 token 日志 ====================
        self._flush_all_token_logs(epoch=-1)  # epoch=-1 表示最终写入
        
        # 保存结果（根据配置决定是保存所有轮次还是只保存最后一轮）
        result = self._build_result(case_data, final_verdict, all_epoch_opinions)

        result['ground_truth'] = case_data['ground_truth']
        self._save_result(case_id, result)
        
        print(f"\n{'='*70}")
        print(f"✅ 案件 {case_id} 讨论完成")
        print(f"   投票结果: 买家 {final_verdict['buyer_votes']} vs 卖家 {final_verdict['seller_votes']}")
        print(f"   最终裁决: {final_verdict['verdict'].upper()} vs {case_data['ground_truth']['court_support']}")
        print(f"{'='*70}\n")
        
        return result
    
    def _parallel_reasoning(self, case_data: Dict, mean_field: Optional[MeanField],
                           social_consensus: Optional[str], 
                           previous_opinions: List[AgentOpinion],
                           epoch: int = 0) -> List[AgentOpinion]:
        """并行推理 - 使用多线程
        
        Args:
            case_data: 案件数据
            mean_field: 平均场
            social_consensus: 社会共识
            previous_opinions: 上一轮观点
            epoch: 当前轮次（用于显示）
        """
        
        opinions = []
        case_id = case_data.get('case_id', 'unknown')
        
        print(f"  🤖 案例 {case_id} 第 {epoch + 1} 轮：{self.num_agents} 个智能体并行推理中...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # ✅ 复用预先创建的模型实例（性能优化：避免每轮重复创建）
            futures = {}
            agent_start_times = {}  # 记录每个agent的开始时间
            
            for agent in self.agents:
                agent_id = agent.agent_id
                
                # ✅ 使用预先创建的模型实例（已在__init__中绑定到agent.model）
                # 不再重复创建模型，直接使用已有的 agent.model
                
                # 根据社交网络筛选邻居观点
                if self.use_social_network and previous_opinions:
                    following_ids = self.following_network.get(str(agent_id), [])
                    neighbor_opinions = [
                        op for op in previous_opinions 
                        if op.agent_id in following_ids
                    ]
                else:
                    neighbor_opinions = []
                
                future = executor.submit(
                    agent.run_in_thread,
                    case_data,
                    mean_field,
                    social_consensus,
                    neighbor_opinions  # 传递邻居观点
                )
                futures[future] = agent_id
                agent_start_times[agent_id] = time.time()
            
            # 收集结果
            completed = 0
            failed = 0
            buyer_count = 0
            seller_count = 0
            
            for future in as_completed(futures):
                agent_id = futures[future]
                elapsed = time.time() - agent_start_times[agent_id]
                try:
                    opinion = future.result(timeout=300)  # 5分钟超时
                    opinions.append(opinion)
                    completed += 1
                    
                    # 统计裁决
                    if opinion.verdict == 'buyer':
                        buyer_count += 1
                    else:
                        seller_count += 1
                    
                    # 每完成一个智能体都输出进度
                    progress_bar = '█' * (completed * 20 // self.num_agents) + '░' * (20 - completed * 20 // self.num_agents)
                    print(f"  [{progress_bar}] {completed:2d}/{self.num_agents} 完成 | 买家:{buyer_count:2d} 卖家:{seller_count:2d} | 平均:{(time.time()-start_time)/completed:.1f}秒/智能体 | {case_id} Agent#{agent_id:2d}:{opinion.verdict}")
                    
                except Exception as e:
                    failed += 1
                    completed += 1
                    print(f"    ✗ 智能体 #{agent_id:2d} 失败 [{completed:2d}/{self.num_agents}] - 耗时: {elapsed:5.1f}秒 - 错误: {str(e)[:50]}")
                    import traceback
                    traceback.print_exc()
        
        elapsed = time.time() - start_time
        
        if opinions:
            print(f"  ✅ 第 {epoch + 1} 轮完成! 总耗时: {elapsed:.1f}秒 | 成功: {len(opinions)}/{self.num_agents} | 最终投票: 买家 {buyer_count} vs 卖家 {seller_count}")
            if failed > 0:
                print(f"  ⚠️  失败: {failed} 个智能体")
        else:
            print(f"  ⚠️  所有智能体推理失败!")
        
        return opinions
    
    def _compute_mean_field(self, epoch: int, opinions: List[AgentOpinion], case_data: Dict) -> MeanField:
        """计算平均场（生成文本总结）"""
        
        if not opinions:
            return MeanField(
                epoch=epoch,
                buyer_support_ratio=0.5,
                seller_support_ratio=0.5,
                consensus_level=0.5,  # 无观点时视为完全分歧
                mf_text=""
            )
        
        # 统计支持比例
        buyer_count = sum(1 for op in opinions if op.verdict == 'buyer')
        seller_count = len(opinions) - buyer_count
        
        buyer_ratio = buyer_count / len(opinions)
        seller_ratio = seller_count / len(opinions)
        
        # 共识程度 = 投票多的一方占总人数的比例
        consensus = max(buyer_count, seller_count) / len(opinions)
        
        # 生成平均场文本
        mf_text = self._generate_mean_field_text(epoch, opinions, case_data)
        
        return MeanField(
            epoch=epoch,
            buyer_support_ratio=buyer_ratio,
            seller_support_ratio=seller_ratio,
            consensus_level=consensus,
            mf_text=mf_text
        )
    
    def _generate_mean_field_text(self, epoch: int, opinions: List[AgentOpinion], case_data: Dict) -> str:
        """生成平均场文本总结（使用 prompt.py 的模板）"""
        try:
            # 获取旧的平均场文本
            old_mf_text = self.mean_field_history[-1].mf_text if self.mean_field_history else ''
            
            # 构建案例文本
            content_text = prompt.get_case_info_text(case_data)
            
            # 构建评论文本
            prompt_comment = ''
            for op in opinions:
                comment_data = {
                    'verdict': op.verdict,
                    'reasoning': op.reasoning
                }
                prompt_comment += prompt.summary_prompt_comment_template.substitute(comment_data)
            
            # 构建 prompt
            content_dict = {
                'content': content_text,
                'comment': prompt_comment,
                'mf_text': old_mf_text
            }
            prompt_text = prompt.summary_prompt_template.substitute(content_dict)
            
            # 同步生成平均场文本（参考 cot_agent_our_visual.py）
            result = self.summary_model.generate(prompt_text)
            return result.strip() if result else ""
                
        except Exception as e:
            print(f"  ⚠️  生成平均场文本失败: {e}")
            import traceback
            traceback.print_exc()
            return old_mf_text if self.mean_field_history else ""
    
    def _final_vote(self, final_opinions: List[AgentOpinion]) -> Dict:
        """最终投票"""
        
        buyer_votes = sum(1 for op in final_opinions if op.verdict == 'buyer')
        seller_votes = len(final_opinions) - buyer_votes
        
        verdict = 'buyer' if buyer_votes > seller_votes else 'seller'
        
        return {
            'verdict': verdict,
            'buyer_votes': buyer_votes,
            'seller_votes': seller_votes,
            'mean_field': self.mean_field_history[-1].to_dict() if self.mean_field_history else None
        }
    
    def _retrieve_social_consensus(self, case_data: Dict) -> Optional[str]:
        """检索社会共识"""
        try:
            hits = retrieve_consensus_for_case(case_data, k=3)
            if hits:
                parts = ["相似案例参考（Top-3）："]
                for i, h in enumerate(hits, 1):
                    case_id = h.get('id', h.get('case_id', 'N/A'))
                    parts.append(f"{i}. 案件{case_id} (相似度{h.get('score', 0):.2f})")
                    parts.append(f"   {h.get('reflection_result', '')[:200]}...")
                return "\n".join(parts)
        except Exception as e:
            print(f"  ⚠️  社会共识检索失败: {e}")
        return None
    
    def _print_epoch_summary(self, epoch: int, mean_field: MeanField, opinions: List[AgentOpinion]):
        """打印讨论总结"""
        buyer_votes = int(mean_field.buyer_support_ratio * len(opinions))
        seller_votes = int(mean_field.seller_support_ratio * len(opinions))
        print(f"\n  📊 平均场更新: 买家 {buyer_votes}/{len(opinions)} ({mean_field.buyer_support_ratio:.1%}) | 卖家 {seller_votes}/{len(opinions)} ({mean_field.seller_support_ratio:.1%}) | 共识度 {mean_field.consensus_level:.1%}")
    
    def _build_result(self, case_data: Dict, final_verdict: Dict, all_epoch_opinions: List[List[AgentOpinion]]) -> Dict:
        """构建结果
        
        Args:
            case_data: 案件数据
            final_verdict: 最终裁决
            all_epoch_opinions: 所有轮次的智能体观点列表
        
        Returns:
            结果字典
        """
        # 基本信息
        result = {
            'case_id': case_data.get('id', case_data.get('case_id', 'unknown')),
            'num_epochs': len(self.mean_field_history),
            'num_agents': self.num_agents,
            'final_verdict': final_verdict,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 根据配置决定保存方式
        save_all_epochs = self.config.get('save_all_epochs', False)
        
        if save_all_epochs:
            # 保存所有轮次的数据
            # 1. 保存所有轮次的智能体观点
            result['all_epochs_opinions'] = [
                {
                    'epoch': epoch_idx,
                    'agent_opinions': [
                        {
                            'agent_id': op.agent_id,
                            'verdict': op.verdict,
                            'reasoning': op.reasoning
                        } for op in epoch_opinions
                    ]
                } for epoch_idx, epoch_opinions in enumerate(all_epoch_opinions)
            ]
            # 2. 保存所有轮次的平均场
            result['mean_field_history'] = [mf.to_dict() for mf in self.mean_field_history]
        else:
            # 只保存最后一轮的数据（节省空间）
            # 1. 只保存最后一轮的智能体观点
            result['final_agent_opinions'] = [
                {
                    'agent_id': op.agent_id,
                    'verdict': op.verdict,
                    'reasoning': op.reasoning
                } for op in all_epoch_opinions[-1]
            ]
            # 2. 只保存最后一轮的平均场
            if self.mean_field_history:
                result['final_mean_field'] = self.mean_field_history[-1].to_dict()
            else:
                result['final_mean_field'] = None
        
        return result
    
    def _save_result(self, case_id: str, result: Dict):
        """保存结果（文件名包含评审结果）"""
        # 判断评审结果是否正确
        predicted = result.get('final_verdict', {}).get('verdict', '').lower()
        ground_truth = 'buyer' if result.get('ground_truth', '').get('court_support', 0) == 0 else 'seller'
        
        # 构建文件名：{case_id}_debate_{correct/wrong}.json
        output_file = self.output_dir / f"{case_id}_debate_{predicted == ground_truth}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 结果已保存: {output_file.name} {predicted == ground_truth}")
    
    def _flush_all_token_logs(self, epoch: int):
        """批量写入所有智能体和平均场模型的 token 使用日志
        
        Args:
            epoch: 当前轮次（-1 表示最终写入）
        """
        try:
            # 收集所有模型的 token 使用记录
            all_token_records = []
            
            # 收集所有智能体的 token 记录
            for agent in self.agents:
                if agent.model.token_usage_buffer:
                    all_token_records.extend(agent.model.token_usage_buffer)
            
            # 收集平均场生成模型的 token 记录
            if self.summary_model.token_usage_buffer:
                all_token_records.extend(self.summary_model.token_usage_buffer)
            
            # 如果有记录，批量写入
            if all_token_records:
                # 使用第一个智能体的模型写入（它们共享同一个 token_log_path）
                token_log_path = self.agents[0].model.token_log_path
                
                # 读取已有数据
                if token_log_path.exists():
                    try:
                        content = token_log_path.read_text(encoding='utf-8')
                        existing = json.loads(content) if content.strip() else []
                        if not isinstance(existing, list):
                            existing = []
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"[token_log] 读取失败，重新创建: {e}")
                        existing = []
                else:
                    existing = []
                
                # 批量追加
                existing.extend(all_token_records)
                token_log_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')
                
                # 清空所有模型的缓冲区
                for agent in self.agents:
                    agent.model.clear_token_buffer()
                self.summary_model.clear_token_buffer()
                
                if epoch >= 0:
                    print(f"  💾 第 {epoch + 1} 轮 token 日志已保存 ({len(all_token_records)} 条记录)")
                else:
                    print(f"  💾 最终 token 日志已保存 ({len(all_token_records)} 条记录)")
                    
        except Exception as e:
            print(f"[token_log] 批量写入失败: {e}")
            import traceback
            traceback.print_exc()
