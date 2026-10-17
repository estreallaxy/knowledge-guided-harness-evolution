# import pandas as pd
# import numpy as np
# from pathlib import Path

# class FeedbackMatrixManager:
#     # 定义标准的行和列顺序
#     ORDER_LLM = ["NE","E1","E2","E3","E4","E5","E6","E7","E8","E9","E10","E11"]
#     ORDER_FB = ["NEU","NEG_1","NEG_2","NEG_3","NEG_4","NEG_5","POS","STOP"]

#     def __init__(self, base_json_path, user_json_path, alpha=0.03):
#         """
#         Args:
#             base_json_path (str): 基础矩阵（计数）路径
#             user_json_path (str): 用户矩阵（计数）路径
#             alpha (float): 插值系数 (0.0 ~ 1.0)。
#                            Total = (1 - alpha) * Base_Norm + alpha * User_Norm
#         """
#         self.base_json_path = Path(base_json_path)
#         self.user_json_path = Path(user_json_path)
#         self.alpha = alpha

#         # 1. 加载基础矩阵 (Counts)
#         self.base_df = self._load_matrix(self.base_json_path, is_base=True)

#         # 2. 加载或初始化用户矩阵 (Counts)
#         self.user_df = self._load_user_matrix()

#         # 3. 计算 Total 矩阵 (Probabilities / Scores)
#         self.total_df = pd.DataFrame() 
#         self._update_total_matrix()

#     def _load_matrix(self, path, is_base=False):
#         if not path.exists():
#             if is_base:
#                 raise FileNotFoundError(f"Base matrix not found at: {path}")
#             else:
#                 return self._create_zero_matrix()

#         try:
#             df = pd.read_json(path, orient="index")
#             df = df.reindex(index=self.ORDER_LLM, columns=self.ORDER_FB, fill_value=0)
#             return df.astype(float)
#         except Exception as e:
#             print(f"[ERROR] Failed to load json from {path}: {e}")
#             return self._create_zero_matrix()

#     def _create_zero_matrix(self):
#         return pd.DataFrame(0.0, index=self.ORDER_LLM, columns=self.ORDER_FB)

#     def _load_user_matrix(self):
#         if not self.user_json_path.exists():
#             df = self._create_zero_matrix()
#             self._save_matrix(df, self.user_json_path)
#             return df
#         else:
#             return self._load_matrix(self.user_json_path)

#     def _save_matrix(self, df, path):
#         df.to_json(path, orient="index", indent=4)

#     def _normalize_df(self, df):
#         """按行归一化 (Counts -> Prob)"""
#         row_sums = df.sum(axis=1)
#         # 避免除以0，若和为0，则该行全为0
#         norm_df = df.div(row_sums, axis=0).fillna(0.0)
#         return norm_df

#     def _update_total_matrix(self):
#         """
#         核心逻辑：线性插值融合
#         Formula: Total = (1 - alpha) * Base_Norm + alpha * User_Norm
#         """
#         # 1. 计算归一化矩阵
#         base_norm = self._normalize_df(self.base_df)
#         user_norm = self._normalize_df(self.user_df)

#         # 2. 应用公式
#         # 注意：如果某一行用户还没数据，user_norm 这一行为全0。
#         # 此时 total = (1-alpha)*base + 0。
#         # 该行的和将变成 (1-alpha)，而不是 1。
#         # 这在 get_final_prob 中会被重新归一化处理，逻辑是自洽的。
#         self.total_df = (base_norm * (1 - self.alpha)) + (user_norm * self.alpha)

#     # ================= 公共接口 =================

#     def set_alpha(self, new_alpha):
#         """运行时调整 alpha"""
#         if not (0 <= new_alpha <= 1.0):
#             print(f"[WARN] Alpha {new_alpha} is typically between 0 and 1.")
        
#         self.alpha = new_alpha
#         self._update_total_matrix()

#     def update_user_feedback(self, llm_type, feedback_category, count=1):
#         """更新用户反馈并刷新矩阵"""
#         if llm_type not in self.ORDER_LLM or feedback_category not in self.ORDER_FB:
#             return

#         # 更新计数
#         self.user_df.at[llm_type, feedback_category] += count

#         # 保存
#         self._save_matrix(self.user_df, self.user_json_path)

#         # 刷新
#         self._update_total_matrix()

#     def get_final_prob(self, llm_type, feedback_category):
#         """
#         获取最终用于采样的概率。
#         会自动处理行和不为1的情况（例如用户数据缺失导致的权重衰减）。
#         """
#         if llm_type not in self.total_df.index:
#             return 0.0
        
#         score = self.total_df.at[llm_type, feedback_category]
#         row_sum = self.total_df.loc[llm_type].sum()
        
#         if row_sum == 0:
#             return 0.0
        
#         # 重新归一化，确保返回的是严格的概率
#         return score / row_sum

#     def get_total_row_dict(self, llm_type):
#         """获取某一行完整的概率分布"""
#         if llm_type not in self.total_df.index:
#             return {}
        
#         row = self.total_df.loc[llm_type]
#         row_sum = row.sum()
        
#         if row_sum > 0:
#             return (row / row_sum).to_dict()
#         else:
#             return row.to_dict() # 全0

# # ================= 测试代码 =================
# # if __name__ == "__main__":
# #     base_path = "contingency_table_result.json"
# #     user_path = "user_feedback_matrix_interp.json"

# #     # 初始化：alpha = 0.2 (主要信赖 Base，20% 信赖 User)
# #     manager = FeedbackMatrixManager(base_path, user_path, alpha=0.2)

# #     print("=== State 1: No User Data ===")
# #     # 此时 user_norm 为 0。
# #     # total = 0.8 * base + 0.2 * 0 = 0.8 * base
# #     # get_final_prob 会做除法: (0.8 * p) / 0.8 = p
# #     # 所以结果应该等于 base 的概率
# #     prob_base = manager.get_final_prob('E1', 'POS')
# #     print(f"Final Prob (E1, POS) [Should equal Base]: {prob_base:.4f}")

# #     print("\n=== State 2: User gives intense feedback ===")
# #     # 用户给 E1 投了 POS
# #     manager.update_user_feedback("E1", "POS", count=1)
    
# #     # 此时 User Norm 对于 E1 来说：POS=1.0, 其他=0
# #     # Base Norm (假设): POS=0.5, NEG=0.5
# #     # Total = 0.8 * [0.5, 0.5] + 0.2 * [1.0, 0.0]
# #     #       = [0.4, 0.4] + [0.2, 0.0] 
# #     #       = [0.6, 0.4]
# #     # 归一化后: POS=0.6, NEG=0.4 (可见 POS 概率上升了)
    
# #     dist = manager.get_total_row_dict("E1")
# #     print(f"New Dist (E1): {dist}")





import pandas as pd
import numpy as np
from pathlib import Path

class FeedbackMatrixManager:
    # 定义标准的行和列顺序
    ORDER_LLM = ["NE","E1","E2","E3","E4","E5","E6","E7","E8","E9","E10","E11"]
    ORDER_FB = ["NEU","NEG_1","NEG_2","NEG_3","NEG_4","NEG_5","POS","STOP"]

    def __init__(self, base_json_path, user_json_path, alpha=0.001):
        """
        Args:
            base_json_path (str): 基础矩阵（计数）路径
            user_json_path (str): 用户矩阵（计数）路径
            alpha (float): 插值系数 (0.0 ~ 1.0)。
                           Total = (1 - alpha) * Base_Norm + alpha * User_Norm
        """
        self.base_json_path = Path(base_json_path)
        self.user_json_path = Path(user_json_path)
        self.alpha = alpha

        # 1. 加载基础矩阵 (Counts)
        self.base_df = self._load_matrix(self.base_json_path, is_base=True)

        # 2. 加载或初始化用户矩阵 (Counts)
        self.user_df = self._load_user_matrix()

        # 3. 计算 Total 矩阵 (Probabilities / Scores)
        self.total_df = pd.DataFrame() 
        self._update_total_matrix()

    def _load_matrix(self, path, is_base=False):
        if not path.exists():
            if is_base:
                raise FileNotFoundError(f"Base matrix not found at: {path}")
            else:
                return self._create_zero_matrix()

        try:
            df = pd.read_json(path, orient="index")
            df = df.reindex(index=self.ORDER_LLM, columns=self.ORDER_FB, fill_value=0)
            return df.astype(float)
        except Exception as e:
            print(f"[ERROR] Failed to load json from {path}: {e}")
            return self._create_zero_matrix()

    def _create_zero_matrix(self):
        return pd.DataFrame(0.0, index=self.ORDER_LLM, columns=self.ORDER_FB)

    def _load_user_matrix(self):
        if not self.user_json_path.exists():
            df = self._create_zero_matrix()
            self._save_matrix(df, self.user_json_path)
            return df
        else:
            return self._load_matrix(self.user_json_path)

    def _save_matrix(self, df, path):
        df.to_json(path, orient="index", indent=4)

    def _normalize_df(self, df):
        """按行归一化 (Counts -> Prob)"""
        row_sums = df.sum(axis=1)
        # 避免除以0，若和为0，则该行全为0
        norm_df = df.div(row_sums, axis=0).fillna(0.0)
        return norm_df

    def _update_total_matrix(self):
        """
        核心逻辑：线性插值融合
        Formula: Total = (1 - alpha) * Base_Norm + alpha * User_Norm
        """
        # 1. 计算归一化矩阵
        base_norm = self._normalize_df(self.base_df)
        user_norm = self._normalize_df(self.user_df)

        # 2. 应用公式
        # 注意：如果某一行用户还没数据，user_norm 这一行为全0。
        # 此时 total = (1-alpha)*base + 0。
        # 该行的和将变成 (1-alpha)，而不是 1。
        # 这在 get_final_prob 中会被重新归一化处理，逻辑是自洽的。
        self.total_df = (base_norm * (1 - self.alpha)) + (user_norm * self.alpha)

    # ================= 公共接口 =================

    def set_alpha(self, new_alpha):
        """运行时调整 alpha"""
        if not (0 <= new_alpha <= 1.0):
            print(f"[WARN] Alpha {new_alpha} is typically between 0 and 1.")
        
        self.alpha = new_alpha
        self._update_total_matrix()

    def update_user_feedback(self, llm_type, feedback_category, count=1):
        """更新用户反馈并刷新矩阵"""
        if llm_type not in self.ORDER_LLM or feedback_category not in self.ORDER_FB:
            return

        # 更新计数
        self.user_df.at[llm_type, feedback_category] += count

        # 保存
        self._save_matrix(self.user_df, self.user_json_path)

        # 刷新
        self._update_total_matrix()

    def get_final_prob(self, llm_type, feedback_category):
        """
        获取最终用于采样的概率。
        会自动处理行和不为1的情况（例如用户数据缺失导致的权重衰减）。
        """
        if llm_type not in self.total_df.index:
            return 0.0
        
        score = self.total_df.at[llm_type, feedback_category]
        row_sum = self.total_df.loc[llm_type].sum()
        
        if row_sum == 0:
            return 0.0
        
        # 重新归一化，确保返回的是严格的概率
        return score / row_sum

    def get_total_row_dict(self, llm_type):
        """获取某一行完整的概率分布"""
        if llm_type not in self.total_df.index:
            return {}
        
        row = self.total_df.loc[llm_type]
        row_sum = row.sum()
        
        if row_sum > 0:
            return (row / row_sum).to_dict()
        else:
            return row.to_dict() # 全0
    def get_reward_matrix(self):
        reward_table = {
            "POS": {"NE": 1.0, "E8": 0.5, "E7": 0.5, "E6": 0.5, "E4": 0.2, "E3": 0.2, "E1": 0.2, "E2": 0.2, "E11": 0.2, "E5": -0.2, "E9": -0.2, "E10": -0.2},
            "NEU": {"NE": 0.5, "E8": 0.2, "E7": 0.2, "E6": 0.2, "E4": -0.1, "E3": -0.1, "E1": -0.1, "E2": -0.1, "E11": -0.1, "E5": -0.3, "E9": -0.3, "E10": -0.3},
            "STOP": {"NE": 0.2, "E8": 0.1, "E7": 0.1, "E6": 0.1, "E4": -0.2, "E3": -0.2, "E1": -0.2, "E2": -0.2, "E11": -0.2, "E5": -0.4, "E9": -0.4, "E10": -0.4},
            "NEG_5": {"NE": 0.0, "E8": -0.1, "E7": -0.1, "E6": -0.1, "E4": -0.3, "E3": -0.3, "E1": -0.3, "E2": -0.3, "E11": -0.3, "E5": -0.4, "E9": -0.4, "E10": -0.4},
            "NEG_1": {"NE": -0.1, "E8": -0.3, "E7": -0.3, "E6": -0.3, "E4": -0.5, "E3": -0.5, "E1": -0.5, "E2": -0.5, "E11": -0.5, "E5": -0.6, "E9": -0.6, "E10": -0.6},
            "NEG_4": {"NE": -0.1, "E8": -0.4, "E7": -0.4, "E6": -0.4, "E4": -0.6, "E3": -0.6, "E1": -0.6, "E2": -0.6, "E11": -0.6, "E5": -0.7, "E9": -0.7, "E10": -0.7},
            "NEG_3": {"NE": -0.1, "E8": -0.6, "E7": -0.6, "E6": -0.6, "E4": -0.8, "E3": -0.8, "E1": -0.8, "E2": -0.8, "E11": -0.8, "E5": -0.8, "E9": -0.8, "E10": -0.8},
            "NEG_2": {"NE": -0.2, "E8": -0.7, "E7": -0.7, "E6": -0.7, "E4": -0.9, "E3": -0.9, "E1": -0.9, "E2": -0.9, "E11": -0.9, "E5": -0.9, "E9": -0.9, "E10": -0.9}
        }

        # 获取每个 LLM 的最终概率分布（行归一化后的 total_df）
        expected_rewards = {}

        for llm in self.ORDER_LLM:
            exp_reward = 0.0
            prob_dist = self.get_total_row_dict(llm)  # {feedback: prob}

            for fb, prob in prob_dist.items():
                if prob == 0.0:
                    continue
                # 从 reward_table[fb][llm] 获取奖励
                fb_rewards = reward_table.get(fb, {})
                reward = fb_rewards.get(llm, 0.0)  # 若未定义，默认0
                exp_reward += prob * reward

            expected_rewards[llm] = exp_reward

        return expected_rewards
# ================= 测试代码 =================
# if __name__ == "__main__":
#     base_path = "contingency_table_result.json"
#     user_path = "user_feedback_matrix_interp.json"

#     # 初始化：alpha = 0.2 (主要信赖 Base，20% 信赖 User)
#     manager = FeedbackMatrixManager(base_path, user_path, alpha=0.2)

#     print("=== State 1: No User Data ===")
#     # 此时 user_norm 为 0。
#     # total = 0.8 * base + 0.2 * 0 = 0.8 * base
#     # get_final_prob 会做除法: (0.8 * p) / 0.8 = p
#     # 所以结果应该等于 base 的概率
#     prob_base = manager.get_final_prob('E1', 'POS')
#     print(f"Final Prob (E1, POS) [Should equal Base]: {prob_base:.4f}")

#     print("\n=== State 2: User gives intense feedback ===")
#     # 用户给 E1 投了 POS
#     manager.update_user_feedback("E1", "POS", count=1)
    
#     # 此时 User Norm 对于 E1 来说：POS=1.0, 其他=0
#     # Base Norm (假设): POS=0.5, NEG=0.5
#     # Total = 0.8 * [0.5, 0.5] + 0.2 * [1.0, 0.0]
#     #       = [0.4, 0.4] + [0.2, 0.0] 
#     #       = [0.6, 0.4]
#     # 归一化后: POS=0.6, NEG=0.4 (可见 POS 概率上升了)
    
#     dist = manager.get_total_row_dict("E1")
#     print(f"New Dist (E1): {dist}")