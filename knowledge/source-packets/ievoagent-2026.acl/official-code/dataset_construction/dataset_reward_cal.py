from src.agent.utils.reward import *
def process_jsonl_file(filepath: str, output_filepath: str, device: str="cuda"):
    """
    读取 JSONL 文件，计算每一轮对话的 Reward，并将结果写入新的 JSONL 文件。
    """
    processed_lines = 0
    
    print(f"--- 🚀 Start processing: {filepath}")
    
    # 第一次迭代，快速获取总行数，以便 tqdm 正确显示进度
    # 使用 'rb' 模式并按字节查找换行符是最快的计数方式
    try:
        with open(filepath, 'rb') as f:
            total_lines = sum(1 for line in f if line.strip())
    except FileNotFoundError:
        print(f"Error: Input file not found at {filepath}")
        return
    except Exception as e:
        print(f"Error reading file line count: {e}")
        return

    # 主处理循环
    with jsonlines.open(filepath, mode='r') as reader, \
         jsonlines.open(output_filepath, mode='w') as writer:
        
        # 使用 tqdm 包装 reader，以显示进度条
        for aline in tqdm(reader, total=total_lines, desc="Processing Lines"):
            
            # 创建一个用于存储新 Reward 的列表
            rewards = []
            ufb_rs = []
            info_rs = []
            
            # 迭代对话轮次 (使用 .get() 以防止键不存在)
            num_turns = aline.get("turn", 0)
            
            for i in range(num_turns):
                try:
                    # 提取当前轮次的对话数据
                    # History 是 [0, 1, 2, ..., i*2 - 1] 之间的所有对话元素
                    history = aline["conversation"][:i*2] 
                    # Input 是 i*2 索引的元素
                    input_text = aline["conversation"][i*2]["content"]
                    # Response 是 i*2 + 1 索引的元素
                    response_text = aline["conversation"][i*2+1]["content"]
                    
                    # 使用 .get() 确保键在数据中缺失时不会崩溃
                    ufb_types = aline["user_feedback_category"]
                    error_types = aline["llm_response_type"]
                    if len(ufb_types)!=num_turns or len(error_types)!=num_turns:
                        raise ValueError(f"Length mismatch in feedback or error type lists at turn {i}")
                        break
                    ufb_type = ufb_types[i]
                    error_type = error_types[i]
                    if ufb_type is None or error_type is None:
                        raise ValueError(f"Missing feedback or error type at turn {i}")
                        break
                    # 运行 compute_reward (使用您的函数)
                    ufb_r, info_r = compute_reward(input_text, response_text, ufb_type, error_type, history = history)
                    ufb_rs.append(ufb_r)
                    info_rs.append(info_r)
                    rewards.append(ufb_r+info_r)
                    
                except Exception as e:
                    # rewards.append(0.0) 
                    print("error", e, processed_lines)
                    break
                    # return       
            # 将新的 Reward 列表添加到当前 JSON 对象中
            # 命名为 'mi_sim_rewards' 以区分其他可能的奖励
            if len(rewards)==num_turns:
                aline["rewards"] = rewards
                aline["ufb_rewards"] = ufb_rs
                aline["info_rewards"] = info_rs
                aline["average_r"] = sum(rewards)/len(rewards)
                
                # 写入结果到新的 JSONL 文件
                writer.write(aline)
                processed_lines += 1
            
    print(f"\nProcessing finished. Total lines processed: {processed_lines}")
    print(f"Output saved to: {output_filepath}")


# =================================================================
# 主入口和配置
# =================================================================

if __name__ == '__main__':
    # --- 文件路径配置 ---
    for i in range(10):
        INPUT_FILEPATH = f"./dataset/our_dataset/WildChat/WildChat-1M-geq8_part_{i}.jsonl"
        OUTPUT_FILEPATH = f"./dataset/our_dataset/WildChat_r/WildChat-1M-geq8_part_{i}_r.jsonl"

        # INPUT_FILEPATH = f"./dataset/our_dataset/lmsys/lmsys-chat-1m-geq8_part_{i}.jsonl"
        # OUTPUT_FILEPATH = f"./dataset/our_dataset/lmsys_r/lmsys-chat-1m-geq8_part_{i}_r.jsonl"
        os.makedirs(os.path.dirname(OUTPUT_FILEPATH), exist_ok=True)
        process_jsonl_file(INPUT_FILEPATH, OUTPUT_FILEPATH)