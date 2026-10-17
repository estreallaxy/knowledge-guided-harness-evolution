"""Propagation module for cross-boundary entity propagation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4
from collections import deque

import structlog

logger = structlog.get_logger()


class PropagationEdgeType(str, Enum):
    """Types of propagation edges."""
    DIRECT_CALL = "direct_call"
    EVENT_TRIGGERED = "event_triggered"
    NAMESPACE_SHARING = "namespace_sharing"
    NESTED_TOOL_CALL = "nested_tool_call"
    AGENT_DELEGATION = "agent_delegation"
    SHARED_STATE = "shared_state"


class PropagationNodeType(str, Enum):
    """Types of nodes in propagation graph."""
    AGENT = "agent"
    TOOL = "tool"
    HOOK = "hook"
    ENTITY = "entity"
    SESSION = "session"
    EXTERNAL = "external"


@dataclass
class PropagationNode:
    """Node in the propagation graph."""
    id: UUID
    name: str
    node_type: PropagationNodeType
    entity_id: Optional[UUID] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "node_type": self.node_type.value,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class PropagationEdge:
    """Edge in the propagation graph."""
    id: UUID
    source: UUID
    target: UUID
    edge_type: PropagationEdgeType
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    occurrence_count: int = 1
    correlation_ids: list[UUID] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "source": str(self.source),
            "target": str(self.target),
            "edge_type": self.edge_type.value,
            "weight": self.weight,
            "created_at": self.created_at.isoformat(),
            "occurrence_count": self.occurrence_count,
            "correlation_ids": [str(c) for c in self.correlation_ids],
        }


@dataclass
class PropagationEvent:
    """Event recording a propagation occurrence."""
    id: UUID
    source: UUID
    target: UUID
    edge_type: PropagationEdgeType
    timestamp: datetime
    payload: Optional[dict[str, Any]] = None
    depth: int = 0
    root_event_id: Optional[UUID] = None

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "source": str(self.source),
            "target": str(self.target),
            "edge_type": self.edge_type.value,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "depth": self.depth,
            "root_event_id": str(self.root_event_id) if self.root_event_id else None,
        }


@dataclass
class PropagationPolicy:
    """Policy for controlling propagation."""
    max_depth: int = 10
    allowed_edge_types: set[PropagationEdgeType] = field(default_factory=lambda: {
        PropagationEdgeType.DIRECT_CALL,
        PropagationEdgeType.EVENT_TRIGGERED,
        PropagationEdgeType.NESTED_TOOL_CALL,
    })
    blocked_pairs: set[tuple[UUID, UUID]] = field(default_factory=set)
    require_authorization: bool = False
    detect_cycles: bool = True

    def allows_edge_type(self, edge_type: PropagationEdgeType) -> bool:
        return edge_type in self.allowed_edge_types

    def is_pair_blocked(self, source: UUID, target: UUID) -> bool:
        return (source, target) in self.blocked_pairs


class PropagationGraph:
    """Graph for tracking entity propagation."""

    def __init__(self, max_depth: int = 10):
        self._nodes: dict[UUID, PropagationNode] = {}
        self._edges: dict[UUID, PropagationEdge] = {}
        self._adjacency: dict[UUID, list[UUID]] = {}  # source -> [edge_ids]
        self._reverse_adjacency: dict[UUID, list[UUID]] = {}  # target -> [edge_ids]
        self._entity_node_map: dict[UUID, UUID] = {}  # entity_id -> node_id
        self._history: list[PropagationEvent] = []
        self._policy = PropagationPolicy(max_depth=max_depth)
        self._max_depth = max_depth

    def add_node(
        self,
        name: str,
        node_type: PropagationNodeType,
        entity_id: Optional[UUID] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> UUID:
        """Add a node to the graph."""
        node = PropagationNode(
            id=uuid4(),
            name=name,
            node_type=node_type,
            entity_id=entity_id,
            metadata=metadata or {},
        )

        self._nodes[node.id] = node
        self._adjacency[node.id] = []
        self._reverse_adjacency[node.id] = []

        if entity_id:
            self._entity_node_map[entity_id] = node.id

        logger.debug(
            "Propagation node added",
            node_id=str(node.id),
            name=name,
            node_type=node_type.value,
        )

        return node.id

    def add_edge(
        self,
        source: UUID,
        target: UUID,
        edge_type: PropagationEdgeType,
        weight: float = 1.0,
    ) -> UUID:
        """Add an edge (propagation path) to the graph."""
        # Validate nodes exist
        if source not in self._nodes:
            raise ValueError(f"Source node {source} not found")
        if target not in self._nodes:
            raise ValueError(f"Target node {target} not found")

        # Check policy
        if not self._policy.allows_edge_type(edge_type):
            raise ValueError(f"Edge type {edge_type} not allowed by policy")

        if self._policy.is_pair_blocked(source, target):
            raise ValueError(f"Propagation from {source} to {target} is blocked")

        # Check for cycles
        if self._policy.detect_cycles and self._would_create_cycle(source, target):
            path = self._get_path(target, source)
            raise ValueError(f"Adding edge would create cycle: {' -> '.join(str(p) for p in path)}")

        # Create edge
        edge = PropagationEdge(
            id=uuid4(),
            source=source,
            target=target,
            edge_type=edge_type,
            weight=weight,
        )

        self._edges[edge.id] = edge
        self._adjacency[source].append(edge.id)
        self._reverse_adjacency[target].append(edge.id)

        logger.debug(
            "Propagation edge added",
            edge_id=str(edge.id),
            source=str(source),
            target=str(target),
            edge_type=edge_type.value,
        )

        return edge.id

    def _would_create_cycle(self, source: UUID, target: UUID) -> bool:
        """Check if adding an edge would create a cycle."""
        # BFS from target to see if we can reach source
        visited = set()
        queue = deque([target])

        while queue:
            current = queue.popleft()
            if current == source:
                return True

            if current in visited:
                continue
            visited.add(current)

            for edge_id in self._adjacency.get(current, []):
                edge = self._edges[edge_id]
                queue.append(edge.target)

        return False

    def _get_path(self, from_node: UUID, to_node: UUID) -> list[UUID]:
        """Get path between two nodes using BFS."""
        visited = set()
        queue = deque([(from_node, [from_node])])

        while queue:
            current, path = queue.popleft()
            if current == to_node:
                return path

            if current in visited:
                continue
            visited.add(current)

            for edge_id in self._adjacency.get(current, []):
                edge = self._edges[edge_id]
                queue.append((edge.target, path + [edge.target]))

        return []

    def record_propagation(
        self,
        source: UUID,
        target: UUID,
        edge_type: PropagationEdgeType,
        payload: Optional[dict[str, Any]] = None,
        depth: int = 0,
        root_event_id: Optional[UUID] = None,
    ) -> UUID:
        """Record a propagation event."""
        event = PropagationEvent(
            id=uuid4(),
            source=source,
            target=target,
            edge_type=edge_type,
            timestamp=datetime.utcnow(),
            payload=payload,
            depth=depth,
            root_event_id=root_event_id,
        )

        self._history.append(event)

        # Update edge occurrence count if edge exists
        for edge_id in self._adjacency.get(source, []):
            edge = self._edges[edge_id]
            if edge.target == target and edge.edge_type == edge_type:
                edge.occurrence_count += 1
                break

        logger.debug(
            "Propagation recorded",
            event_id=str(event.id),
            source=str(source),
            target=str(target),
            depth=depth,
        )

        return event.id

    def get_reachable_nodes(
        self,
        source: UUID,
        max_depth: Optional[int] = None,
    ) -> list[tuple[UUID, int]]:
        """Get all nodes reachable from a source within max depth."""
        max_d = max_depth or self._max_depth
        reachable = []
        visited = set()
        queue = deque([(source, 0)])

        while queue:
            current, depth = queue.popleft()

            if depth > max_d:
                continue

            if current in visited:
                continue
            visited.add(current)

            if depth > 0:
                reachable.append((current, depth))

            for edge_id in self._adjacency.get(current, []):
                edge = self._edges[edge_id]
                queue.append((edge.target, depth + 1))

        return reachable

    def get_all_paths(self, source: UUID, target: UUID) -> list[list[UUID]]:
        """Get all paths from source to target."""
        paths = []
        self._dfs_paths(source, target, [source], set(), paths)
        return paths

    def _dfs_paths(
        self,
        current: UUID,
        target: UUID,
        path: list[UUID],
        visited: set[UUID],
        paths: list[list[UUID]],
    ) -> None:
        """DFS helper for finding all paths."""
        if current == target:
            paths.append(list(path))
            return

        visited.add(current)

        for edge_id in self._adjacency.get(current, []):
            edge = self._edges[edge_id]
            if edge.target not in visited:
                path.append(edge.target)
                self._dfs_paths(edge.target, target, path, visited, paths)
                path.pop()

        visited.remove(current)

    def get_node(self, node_id: UUID) -> Optional[PropagationNode]:
        """Get a node by ID."""
        return self._nodes.get(node_id)

    def get_node_by_entity(self, entity_id: UUID) -> Optional[PropagationNode]:
        """Get a node by entity ID."""
        node_id = self._entity_node_map.get(entity_id)
        if node_id:
            return self._nodes.get(node_id)
        return None

    def get_edge(self, edge_id: UUID) -> Optional[PropagationEdge]:
        """Get an edge by ID."""
        return self._edges.get(edge_id)

    def get_outgoing_edges(self, node_id: UUID) -> list[PropagationEdge]:
        """Get all outgoing edges from a node."""
        edge_ids = self._adjacency.get(node_id, [])
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]

    def get_incoming_edges(self, node_id: UUID) -> list[PropagationEdge]:
        """Get all incoming edges to a node."""
        edge_ids = self._reverse_adjacency.get(node_id, [])
        return [self._edges[eid] for eid in edge_ids if eid in self._edges]

    def get_history(self, limit: int = 100) -> list[PropagationEvent]:
        """Get recent propagation history."""
        return self._history[-limit:]

    def set_policy(self, policy: PropagationPolicy) -> None:
        """Set the propagation policy."""
        self._policy = policy

    def get_policy(self) -> PropagationPolicy:
        """Get the current policy."""
        return self._policy

    def export(self) -> dict:
        """Export graph state."""
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges.values()],
            "history": [h.to_dict() for h in self._history[-100:]],
            "total_propagations": len(self._history),
        }

    def to_dot(self) -> str:
        """Export as DOT format for visualization."""
        lines = ["digraph propagation {", "  rankdir=LR;", "  node [shape=box];", ""]

        # Node colors by type
        colors = {
            PropagationNodeType.AGENT: "lightblue",
            PropagationNodeType.TOOL: "lightgreen",
            PropagationNodeType.HOOK: "lightyellow",
            PropagationNodeType.ENTITY: "lightpink",
            PropagationNodeType.SESSION: "lightgray",
            PropagationNodeType.EXTERNAL: "white",
        }

        # Add nodes
        for node in self._nodes.values():
            color = colors.get(node.node_type, "white")
            lines.append(
                f'  "{node.id}" [label="{node.name}\\n({node.node_type.value})" '
                f'style=filled fillcolor={color}];'
            )

        lines.append("")

        # Edge styles by type
        styles = {
            PropagationEdgeType.DIRECT_CALL: "solid",
            PropagationEdgeType.EVENT_TRIGGERED: "dashed",
            PropagationEdgeType.NAMESPACE_SHARING: "dotted",
            PropagationEdgeType.NESTED_TOOL_CALL: "bold",
            PropagationEdgeType.AGENT_DELEGATION: "bold",
            PropagationEdgeType.SHARED_STATE: "dotted",
        }

        # Add edges
        for edge in self._edges.values():
            style = styles.get(edge.edge_type, "solid")
            lines.append(
                f'  "{edge.source}" -> "{edge.target}" '
                f'[label="{edge.edge_type.value}" style={style}];'
            )

        lines.append("}")
        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all state."""
        self._nodes.clear()
        self._edges.clear()
        self._adjacency.clear()
        self._reverse_adjacency.clear()
        self._entity_node_map.clear()
        self._history.clear()
        logger.debug("Propagation graph cleared")
