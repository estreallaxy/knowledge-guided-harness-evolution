#!/usr/bin/env python3
"""
测试 Agent 推理系统是否正常工作
"""
import sys
import os

# Add required paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # agent_inference.py is here
sys.path.insert(0, os.path.join(current_dir, "..", "..", "src", "agent"))
sys.path.insert(0, os.path.join(current_dir, "..", ".."))  # project root

from agent_inference import AgentInferenceManager

def test_agent():
    print("=" * 60)
    print("Testing Agent Inference System")
    print("=" * 60)
    
    # 初始化 Agent
    print("\n[1] Initializing Agent...")
    agent = AgentInferenceManager(
        model_name="qwen2.5-7b",
        local_api_base="http://localhost:8001/v1"
    )
    print("✓ Agent initialized successfully")
    
    # 测试单轮对话
    print("\n[2] Testing single-turn conversation...")
    test_messages_1 = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    response_1 = agent.generate(test_messages_1)
    print(f"User: {test_messages_1[0]['content']}")
    print(f"Agent: {response_1}")
    
    # 测试多轮对话
    print("\n[3] Testing multi-turn conversation...")
    test_messages_2 = [
        {"role": "user", "content": "Tell me about Python programming."},
        {"role": "assistant", "content": "Python is a high-level programming language..."},
        {"role": "user", "content": "What are its main features?"}
    ]
    response_2 = agent.generate(test_messages_2)
    print(f"User: {test_messages_2[-1]['content']}")
    print(f"Agent: {response_2}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nReady to run WildBench evaluation!")
    print("Run: bash run_agent.sh")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_agent()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check:")
        print("1. vLLM service is running at http://localhost:8001/v1")
        print("   Start with: cd ./src/agent && bash llm_start.sh")
        print("2. All dependencies are installed")
        sys.exit(1)

