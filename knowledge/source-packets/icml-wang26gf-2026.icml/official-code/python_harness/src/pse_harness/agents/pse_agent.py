"""PSE-aware agent that integrates with the PSE system."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
import structlog

from .base import (
    AgentConfig,
    AgentResponse,
    AgentStatus,
    AgentStep,
    BaseAgent,
    Tool,
    ToolCall,
)
from .openai_agent import OpenAIAgent
from ..core import PseSystem, PseConfig
from ..registry import Entity, EntityPayload, Namespace
from ..events import Event, EventType, EventSource, Hook
from ..propagation import PropagationNodeType, PropagationEdgeType

logger = structlog.get_logger()


class PseAgentConfig(AgentConfig):
    """Configuration for PSE-aware agent."""
    pse_config: PseConfig = Field(default_factory=PseConfig)
    track_propagation: bool = Field(default=True)
    emit_events: bool = Field(default=True)


class PseAgent(BaseAgent):
    """Agent that integrates with the PSE system for tracking and experiments."""

    def __init__(
        self,
        config: PseAgentConfig,
        tools: Optional[list[Tool]] = None,
        api_key: Optional[str] = None,
        pse_system: Optional[PseSystem] = None,
    ):
        super().__init__(config, tools)
        self.pse_config = config.pse_config

        # Initialize or use provided PSE system
        self.pse_system = pse_system or PseSystem(config.pse_config)

        # Create underlying agent
        self._inner_agent = OpenAIAgent(config, tools, api_key)

        # Agent node ID in propagation graph
        self._node_id: Optional[UUID] = None

        # Track registered entities
        self._registered_entities: dict[str, UUID] = {}

        # Initialize agent in PSE system
        self._init_pse()

    def _init_pse(self) -> None:
        """Initialize agent in PSE system."""
        # Add agent node to propagation graph
        if self.pse_config.enable_propagation:
            self._node_id = self.pse_system.propagation_graph.add_node(
                name=self.config.agent_name,
                node_type=PropagationNodeType.AGENT,
                metadata={"agent_id": self.config.agent_id},
            )

        # Register tools as entities
        if self.pse_config.enable_name_binding:
            namespace = Namespace.for_agent(self.config.agent_id)
            for tool in self.tools:
                entity_id = self.pse_system.registry.register(
                    name=f"tool:{tool.name}",
                    namespace=namespace,
                    payload=EntityPayload.tool(
                        description=tool.description,
                        handler_ref=f"{self.config.agent_id}:{tool.name}",
                    ),
                )
                self._registered_entities[tool.name] = entity_id

                # Add tool node to propagation graph
                if self.pse_config.enable_propagation:
                    tool_node_id = self.pse_system.propagation_graph.add_node(
                        name=tool.name,
                        node_type=PropagationNodeType.TOOL,
                        entity_id=entity_id,
                    )
                    # Add edge from agent to tool
                    self.pse_system.propagation_graph.add_edge(
                        self._node_id,
                        tool_node_id,
                        PropagationEdgeType.DIRECT_CALL,
                    )

        logger.info(
            "PSE agent initialized",
            agent_id=self.config.agent_id,
            node_id=str(self._node_id) if self._node_id else None,
            registered_entities=len(self._registered_entities),
        )

    def _emit_event(self, event_type: EventType, payload: dict[str, Any]) -> list[Hook]:
        """Emit an event and return triggered hooks."""
        if not self.pse_config.enable_event_triggering:
            return []

        event = Event.create(
            event_type=event_type,
            source=EventSource.agent(self.config.agent_id, self.config.agent_name),
            payload=payload,
        )

        return self.pse_system.event_bus.emit(event)

    def _record_propagation(
        self,
        target_node_id: UUID,
        edge_type: PropagationEdgeType,
        payload: Optional[dict[str, Any]] = None,
        depth: int = 0,
    ) -> None:
        """Record a propagation event."""
        if not self.pse_config.enable_propagation or not self._node_id:
            return

        self.pse_system.propagation_graph.record_propagation(
            source=self._node_id,
            target=target_node_id,
            edge_type=edge_type,
            payload=payload,
            depth=depth,
        )

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt."""
        self._inner_agent.set_system_prompt(prompt)

    def reset_conversation(self) -> None:
        """Reset the conversation."""
        self._inner_agent.reset_conversation()

    async def run(self, task: str) -> AgentResponse:
        """Run the agent on a task with PSE tracking."""
        run_id = uuid4()
        start_time = datetime.utcnow()

        logger.info(
            "PSE agent run started",
            run_id=str(run_id),
            task=task[:100],
            agent_id=self.config.agent_id,
        )

        # Emit step start event
        triggered_hooks = self._emit_event(
            EventType.AGENT_STEP_START,
            {"task": task, "run_id": str(run_id)},
        )

        # Execute hooks if any
        if triggered_hooks:
            self.pse_system.event_bus.execute_hooks(
                Event.create(
                    EventType.AGENT_STEP_START,
                    EventSource.agent(self.config.agent_id),
                    {"task": task},
                ),
                triggered_hooks,
            )

        # Run inner agent
        response = await self._inner_agent.run(task)

        # Track tool calls in PSE system
        for step in response.steps:
            for tool_call in step.tool_calls:
                # Emit tool call events
                self._emit_event(
                    EventType.TOOL_CALL_PRE,
                    {
                        "tool_name": tool_call.name,
                        "arguments": tool_call.arguments,
                    },
                )

                self._emit_event(
                    EventType.TOOL_CALL_POST,
                    {
                        "tool_name": tool_call.name,
                        "result": tool_call.result,
                        "error": tool_call.error,
                    },
                )

                # Record access to tool entity
                if tool_call.name in self._registered_entities:
                    entity_id = self._registered_entities[tool_call.name]
                    self.pse_system.registry._record_access(
                        self.pse_system.registry.get_by_id(entity_id)
                    )

        # Emit step end event
        self._emit_event(
            EventType.AGENT_STEP_END,
            {
                "run_id": str(run_id),
                "status": response.status.value,
                "num_steps": len(response.steps),
            },
        )

        # Add PSE metadata to response
        response.metadata["pse_trace_id"] = self.pse_system.trace_id
        response.metadata["pse_node_id"] = str(self._node_id) if self._node_id else None
        response.metadata["pse_config"] = self.pse_config.model_dump()

        self._run_history.append(response)

        logger.info(
            "PSE agent run completed",
            run_id=str(run_id),
            status=response.status.value,
            num_tool_calls=len(response.tool_call_sequence),
        )

        return response

    async def step(self, input_text: str) -> AgentStep:
        """Execute a single step with PSE tracking."""
        self._emit_event(
            EventType.AGENT_STEP_START,
            {"input": input_text},
        )

        step = await self._inner_agent.step(input_text)

        for tool_call in step.tool_calls:
            self._emit_event(
                EventType.TOOL_CALL_POST,
                {
                    "tool_name": tool_call.name,
                    "result": tool_call.result,
                },
            )

        self._emit_event(
            EventType.AGENT_STEP_END,
            {"output": step.output},
        )

        return step

    def get_pse_state(self) -> dict[str, Any]:
        """Get current PSE system state."""
        return self.pse_system.export_state()

    def get_propagation_graph_dot(self) -> str:
        """Get propagation graph in DOT format."""
        return self.pse_system.propagation_graph.to_dot()


class MultiAgentPseSystem:
    """Coordinator for multiple PSE-aware agents."""

    def __init__(self, pse_config: Optional[PseConfig] = None):
        self.pse_config = pse_config or PseConfig()
        self.pse_system = PseSystem(self.pse_config)
        self._agents: dict[str, PseAgent] = {}

    def create_agent(
        self,
        name: str,
        tools: Optional[list[Tool]] = None,
        api_key: Optional[str] = None,
    ) -> PseAgent:
        """Create a new PSE-aware agent."""
        config = PseAgentConfig(
            agent_id=str(uuid4()),
            agent_name=name,
            pse_config=self.pse_config,
        )

        agent = PseAgent(
            config=config,
            tools=tools,
            api_key=api_key,
            pse_system=self.pse_system,
        )

        self._agents[name] = agent
        return agent

    def get_agent(self, name: str) -> Optional[PseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        """List all agent names."""
        return list(self._agents.keys())

    async def run_task_with_delegation(
        self,
        task: str,
        primary_agent: str,
        delegate_agents: Optional[list[str]] = None,
    ) -> dict[str, AgentResponse]:
        """Run a task with potential delegation to other agents."""
        results = {}

        primary = self._agents.get(primary_agent)
        if not primary:
            raise ValueError(f"Primary agent '{primary_agent}' not found")

        # Run primary agent
        results[primary_agent] = await primary.run(task)

        # Record delegation in propagation graph
        if delegate_agents and self.pse_config.enable_propagation:
            for delegate_name in delegate_agents:
                delegate = self._agents.get(delegate_name)
                if delegate and delegate._node_id and primary._node_id:
                    self.pse_system.propagation_graph.add_edge(
                        primary._node_id,
                        delegate._node_id,
                        PropagationEdgeType.AGENT_DELEGATION,
                    )

        return results

    def get_system_state(self) -> dict[str, Any]:
        """Get full system state."""
        return {
            "pse_system": self.pse_system.export_state(),
            "agents": {
                name: {
                    "config": agent.config.model_dump(),
                    "run_count": len(agent.get_run_history()),
                }
                for name, agent in self._agents.items()
            },
        }
