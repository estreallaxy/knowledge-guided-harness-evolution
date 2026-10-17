import json
import time
from typing import List, Dict, Any, Optional

class DialogTraj:
    def __init__(self, system_prompt: str = None, session_id: str = None):
        """
        初始化对话轨迹对象。
        
        Args:
            system_prompt: 可选的系统提示词（System Message）。
            session_id: 可选的会话 ID，用于追踪。
        """
        self.session_id = session_id or str(int(time.time()))
        self.system_prompt = system_prompt
        self.turns: List[Dict[str, Any]] = []
        self.creation_time = time.time()
    def reset(self):
        """重置对话轨迹，清空所有轮次。"""
        self.turns = []
    def add_turn(self, 
                 user_input: str, 
                 ai_response: str, 
                 llm_type: str = None, 
                 user_feedback: str = None,
                 **extra_info):
        """
        记录一轮对话。
        
        Args:
            user_input: 用户的输入内容。
            ai_response: AI 的回复内容。
            llm_type: AI 回复的类型标记 (例如 "E1", "NE" 等)。
            **extra_info: 任意额外的键值对信息。
                          例如: reward=0.5, user_feedback='POS', latency=1.2
        """
        turn_data = {
            "turn_index": len(self.turns),
            "timestamp": time.time(),
            "user_input": user_input,
            "user_feedback": user_feedback,
            "ai_response": ai_response,
            "llm_type": llm_type,
            "extra_info": extra_info  # 将所有额外信息存入一个字典
        }
        self.turns.append(turn_data)

    def get_openai_messages(self) -> List[Dict[str, str]]:
        """
        将当前历史记录转换为 OpenAI Chat 格式的 list。
        用于传给 LLM 生成下一句话。
        
        Returns:
            [
                {"role": "system", "content": "..."},
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."},
                ...
            ]
        """
        messages = []
        
        # 1. 添加 System Prompt (如果有)
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
            
        # 2. 添加历史轮次
        for turn in self.turns:
            messages.append({"role": "user", "content": turn["user_input"]})
            messages.append({"role": "assistant", "content": turn["ai_response"]})
            
        return messages

    def get_last_turn(self) -> Optional[Dict[str, Any]]:
        """获取最后一轮的数据"""
        return self.turns[-1] if self.turns else None

    def to_dict(self) -> Dict[str, Any]:
        """序列化整个对象为字典"""
        return {
            "session_id": self.session_id,
            "system_prompt": self.system_prompt,
            "creation_time": self.creation_time,
            "turn_count": len(self.turns),
            "turns": self.turns
        }

    def save_json(self, file_path: str):
        """保存到 JSON 文件"""
        data = self.to_dict()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @classmethod
    def load_json(cls, file_path: str):
        """从 JSON 文件加载回对象"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 重建对象
        instance = cls(
            system_prompt=data.get("system_prompt"),
            session_id=data.get("session_id")
        )
        instance.turns = data.get("turns", [])
        instance.creation_time = data.get("creation_time", time.time())
        return instance

    def __len__(self):
        return len(self.turns)

    def __repr__(self):
        return f"<DialogTraj id={self.session_id} turns={len(self)}>"


# # ================= 使用示例 =================
# if __name__ == "__main__":
#     # 1. 创建轨迹
#     traj = DialogTraj(system_prompt="You are a helpful AI assistant.")

#     # 2. 第一轮：模型回复类型 E1，尚未获得奖励
#     traj.add_turn(
#         user_input="你好，帮我写一首关于秋天的诗。",
#         ai_response="秋风起兮白云飞...",
#         llm_type="E1",
#         user_feedback = "NEU",
#         # 额外信息可以无限添加
#         latency=0.5,
#         model_version="qwen-7b" 
#     )

#     # 3. 模拟获得用户反馈，更新上一轮的 extra_info (通常在实际应用中发生)
#     # 假设我们拿到了 reward，想存进去
#     last_turn = traj.get_last_turn()
#     if last_turn:
#         last_turn["extra_info"]["user_feedback"] = "POS"
#         last_turn["extra_info"]["reward_score"] = 1.0

#     # 4. 第二轮
#     traj.add_turn(
#         user_input="再短一点。",
#         ai_response="落叶知秋。",
#         llm_type="E2",
#         user_feedback="NEU", # 也可以直接在添加时传入
#         reward_score=0.1
#     )

#     # 5. 获取用于下一次推理的 messages
#     print("=== OpenAI Messages ===")
#     print(json.dumps(traj.get_openai_messages(), indent=2, ensure_ascii=False))

#     # 6. 保存轨迹
#     traj.save_json("dialog_session_001.json")
#     print(f"\nSaved trajectory with {len(traj)} turns.")