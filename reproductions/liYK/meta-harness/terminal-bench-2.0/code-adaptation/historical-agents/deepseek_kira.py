"""DeepSeek V4 Flash via Bailian; share only the provider wiring, not Qwen candidates."""
from pathlib import Path
from agents.qwen_kira import AgentHarness as BailianKiraHarness


class AgentHarness(BailianKiraHarness):
    _policy_path = Path(__file__).resolve().parents[4] / 'configs/deepseek-api.json'
