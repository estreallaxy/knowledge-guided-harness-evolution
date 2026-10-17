"""Registry module for name binding and entity management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger()


class NamespaceIsolation(str, Enum):
    """Namespace isolation modes."""
    NONE = "none"           # Global namespace
    PER_AGENT = "per_agent" # Per-agent isolation
    PER_TASK = "per_task"   # Per-task isolation
    PER_SESSION = "per_session"  # Per-session isolation


@dataclass
class Namespace:
    """Namespace for entity isolation."""
    id: str
    isolation: NamespaceIsolation = NamespaceIsolation.NONE
    parent: Optional[Namespace] = None

    @classmethod
    def global_ns(cls) -> Namespace:
        """Create a global namespace."""
        return cls(id="global", isolation=NamespaceIsolation.NONE)

    @classmethod
    def for_agent(cls, agent_id: str) -> Namespace:
        """Create a namespace for an agent."""
        return cls(
            id=f"agent:{agent_id}",
            isolation=NamespaceIsolation.PER_AGENT,
            parent=cls.global_ns(),
        )

    @classmethod
    def for_task(cls, task_id: str, agent_id: Optional[str] = None) -> Namespace:
        """Create a namespace for a task."""
        parent = cls.for_agent(agent_id) if agent_id else cls.global_ns()
        return cls(
            id=f"task:{task_id}",
            isolation=NamespaceIsolation.PER_TASK,
            parent=parent,
        )

    @classmethod
    def for_session(cls, session_id: str) -> Namespace:
        """Create a namespace for a session."""
        return cls(
            id=f"session:{session_id}",
            isolation=NamespaceIsolation.PER_SESSION,
            parent=cls.global_ns(),
        )

    def full_path(self) -> str:
        """Get the full namespace path."""
        if self.parent:
            return f"{self.parent.full_path()}::{self.id}"
        return self.id

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "isolation": self.isolation.value,
            "parent": self.parent.to_dict() if self.parent else None,
            "full_path": self.full_path(),
        }


@dataclass
class EntityPayload:
    """Payload for an entity."""
    payload_type: str
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def tool(cls, description: str, handler_ref: str, parameters: Optional[dict] = None) -> EntityPayload:
        """Create a tool payload."""
        return cls(
            payload_type="tool",
            data={
                "description": description,
                "handler_ref": handler_ref,
                "parameters": parameters or {},
            },
        )

    @classmethod
    def hook(cls, event_type: str, handler_ref: str, priority: int = 0) -> EntityPayload:
        """Create a hook payload."""
        return cls(
            payload_type="hook",
            data={
                "event_type": event_type,
                "handler_ref": handler_ref,
                "priority": priority,
            },
        )

    @classmethod
    def state(cls, data: dict[str, Any]) -> EntityPayload:
        """Create a state payload."""
        return cls(payload_type="state", data={"state": data})

    @classmethod
    def policy(cls, rules: list[dict[str, Any]]) -> EntityPayload:
        """Create a policy payload."""
        return cls(payload_type="policy", data={"rules": rules})

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "payload_type": self.payload_type,
            "data": self.data,
        }


@dataclass
class Entity:
    """Semantic entity that can persist through name binding."""
    id: UUID
    name: str
    namespace: Namespace
    payload: EntityPayload
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    active: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "namespace": self.namespace.to_dict(),
            "payload": self.payload.to_dict(),
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "metadata": self.metadata,
            "active": self.active,
        }


@dataclass
class RegistrationEvent:
    """Event recording a registration action."""
    sequence: int
    timestamp: datetime
    entity_id: UUID
    name: str
    namespace: str
    event_type: str  # "register", "update", "unregister", "access"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "sequence": self.sequence,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": str(self.entity_id),
            "name": self.name,
            "namespace": self.namespace,
            "event_type": self.event_type,
        }


class Registry:
    """Registry for managing named entities."""

    def __init__(self, default_isolation: NamespaceIsolation = NamespaceIsolation.NONE):
        self._entities: dict[str, dict[str, Entity]] = {}  # namespace -> name -> entity
        self._entity_index: dict[UUID, tuple[str, str]] = {}  # id -> (namespace, name)
        self._default_isolation = default_isolation
        self._registration_count = 0
        self._lookup_count = 0
        self._history: list[RegistrationEvent] = []

    def register(
        self,
        name: str,
        namespace: Namespace,
        payload: EntityPayload,
        metadata: Optional[dict[str, Any]] = None,
    ) -> UUID:
        """Register a new entity with a name binding."""
        ns_key = namespace.full_path()

        # Check for existing entity
        if ns_key in self._entities and name in self._entities[ns_key]:
            raise ValueError(f"Entity '{name}' already exists in namespace '{ns_key}'")

        # Create entity
        entity = Entity(
            id=uuid4(),
            name=name,
            namespace=namespace,
            payload=payload,
            metadata=metadata or {},
        )

        # Store entity
        if ns_key not in self._entities:
            self._entities[ns_key] = {}
        self._entities[ns_key][name] = entity
        self._entity_index[entity.id] = (ns_key, name)

        # Record history
        self._registration_count += 1
        self._history.append(RegistrationEvent(
            sequence=self._registration_count,
            timestamp=datetime.utcnow(),
            entity_id=entity.id,
            name=name,
            namespace=ns_key,
            event_type="register",
        ))

        logger.debug(
            "Entity registered",
            entity_id=str(entity.id),
            name=name,
            namespace=ns_key,
            payload_type=payload.payload_type,
        )

        return entity.id

    def lookup(self, name: str, namespace: Namespace) -> Optional[Entity]:
        """Look up an entity by name and namespace."""
        self._lookup_count += 1
        ns_key = namespace.full_path()

        # Try exact namespace
        if ns_key in self._entities and name in self._entities[ns_key]:
            entity = self._entities[ns_key][name]
            self._record_access(entity)
            return entity

        # Try parent namespaces (hierarchical lookup)
        current_ns = namespace.parent
        while current_ns:
            parent_key = current_ns.full_path()
            if parent_key in self._entities and name in self._entities[parent_key]:
                entity = self._entities[parent_key][name]
                self._record_access(entity)
                return entity
            current_ns = current_ns.parent

        return None

    def get_by_id(self, entity_id: UUID) -> Optional[Entity]:
        """Get entity by ID."""
        if entity_id in self._entity_index:
            ns_key, name = self._entity_index[entity_id]
            if ns_key in self._entities and name in self._entities[ns_key]:
                return self._entities[ns_key][name]
        return None

    def _record_access(self, entity: Entity) -> None:
        """Record an access to an entity."""
        entity.last_accessed = datetime.utcnow()
        entity.access_count += 1

        self._history.append(RegistrationEvent(
            sequence=len(self._history) + 1,
            timestamp=datetime.utcnow(),
            entity_id=entity.id,
            name=entity.name,
            namespace=entity.namespace.full_path(),
            event_type="access",
        ))

    def unregister(self, name: str, namespace: Namespace) -> bool:
        """Unregister an entity."""
        ns_key = namespace.full_path()

        if ns_key in self._entities and name in self._entities[ns_key]:
            entity = self._entities[ns_key].pop(name)
            del self._entity_index[entity.id]

            self._history.append(RegistrationEvent(
                sequence=len(self._history) + 1,
                timestamp=datetime.utcnow(),
                entity_id=entity.id,
                name=name,
                namespace=ns_key,
                event_type="unregister",
            ))

            logger.debug("Entity unregistered", entity_id=str(entity.id), name=name)
            return True

        return False

    def list_namespace(self, namespace: Namespace) -> list[Entity]:
        """List all entities in a namespace."""
        ns_key = namespace.full_path()
        if ns_key in self._entities:
            return list(self._entities[ns_key].values())
        return []

    def list_all_namespaces(self) -> list[str]:
        """List all namespace keys."""
        return list(self._entities.keys())

    def get_history(self, start_seq: int = 0, limit: int = 100) -> list[RegistrationEvent]:
        """Get registration history."""
        filtered = [e for e in self._history if e.sequence >= start_seq]
        return filtered[:limit]

    def export(self) -> dict:
        """Export registry state."""
        namespaces = {}
        for ns_key, entities in self._entities.items():
            namespaces[ns_key] = [e.to_dict() for e in entities.values()]

        return {
            "namespaces": namespaces,
            "total_registrations": self._registration_count,
            "total_lookups": self._lookup_count,
            "history_length": len(self._history),
        }

    def clear(self) -> None:
        """Clear all entities."""
        self._entities.clear()
        self._entity_index.clear()
        self._history.clear()
        logger.debug("Registry cleared")
