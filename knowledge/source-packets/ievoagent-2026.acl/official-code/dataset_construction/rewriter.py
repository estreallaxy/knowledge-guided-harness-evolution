# import os
# import json
# import glob
# import time
# from tqdm import tqdm
# from openai import OpenAI, RateLimitError, APIError

# # ================= 配置 =================
# SOURCE_DIRS = [
#     "./dataset/our_dataset/lmsys_r",
#     "./dataset/our_dataset/WildChat_r"
# ]
# OUTPUT_BASE_DIR = "./dataset/our_dataset/rewritten"
# MAX_TURNS = 12

# API_KEYS = ["YOUR_API_KEY","YOUR_API_KEY","YOUR_API_KEY","YOUR_API_KEY"]  # 建议后续从文件或环境变量读取

# os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

# # ================= 辅助函数 =================
# def group_conversation_into_turns(messages):
#     turns = []
#     i = 0
#     while i < len(messages) and messages[i].get("role") != "user":
#         i += 1
#     while i < len(messages):
#         if messages[i].get("role") == "user":
#             user_msg = messages[i].get("content", "")
#             if i + 1 < len(messages) and messages[i + 1].get("role") == "assistant":
#                 assistant_msg = messages[i + 1].get("content", "")
#                 turns.append({"user": user_msg, "assistant": assistant_msg})
#                 i += 2
#             else:
#                 return turns, user_msg
#         else:
#             i += 1
#     return turns, None

# def extract_for_rewrite(messages, max_turns=5):
#     completed_turns, pending_user = group_conversation_into_turns(messages)
#     if pending_user is not None or not completed_turns:
#         return None, None, None
#     last_turn = completed_turns[-1]
#     context_turns = completed_turns[:-1][-max_turns:]
#     return context_turns, last_turn["user"], last_turn["assistant"]

# def rewrite_with_openai(context_turns, last_user, last_assistant, api_keys, max_retries=3):
#     history = ""
#     for turn in context_turns:
#         history += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
#     prompt = f'''You are a concise and accurate AI assistant. Improve the assistant's last response based on the full conversation below.

# Requirements:
# 1. Stay strictly grounded in the context—no hallucination.
# 2. Match the user's intent: be factual if they ask for facts, brief if they want brevity, helpful if they seek advice.
# 3. Keep it natural and to the point.
# 4. Fix any inaccuracies, vagueness, or unsafe content in the original.
# 5. If the original response is wrong or hallucinated, ignore it and generate a correct answer.
# 6. Only output the improved response. No explanations, prefixes, or markdown.

# [Conversation History]
# {history}

# [Current User Instruction]
# {last_user}

# [Original Response]
# {last_assistant}

# [Improved Response]'''

#     for attempt in range(max_retries):
#         key = api_keys[attempt % len(api_keys)]
#         try:
#             client = OpenAI(api_key=key, base_url='https://api.gptsapi.net/v1')  # 修正：移除多余空格
#             response = client.chat.completions.create(
#                 model="gpt-4o",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.0,
#                 max_tokens=2048  # 合理限制输出长度
#             )
#             return response.choices[0].message.content.strip()
#         except (RateLimitError, APIError) as e:
#             print(f"API error (retry {attempt+1}/{max_retries}): {e}")
#             time.sleep(2 ** attempt)
#         except Exception as e:
#             print(f"Unexpected error: {e}")
#             break
#     return None

# def process_single_line(line, api_keys):
#     original_line = line
#     line = line.strip()
#     if not line:
#         return original_line.rstrip('\n')
#     try:
#         data = json.loads(line)
#     except json.JSONDecodeError:
#         return original_line.rstrip('\n')

#     if "conversation" not in data:
#         return original_line.rstrip('\n')

#     messages = data["conversation"]
#     context_turns, last_user, last_assistant = extract_for_rewrite(messages, max_turns=MAX_TURNS)

#     if None in (context_turns, last_user, last_assistant):
#         return original_line.rstrip('\n')

#     new_response = rewrite_with_openai(context_turns, last_user, last_assistant, api_keys)
#     if new_response is not None:
#         data["new_last_turn_response"] = new_response

#     return json.dumps(data, ensure_ascii=False)

# def process_file(input_path, output_path, api_keys):
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#     with open(input_path, 'r', encoding='utf-8') as fin, \
#          open(output_path, 'w', encoding='utf-8') as fout:
#         # 获取总行数用于进度条
#         total_lines = sum(1 for _ in open(input_path, 'r', encoding='utf-8'))
#         fin.seek(0)  # 重置文件指针

#         with tqdm(total=total_lines, desc=f"Processing {os.path.basename(input_path)}", leave=False) as pbar:
#             for line in fin:
#                 result_line = process_single_line(line, api_keys)
#                 fout.write(result_line + "\n")
#                 pbar.update(1)

# def main():
#     all_files = []
#     for d in SOURCE_DIRS:
#         all_files.extend(glob.glob(os.path.join(d, "*.jsonl")))

#     print(f"📁 Found {len(all_files)} JSONL files.")

#     # 外层进度条：按文件
#     for input_file in tqdm(all_files, desc="Overall progress"):
#         rel_path = os.path.relpath(input_file, "./dataset/our_dataset")
#         output_file = os.path.join(OUTPUT_BASE_DIR, rel_path)
#         process_file(input_file, output_file, API_KEYS)

#     print("✅ All done! Output saved to:", OUTPUT_BASE_DIR)

# if __name__ == "__main__":
#     main()





import os
import json
import glob
import time
from tqdm import tqdm
from openai import OpenAI, RateLimitError, APIError
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# ================= 配置 =================
SOURCE_DIRS = [
    "./dataset/our_dataset/lmsys_r",
    "./dataset/our_dataset/WildChat_r"
]
OUTPUT_BASE_DIR = "./dataset/our_dataset/rewritten"
MAX_TURNS = 12

# ✅ 替换为你的真实 API Keys（建议至少2个以上）
API_KEYS = [
# "YOUR_API_KEY","YOUR_API_KEY","YOUR_API_KEY","YOUR_API_KEY"
]

os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

# ================= 辅助函数 =================
def group_conversation_into_turns(messages):
    turns = []
    i = 0
    while i < len(messages) and messages[i].get("role") != "user":
        i += 1
    while i < len(messages):
        if messages[i].get("role") == "user":
            user_msg = messages[i].get("content", "")
            if i + 1 < len(messages) and messages[i + 1].get("role") == "assistant":
                assistant_msg = messages[i + 1].get("content", "")
                turns.append({"user": user_msg, "assistant": assistant_msg})
                i += 2
            else:
                return turns, user_msg
        else:
            i += 1
    return turns, None

def extract_for_rewrite(messages, max_turns=5):
    completed_turns, pending_user = group_conversation_into_turns(messages)
    if pending_user is not None or not completed_turns:
        return None, None, None
    last_turn = completed_turns[-1]
    context_turns = completed_turns[:-1][-max_turns:]
    return context_turns, last_turn["user"], last_turn["assistant"]

def rewrite_with_openai(context_turns, last_user, last_assistant, api_keys, max_retries=3):
    history = ""
    for turn in context_turns:
        history += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
    prompt = f'''You are a concise and accurate AI assistant. Improve the assistant's last response based on the full conversation below.

Requirements:
1. Stay strictly grounded in the context—no hallucination.
2. Match the user's intent: be factual if they ask for facts, brief if they want brevity, helpful if they seek advice.
3. Keep it natural and to the point.
4. Fix any inaccuracies, vagueness, or unsafe content in the original.
5. If the original response is wrong or hallucinated, ignore it and generate a correct answer.
6. Only output the improved response. No explanations, prefixes, or markdown.

[Conversation History]
{history}

[Current User Message]
{last_user}

[Original Response]
{last_assistant}

[Improved Response]'''

    for attempt in range(max_retries):
        key = api_keys[attempt % len(api_keys)]
        try:
            client = OpenAI(api_key=key, base_url='https://api.gptsapi.net/v1')  # ✅ 修正：无多余空格
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=2048
            )
            return response.choices[0].message.content.strip()
        except (RateLimitError, APIError) as e:
            time.sleep(2 ** attempt)
        except Exception as e:
            break
    return None

def process_single_line(line, api_keys):
    original_line = line
    line = line.strip()
    if not line:
        return original_line.rstrip('\n')
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return original_line.rstrip('\n')

    if "conversation" not in data:
        return original_line.rstrip('\n')

    messages = data["conversation"]
    context_turns, last_user, last_assistant = extract_for_rewrite(messages, max_turns=MAX_TURNS)

    if None in (context_turns, last_user, last_assistant):
        return original_line.rstrip('\n')

    new_response = rewrite_with_openai(context_turns, last_user, last_assistant, api_keys)
    if new_response is not None:
        data["new_last_turn_response"] = new_response

    return json.dumps(data, ensure_ascii=False)

# ================= 并发处理单个文件（线程池） =================
def process_file_concurrent(input_path, output_path, api_keys, max_workers=12):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(input_path, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()

    total = len(lines)
    results = [None] * total

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(process_single_line, line, api_keys): idx
            for idx, line in enumerate(lines)
        }

        with tqdm(total=total, desc=f"File: {os.path.basename(input_path)}", leave=False) as pbar:
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = lines[idx].rstrip('\n')
                pbar.update(1)

    with open(output_path, 'w', encoding='utf-8') as fout:
        for res in results:
            fout.write(res + "\n")

# ================= 主程序：支持文件级并行 =================
def main():
    all_files = []
    for d in SOURCE_DIRS:
        all_files.extend(glob.glob(os.path.join(d, "*.jsonl")))

    print(f"📁 Found {len(all_files)} JSONL files.")

    # ⚠️ 文件级并发（若机器资源充足，可开启；否则注释掉 ProcessPoolExecutor，用 for 循环）
    with ProcessPoolExecutor(max_workers=2) as executor:  # 控制同时处理的文件数（建议 1~4）
        futures = []
        for input_file in all_files:
            rel_path = os.path.relpath(input_file, "./dataset/our_dataset")
            output_file = os.path.join(OUTPUT_BASE_DIR, rel_path)
            futures.append(
                executor.submit(process_file_concurrent, input_file, output_file, API_KEYS, 12)
            )

        # 显示整体进度
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Overall progress"):
            pass

    print("✅ All done! Output saved to:", OUTPUT_BASE_DIR)

if __name__ == "__main__":
    main()