import os
import json
import glob
from tqdm import tqdm
from src.agent.utils.reward import compute_reward

# ================= 配置 =================
# 输入：重写后的数据目录（包含 new_last_turn_response）
INPUT_DIRS = [
    "./dataset/our_dataset/rewritten/lmsys_r",
    "./dataset/our_dataset/rewritten/WildChat_r"
]

# 输出目录（保持结构）
OUTPUT_BASE_DIR = "./dataset/our_dataset/rewritten_with_info_r"

os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

# ================= 辅助函数：提取最后一轮的 input + history =================
def extract_last_turn_for_reward(conversation):
    """
    从 conversation 中提取最后一轮的：
    - history: 所有在最后一轮 assistant 之前的 messages
    - input_text: 最后一轮的 user 消息
    - response_text: 最后一轮的 assistant 消息（这里用 new_last_turn_response）
    
    假设 conversation 是标准的交替 user/assistant 列表。
    """
    if not conversation:
        return None, None, None

    # 找到最后一个 assistant 的位置
    last_assist_idx = None
    for i in range(len(conversation) - 1, -1, -1):
        if conversation[i].get("role") == "assistant":
            last_assist_idx = i
            break

    if last_assist_idx is None or last_assist_idx == 0:
        return None, None, None

    # 确保前一个是 user
    if conversation[last_assist_idx - 1].get("role") != "user":
        return None, None, None

    history = conversation[:last_assist_idx - 1]  # 不包含当前轮的 user
    input_text = conversation[last_assist_idx - 1]["content"]
    response_text = None  # 将由外部传入（new_last_turn_response）

    return history, input_text, response_text

# ================= 主处理函数 =================
def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8') as fout:

        lines = fin.readlines()
        for line in tqdm(lines, desc=f"Processing {os.path.basename(input_path)}"):
            line = line.strip()
            if not line:
                fout.write(line + "\n")
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                fout.write(line + "\n")
                continue

            # 检查必要字段
            if "conversation" not in data or "new_last_turn_response" not in data:
                fout.write(line + "\n")
                continue

            conversation = data["conversation"]
            new_response = data["new_last_turn_response"]

            # 提取上下文和 user input
            history, input_text, _ = extract_last_turn_for_reward(conversation)
            if history is None or input_text is None:
                fout.write(line + "\n")
                continue

            try:
                # 调用你的 reward 函数（只取 info_r）
                # 注意：这里 user_feedback_category 和 llm_response_type 无法获取，
                # 所以只计算 info_r 部分（假设 compute_reward 支持仅传前两个参数）
                _, info_r = compute_reward(input_text, new_response, "NEU", "NE", history=history)
                data["improve_info_reward"] = info_r
            except Exception as e:
                # 如果 compute_reward 报错，保留原数据
                pass

            fout.write(json.dumps(data, ensure_ascii=False) + "\n")

# ================= 主程序 =================
def main():
    all_files = []
    for d in INPUT_DIRS:
        all_files.extend(glob.glob(os.path.join(d, "*.jsonl")))

    print(f"📁 Found {len(all_files)} JSONL files.")

    for input_file in tqdm(all_files, desc="Overall progress"):
        rel_path = os.path.relpath(input_file, "./dataset/our_dataset/rewritten")
        output_file = os.path.join(OUTPUT_BASE_DIR, rel_path)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        process_file(input_file, output_file)

    print("✅ All done! Output saved to:", OUTPUT_BASE_DIR)

if __name__ == "__main__":
    main()