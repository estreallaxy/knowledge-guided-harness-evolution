import os
import json
import glob
from tqdm import tqdm

# ================= 配置 =================
INPUT_DIRS = [
    "./dataset/our_dataset/rewritten_with_info_r/lmsys_r",
    "./dataset/our_dataset/rewritten_with_info_r/WildChat_r"
]

true_count = 0
false_count = 0
total_valid = 0

print("🔍 Scanning files and computing label distribution...")

for d in INPUT_DIRS:
    for file_path in glob.glob(os.path.join(d, "*.jsonl")):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except:
                    continue

                # 检查必要字段
                if "improve_info_reward" not in data or "average_r" not in data:
                    continue

                improve_r = data["improve_info_reward"]
                avg_r = data["average_r"]

                # 跳过无效数值
                if not isinstance(improve_r, (int, float)) or not isinstance(avg_r, (int, float)):
                    continue

                total_valid += 1
                if improve_r > avg_r:
                    true_count += 1
                else:
                    false_count += 1

# ================= 输出统计 =================
if total_valid == 0:
    print("❌ No valid samples found with both 'improve_info_reward' and 'average_r'.")
else:
    true_ratio = true_count / total_valid
    false_ratio = false_count / total_valid

    print("\n" + "="*50)
    print(f"✅ Total valid samples: {total_valid}")
    print(f"   - True  (improve_info_reward > average_r): {true_count} ({true_ratio:.2%})")
    print(f"   - False (improve_info_reward <= average_r): {false_count} ({false_ratio:.2%})")
    print("="*50)

    # 健康比例建议
    if 0.3 <= true_ratio <= 0.7:
        print("💡 Label distribution is balanced. Suitable for KTO!")
    else:
        print("⚠️  Label distribution is skewed. Consider:")
        print("    - Adjusting the comparison logic")
        print("    - Adding a margin (e.g., improve_r > avg_r + 0.1)")