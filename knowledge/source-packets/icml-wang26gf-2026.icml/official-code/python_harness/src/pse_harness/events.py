"""Events module for event triggering and hook system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger()


class EventType(str, Enum):
    """Types of events that can trigger PSE activation."""
    AGENT_STEP_START = "agent_step_start"
    AGENT_STEP_END = "agent_step_end"
    TOOL_CALL_PRE = "tool_call_pre"
    TOOL_CALL_POST = "tool_call_post"
    ERROR = "error"
    RETRY = "retry"
    PLANNER_DECISION = "planner_decision"
    MEMORY_ACCESS = "memory_access"
    MEMORY_UPDATE = "memory_update"
    ENTITY_REGISTERED = "entity_registered"
    ENTITY_ACCESSED = "entity_accessed"
    CUSTOM = "custom"


@dataclass
class EventSource:
    """Source of an event."""
    source_type: str  # "system", "agent", "tool", "user", "external"
    id: str = ""
    name: str = ""

    @classmethod
    def system(cls) -> EventSource:
        return cls(source_type="system")

    @classmethod
    def agent(cls, agent_id: str, agent_name: str = "") -> EventSource:
        return cls(source_type="agent", id=agent_id, name=agent_name or agent_id)

    @classmethod
    def tool(cls, tool_id: str, tool_name: str = "") -> EventSource:
        return cls(source_type="tool", id=tool_id, name=tool_name or tool_id)

    @classmethod
    def user(cls) -> EventSource:
        return cls(source_type="user")

    @classmethod
    def external(cls, source: str) -> EventSource:
        return cls(source_type="external", id=source, name=source)

    def to_dict(self) -> dict:
        return {
            "source_type": self.source_type,
            "id": self.id,
            "name": self.name,
        }


@dataclass
class Event:
    """Event data structure."""
    id: UUID
    event_type: EventType
    source: EventSource
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[UUID] = None
    parent_event_id: Optional[UUID] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        event_type: EventType,
        source: EventSource,
        payload: dict[str, Any],
        correlation_id: Optional[UUID] = None,
        parent_event_id: Optional[UUID] = None,
    ) -> Event:
        """Create a new event."""
        return cls(
            id=uuid4(),
            event_type=event_type,
            source=source,
            payload=payload,
            correlation_id=correlation_id,
            parent_event_id=parent_event_id,
        )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "event_type": self.event_type.value,
            "source": self.source.to_dict(),
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "parent_event_id": str(self.parent_event_id) if self.parent_event_id else None,
            "metadata": self.metadata,
        }


@dataclass
class HookFilter:
    """Filter for hooks."""
    source_pattern: Optional[str] = None
    payload_filter: Optional[dict[str, Any]] = None
    custom_expression: Optional[str] = None

    def matches(self, event: Event) -> bool:
        """Check if this filter matches an event."""
        if self.source_pattern:
            source_str = f"{event.source.source_type}:{event.source.id}"
            if self.source_pattern not in source_str:
                return False

        if self.payload_filter:
            for key, value in self.payload_filter.items():
                if key not in event.payload or event.payload[key] != value:
                    return False

        return True

    def to_dict(self) -> dict:
        return {
            "source_pattern": self.source_pattern,
            "payload_filter": self.payload_filter,
            "custom_expression": self.custom_expression,
        }


@dataclass
class Hook:
    """Hook definition for event-triggered activation."""
    id: UUID
    name: str
    event_types: list[EventType]
    handler_ref: str
    priority: int = 0
    filter: Optional[HookFilter] = None
    entity_id: Optional[UUID] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    execution_count: int = 0

    def matches_event(self, event: Event) -> bool:
        """Check if this hook should be triggered by an event."""
        if not self.enabled:
            return False

        if event.event_type not in self.event_types:
            return False

        if self.filter and not self.filter.matches(event):
            return False

        return True

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "event_types": [et.value for et in self.event_types],
            "handler_ref": self.handler_ref,
            "priority": self.priority,
            "filter": self.filter.to_dict() if self.filter else None,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "execution_count": self.execution_count,
        }


@dataclass
class HookExecutionResult:
    """Result of hook execution."""
    hook_id: UUID
    event_id: UUID
    success: bool
    duration_ms: float
    output: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "hook_id": str(self.hook_id),
            "event_id": str(self.event_id),
            "success": self.success,
            "duration_ms": self.duration_ms,
            "output": self.output,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


class EventBus:
    """Event bus for managing events and hooks."""

    def __init__(self):
        self._hooks: dict[EventType, list[Hook]] = {}
        self._hook_index: dict[UUID, Hook] = {}
        self._event_history: list[Event] = []
        self._execution_history: list[HookExecutionResult] = []
        self._handlers: dict[str, Callable] = {}
        self._event_count = 0
        self._execution_count = 0

    def register_hook(
        self,
        name: str,
        event_types: list[EventType],
        handler_ref: str,
        priority: int = 0,
        hook_filter: Optional[HookFilter] = None,
        entity_id: Optional[UUID] = None,
    ) -> UUID:
        """Register a new hook."""
        hook = Hook(
            id=uuid4(),
            name=name,
            event_types=event_types,
            handler_ref=handler_ref,
            priority=priority,
            filter=hook_filter,
            entity_id=entity_id,
        )

        # Add to type-indexed map
        for event_type in event_types:
            if event_type not in self._hooks:
                self._hooks[event_type] = []
            self._hooks[event_type].append(hook)
            # Sort by priority (descending)
            self._hooks[event_type].sort(key=lambda h: -h.priority)

        self._hook_index[hook.id] = hook

        logger.debug(
            "Hook registered",
            hook_id=str(hook.id),
            name=name,
            event_types=[et.value for et in event_types],
        )

        return hook.id

    def unregister_hook(self, hook_id: UUID) -> bool:
        """Unregister a hook."""
        if hook_id not in self._hook_index:
            return False

        hook = self._hook_index.pop(hook_id)

        for event_type in hook.event_types:
            if event_type in self._hooks:
                self._hooks[event_type] = [h for h in self._hooks[event_type] if h.id != hook_id]

        logger.debug("Hook unregistered", hook_id=str(hook_id))
        return True

    def register_handler(self, handler_ref: str, handler: Callable) -> None:
        """Register a handler function."""
        self._handlers[handler_ref] = handler

    def emit(self, event: Event) -> list[Hook]:
        """Emit an event and return matching hooks."""
        self._event_count += 1
        self._event_history.append(event)

        matching_hooks = []

        if event.event_type in self._hooks:
            for hook in self._hooks[event.event_type]:
                if hook.matches_event(event):
                    matching_hooks.append(hook)

        logger.debug(
            "Event emitted",
            event_id=str(event.id),
            event_type=event.event_type.value,
            matching_hooks=len(matching_hooks),
        )

        return matching_hooks

    def execute_hooks(self, event: Event, hooks: list[Hook]) -> list[HookExecutionResult]:
        """Execute hooks for an event."""
        results = []

        for hook in hooks:
            start_time = datetime.utcnow()
            success = True
            output = None
            error = None

            try:
                if hook.handler_ref in self._handlers:
                    handler = self._handlers[hook.handler_ref]
                    output = handler(event, hook)
                else:
                    logger.warning(
                        "Handler not found",
                        handler_ref=hook.handler_ref,
                        hook_id=str(hook.id),
                    )
            except Exception as e:
                success = False
                error = str(e)
                logger.error(
                    "Hook execution failed",
                    hook_id=str(hook.id),
                    error=error,
                )

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            result = HookExecutionResult(
                hook_id=hook.id,
                event_id=event.id,
                success=success,
                duration_ms=duration_ms,
                output=output,
                error=error,
            )

            results.append(result)
            self._execution_history.append(result)
            self._execution_count += 1

            # Update hook execution count
            hook.execution_count += 1

        return results

    def get_hook(self, hook_id: UUID) -> Optional[Hook]:
        """Get a hook by ID."""
        return self._hook_index.get(hook_id)

    def list_hooks(self) -> list[Hook]:
        """List all hooks."""
        return list(self._hook_index.values())

    def get_hooks_for_event(self, event_type: EventType) -> list[Hook]:
        """Get all hooks for an event type."""
        return self._hooks.get(event_type, [])

    def get_recent_events(self, limit: int = 100) -> list[Event]:
        """Get recent events."""
        return self._event_history[-limit:]

    def get_execution_history(self, limit: int = 100) -> list[HookExecutionResult]:
        """Get recent execution results."""
        return self._execution_history[-limit:]

    def export(self) -> dict:
        """Export event bus state."""
        return {
            "hooks": [h.to_dict() for h in self._hook_index.values()],
            "recent_events": [e.to_dict() for e in self._event_history[-100:]],
            "recent_executions": [r.to_dict() for r in self._execution_history[-100:]],
            "total_events": self._event_count,
            "total_executions": self._execution_count,
        }

    def clear(self) -> None:
        """Clear all state."""
        self._hooks.clear()
        self._hook_index.clear()
        self._event_history.clear()
        self._execution_history.clear()
        logger.debug("Event bus cleared")
