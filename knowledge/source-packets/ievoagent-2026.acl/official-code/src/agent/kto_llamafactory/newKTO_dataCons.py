import os
import json
import glob
import random
from tqdm import tqdm

# ===== 配置 =====
INPUT_DIRS = [
    "./dataset/our_dataset/rewritten_with_info_r/lmsys_r",
    "./dataset/our_dataset/rewritten_with_info_r/WildChat_r"
]

OUTPUT_DIR = "./src/train/kto_llamafactory/new_kto_data"
SEED = 42

def standardize_role(role):
    if role == "user":
        return "human"
    elif role == "assistant":
        return "gpt"
    elif role == "system":
        return "system"
    return role

def build_kto_sample(data):
    conv = data.get("conversation", [])
    new_resp = data.get("new_last_turn_response", "")
    improve_r = data.get("improve_info_reward", None)
    avg_r = data.get("average_r", None)

    if improve_r is None or avg_r is None or not conv or not new_resp:
        return None

    # 找到最后一个 assistant 的位置
    last_assist_idx = None
    for i in range(len(conv) - 1, -1, -1):
        if conv[i].get("role") == "assistant":
            last_assist_idx = i
            break
    if last_assist_idx is None or last_assist_idx == 0:
        return None
    if conv[last_assist_idx - 1].get("role") != "user":
        return None

    # 构建 messages（用新回复替换最后一句）
    messages = []
    for msg in conv[:last_assist_idx]:
        messages.append({
            "from": standardize_role(msg["role"]),
            "value": msg["content"]
        })
    messages.append({"from": "gpt", "value": new_resp})

    # 打标签：新 reward 是否优于历史平均
    label = improve_r > avg_r
    return {"messages": messages, "label": label}

# ===== 主逻辑 =====
all_samples = []

print("📂 Loading and building KTO samples...")
for d in INPUT_DIRS:
    for file_path in glob.glob(os.path.join(d, "*.jsonl")):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    sample = build_kto_sample(data)
                    if sample:
                        all_samples.append(sample)
                except Exception:
                    continue

print(f"✅ Built {len(all_samples)} KTO samples.")

# 随机打乱（固定 seed）
random.seed(SEED)
random.shuffle(all_samples)

# 划分比例
total = len(all_samples)
n_train = int(total * 0.90)
n_val = int(total * 0.05)
n_test = total - n_train - n_val  # 防止浮点误差

train_data = all_samples[:n_train]
val_data = all_samples[n_train:n_train + n_val]
test_data = all_samples[n_train + n_val:]

# 保存目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 保存函数
def save_split(name, data):
    path = os.path.join(OUTPUT_DIR, f"kto_{name}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  - {name.capitalize()}: {len(data)} samples → {path}")

print("\nSplitOptions:")
save_split("train", train_data)
save_split("val", val_data)
save_split("test", test_data)

print(f"\n🎉 All splits saved to: {OUTPUT_DIR}")