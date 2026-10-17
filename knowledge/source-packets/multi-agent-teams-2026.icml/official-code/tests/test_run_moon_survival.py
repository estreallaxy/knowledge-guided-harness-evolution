"""Tests for moon survival experiment runner."""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BackendConfig(BaseModel):
    """Configuration for a single backend."""

    provider: str = Field(description="Backend provider (openai, anthropic, gemini)")
    model: Optional[str] = Field(default=None, description="Model name (uses provider default if None)")
    temperature: Optional[float] = Field(default=None, description="Sampling temperature")


class MoonSurvivalConfig(BaseModel):
    """Configuration for Moon Survival experiment (for testing)."""

    max_rounds: int = Field(ge=1, description="Maximum collaboration rounds")
    expert_info_mode: str = Field(default="none", description="Expert information distribution mode: 'none', 'full', 'single_expert', or 'distributed'")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

    # Single backend mode
    backend: Optional[BackendConfig] = Field(default=None, description="Single backend config (all agents)")
    num_agents: Optional[int] = Field(default=None, ge=1, le=15, description="Number of agents (single backend mode)")

    # W&B configuration
    wandb_project: str = Field(default="moon-survival", description="W&B project name")
    wandb_entity: Optional[str] = Field(default=None, description="W&B entity/team name")

    def generate_run_name(self, total_agents: int, backend_summary: str) -> str:
        """Generate unique experiment run name from config and timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.expert_info_mode == "full":
            info_str = "full-info"
        elif self.expert_info_mode == "single_expert":
            info_str = "single-expert"
        elif self.expert_info_mode == "distributed":
            info_str = "distributed"
        else:  # none
            info_str = "no-info"
        hidden_info_str = info_str
        seed_str = f"_s{self.seed}" if self.seed is not None else ""
        return f"moon-survival_n{total_agents}_r{self.max_rounds}_{hidden_info_str}_{backend_summary}{seed_str}_{timestamp}"


def test_generate_run_name_format():
    """Test that run name follows expected format."""
    config = MoonSurvivalConfig(
        num_agents=5,
        max_rounds=10,
        expert_info_mode="distributed",
        backend=BackendConfig(provider="openai", model="gpt-4o"),
        seed=42
    )

    run_name = config.generate_run_name(total_agents=5, backend_summary="openai-gpt-4o")

    # Check format: moon-survival_n5_r10_distributed_openai-gpt-4o_s42_YYYYMMDD_HHMMSS
    pattern = r"moon-survival_n5_r10_distributed_openai-gpt-4o_s42_\d{8}_\d{6}"
    assert re.match(pattern, run_name), f"Run name '{run_name}' doesn't match expected pattern"


def test_generate_run_name_no_hidden_info():
    """Test run name with hidden info disabled."""
    config = MoonSurvivalConfig(
        num_agents=3,
        max_rounds=5,
        expert_info_mode="none",
        backend=BackendConfig(provider="openai", model="gpt-4o-mini")
    )

    run_name = config.generate_run_name(total_agents=3, backend_summary="openai-gpt-4o-mini")

    assert "no-info" in run_name
    assert "n3" in run_name
    assert "r5" in run_name


def test_generate_run_name_includes_timestamp():
    """Test that run name includes current timestamp."""
    config = MoonSurvivalConfig(
        num_agents=3,
        max_rounds=3,
        expert_info_mode="distributed",
        backend=BackendConfig(provider="openai", model="gpt-4o")
    )

    before = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = config.generate_run_name(total_agents=3, backend_summary="openai-gpt-4o")
    after = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract timestamp from run name
    timestamp_match = re.search(r"(\d{8}_\d{6})$", run_name)
    assert timestamp_match, "Run name should end with timestamp"
    timestamp = timestamp_match.group(1)

    # Timestamp should be between before and after
    assert before <= timestamp <= after


def test_generate_run_name_uniqueness():
    """Test that sequential run names are unique due to timestamp."""
    config = MoonSurvivalConfig(
        num_agents=3,
        max_rounds=3,
        expert_info_mode="distributed",
        backend=BackendConfig(provider="openai", model="gpt-4o")
    )

    import time
    name1 = config.generate_run_name(total_agents=3, backend_summary="openai-gpt-4o")
    time.sleep(1.1)
    name2 = config.generate_run_name(total_agents=3, backend_summary="openai-gpt-4o")

    assert name1 != name2, "Sequential run names should be unique"


def test_generate_run_name_different_configs():
    """Test that different configs produce different run names."""
    config1 = MoonSurvivalConfig(
        num_agents=3,
        max_rounds=3,
        expert_info_mode="distributed",
        backend=BackendConfig(provider="openai", model="gpt-4o")
    )

    config2 = MoonSurvivalConfig(
        num_agents=5,
        max_rounds=3,
        expert_info_mode="distributed",
        backend=BackendConfig(provider="openai", model="gpt-4o")
    )

    name1 = config1.generate_run_name(total_agents=3, backend_summary="openai-gpt-4o")
    name2 = config2.generate_run_name(total_agents=5, backend_summary="openai-gpt-4o")

    # Different agent counts should be reflected
    assert "n3" in name1
    assert "n5" in name2
    assert name1[:name1.rfind("_")] != name2[:name2.rfind("_")]