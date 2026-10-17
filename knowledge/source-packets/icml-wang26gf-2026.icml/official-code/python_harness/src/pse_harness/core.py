"""Core PSE system configuration and coordination."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
import structlog

from .registry import Registry, Namespace, NamespaceIsolation
from .events import EventBus
from .propagation import PropagationGraph


logger = structlog.get_logger()


class LogLevel(str, Enum):
    """Logging verbosity levels."""
    L0 = "L0"  # Standard logs only
    L1 = "L1"  # Enhanced with registry/event/propagation
    L2 = "L2"  # Full trace with causal links


class PseConfig(BaseModel):
    """Configuration for PSE system."""

    # Core PSE mechanisms (for ablation studies)
    enable_name_binding: bool = Field(default=True, description="Enable name binding persistence")
    enable_event_triggering: bool = Field(default=True, description="Enable event triggering")
    enable_propagation: bool = Field(default=True, description="Enable cross-boundary propagation")

    # Propagation limits
    max_propagation_depth: int = Field(default=10, description="Maximum propagation depth")

    # Namespace isolation
    namespace_isolation: NamespaceIsolation = Field(
        default=NamespaceIsolation.NONE,
        description="Namespace isolation mode"
    )

    # Logging
    log_level: LogLevel = Field(default=LogLevel.L1, description="Logging verbosity")

    # Mitigation controls
    enable_registry_lifecycle: bool = Field(default=False, description="Enable registry lifecycle management")
    enable_event_audit: bool = Field(default=False, description="Enable event hook audit")
    enable_propagation_limits: bool = Field(default=False, description="Enable propagation restrictions")

    def to_ablation_key(self) -> str:
        """Generate a key representing the current ablation configuration."""
        return f"nb{int(self.enable_name_binding)}_et{int(self.enable_event_triggering)}_pr{int(self.enable_propagation)}"

    @classmethod
    def from_ablation_key(cls, key: str) -> "PseConfig":
        """Create config from ablation key."""
        parts = key.split("_")
        return cls(
            enable_name_binding=parts[0] == "nb1",
            enable_event_triggering=parts[1] == "et1",
            enable_propagation=parts[2] == "pr1",
        )

    @classmethod
    def all_ablation_configs(cls) -> list["PseConfig"]:
        """Generate all 2x2x2 ablation configurations."""
        configs = []
        for nb in [False, True]:
            for et in [False, True]:
                for pr in [False, True]:
                    configs.append(cls(
                        enable_name_binding=nb,
                        enable_event_triggering=et,
                        enable_propagation=pr,
                    ))
        return configs


class ExperimentConfig(BaseModel):
    """Configuration for an experiment run."""

    # Experiment identification
    experiment_id: str = Field(default_factory=lambda: str(uuid4()))
    experiment_name: str = Field(default="unnamed")
    description: str = Field(default="")

    # PSE configuration
    pse_config: PseConfig = Field(default_factory=PseConfig)

    # Model configuration
    model_provider: str = Field(default="openai", description="Model provider: openai, anthropic, local")
    model_name: str = Field(default="gpt-4o-mini", description="Model identifier")
    temperature: float = Field(default=0.0, description="Sampling temperature")
    max_tokens: int = Field(default=4096, description="Maximum tokens per response")

    # Experiment parameters
    num_runs: int = Field(default=20, description="Number of runs per task")
    task_family: str = Field(default="tool_intensive", description="Task family to use")
    num_tasks: int = Field(default=100, description="Number of tasks to run")

    # Paths
    output_dir: Path = Field(default=Path("data/results"))
    log_dir: Path = Field(default=Path("data/logs"))

    # Random seed
    seed: Optional[int] = Field(default=42, description="Random seed for reproducibility")

    def get_output_path(self) -> Path:
        """Get the output path for this experiment."""
        return self.output_dir / self.experiment_id

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode="json")

    def save(self, path: Optional[Path] = None) -> Path:
        """Save configuration to file."""
        if path is None:
            path = self.get_output_path() / "config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        return path

    @classmethod
    def load(cls, path: Path) -> "ExperimentConfig":
        """Load configuration from file."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)


class PseSystem:
    """Main PSE system coordinator."""

    def __init__(self, config: Optional[PseConfig] = None):
        self.config = config or PseConfig()
        self._registry = Registry(self.config.namespace_isolation)
        self._event_bus = EventBus()
        self._propagation_graph = PropagationGraph(self.config.max_propagation_depth)
        self._trace_id = str(uuid4())
        self._created_at = datetime.utcnow()

        logger.info(
            "PSE system initialized",
            trace_id=self._trace_id,
            config=self.config.model_dump(),
        )

    @property
    def registry(self) -> Registry:
        """Get the entity registry."""
        return self._registry

    @property
    def event_bus(self) -> EventBus:
        """Get the event bus."""
        return self._event_bus

    @property
    def propagation_graph(self) -> PropagationGraph:
        """Get the propagation graph."""
        return self._propagation_graph

    @property
    def trace_id(self) -> str:
        """Get the trace ID for this system instance."""
        return self._trace_id

    def is_name_binding_enabled(self) -> bool:
        """Check if name binding is enabled."""
        return self.config.enable_name_binding

    def is_event_triggering_enabled(self) -> bool:
        """Check if event triggering is enabled."""
        return self.config.enable_event_triggering

    def is_propagation_enabled(self) -> bool:
        """Check if propagation is enabled."""
        return self.config.enable_propagation

    def export_state(self) -> dict[str, Any]:
        """Export full system state for analysis."""
        return {
            "trace_id": self._trace_id,
            "created_at": self._created_at.isoformat(),
            "config": self.config.model_dump(),
            "registry": self._registry.export(),
            "events": self._event_bus.export(),
            "propagation": self._propagation_graph.export(),
        }

    def save_state(self, path: Path) -> None:
        """Save system state to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.export_state(), f, indent=2, default=str)
        logger.info("System state saved", path=str(path))

    def reset(self) -> None:
        """Reset the system state."""
        self._registry.clear()
        self._event_bus.clear()
        self._propagation_graph.clear()
        self._trace_id = str(uuid4())
        logger.info("System reset", new_trace_id=self._trace_id)
