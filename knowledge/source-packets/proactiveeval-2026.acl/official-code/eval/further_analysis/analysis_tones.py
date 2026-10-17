import json
import os
import glob

def analyze_sounds_like_pattern(base_path):
    """
    analysis the number and percentage of assistant messages containing "sounds like"
    """
    results = {}
    
    # get all model json files
    pattern = os.path.join(base_path, "*", "persuasion_v1.json")
    json_files = glob.glob(pattern)
    
    for json_file in json_files:
        model_name = os.path.basename(os.path.dirname(json_file))
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_conversations = len(data)
            count_with_it_sounds_like = 0
            
            for item in data:
                conversation = item.get('conversation', [])
                
                # find the first assistant message
                first_assistant_msg = None
                for msg in conversation:
                    if msg.get('role') == 'assistant':
                        first_assistant_msg = msg.get('content', '')
                        break
                
                # check if it contains "sounds like" (ignore case)
                if first_assistant_msg and "sounds like" in first_assistant_msg.lower():
                    count_with_it_sounds_like += 1
            
            # calculate the percentage
            percentage = (count_with_it_sounds_like / total_conversations * 100) if total_conversations > 0 else 0
            
            results[model_name] = {
                'total_conversations': total_conversations,
                'count_with_it_sounds_like': count_with_it_sounds_like,
                'percentage': percentage
            }
            
        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {e}")
    
    return results

def print_analysis_results(results):
    print("=" * 80)
    print("Assistant first message containing 'sounds like'")
    print("=" * 80)
    
    if not results:
        print("no analysis results found")
        return
    
    for model_name in sorted(results.keys()):
        data = results[model_name]
        print(f"\nmodel: {model_name}")
        print(f"  total conversations: {data['total_conversations']}")
        print(f"  count of messages containing 'sounds like': {data['count_with_it_sounds_like']}")
        print(f"  percentage: {data['percentage']:.2f}%")
    
    total_all = sum(data['total_conversations'] for data in results.values())
    count_all = sum(data['count_with_it_sounds_like'] for data in results.values())
    percentage_all = (count_all / total_all * 100) if total_all > 0 else 0
    
    print("\n" + "=" * 40)
    print("summary statistics")
    print("=" * 40)
    print(f"total conversations: {total_all}")
    print(f"count of messages containing 'sounds like': {count_all}")
    print(f"percentage: {percentage_all:.2f}%")

# 主函数
def main():
    base_path = "../dialogue_guidance_v1"
    results = analyze_sounds_like_pattern(base_path)
    print_analysis_results(results)
    if results:
        output_file = "tones_analysis_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nanalysis results saved to: {output_file}")

if __name__ == "__main__":
    main()
