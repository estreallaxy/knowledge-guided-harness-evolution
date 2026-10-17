//! Propagation module for cross-boundary entity propagation
//!
//! Implements the propagation mechanism that allows PSEs to spread
//! across tool/agent/session boundaries.

use crate::{EntityId, PseError, Result};
use chrono::{DateTime, Utc};
use dashmap::DashMap;
use petgraph::graph::{DiGraph, NodeIndex};
use petgraph::visit::EdgeRef;
use petgraph::Direction;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet, VecDeque};
use std::sync::atomic::{AtomicU64, Ordering};
use uuid::Uuid;

/// Propagation edge types
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum PropagationEdgeType {
    /// Direct invocation
    DirectCall,
    /// Event-triggered propagation
    EventTriggered,
    /// Implicit through shared namespace
    NamespaceSharing,
    /// Through nested tool calls
    NestedToolCall,
    /// Through agent delegation
    AgentDelegation,
    /// Through shared memory/state
    SharedState,
}

/// Node in the propagation graph
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PropagationNode {
    /// Node ID
    pub id: Uuid,
    /// Associated entity ID (if any)
    pub entity_id: Option<EntityId>,
    /// Node type
    pub node_type: PropagationNodeType,
    /// Node name/identifier
    pub name: String,
    /// Metadata
    pub metadata: HashMap<String, serde_json::Value>,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum PropagationNodeType {
    Agent,
    Tool,
    Hook,
    Entity,
    Session,
    External,
}

/// Edge in the propagation graph
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PropagationEdge {
    /// Edge ID
    pub id: Uuid,
    /// Edge type
    pub edge_type: PropagationEdgeType,
    /// Weight/strength
    pub weight: f64,
    /// Timestamp when edge was created
    pub created_at: DateTime<Utc>,
    /// Number of times this propagation occurred
    pub occurrence_count: u64,
    /// Correlation IDs for tracing
    pub correlation_ids: Vec<Uuid>,
}

/// Propagation event for audit trail
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PropagationEvent {
    /// Event ID
    pub id: Uuid,
    /// Source node
    pub source: Uuid,
    /// Target node
    pub target: Uuid,
    /// Edge type
    pub edge_type: PropagationEdgeType,
    /// Timestamp
    pub timestamp: DateTime<Utc>,
    /// Payload that propagated
    pub payload: Option<serde_json::Value>,
    /// Depth in propagation chain
    pub depth: usize,
    /// Root cause event
    pub root_event_id: Option<Uuid>,
}

/// Policy for controlling propagation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PropagationPolicy {
    /// Maximum propagation depth
    pub max_depth: usize,
    /// Allowed edge types
    pub allowed_edge_types: HashSet<PropagationEdgeType>,
    /// Blocked node pairs
    pub blocked_pairs: HashSet<(Uuid, Uuid)>,
    /// Require explicit authorization
    pub require_authorization: bool,
    /// Enable cycle detection
    pub detect_cycles: bool,
}

impl Default for PropagationPolicy {
    fn default() -> Self {
        let mut allowed = HashSet::new();
        allowed.insert(PropagationEdgeType::DirectCall);
        allowed.insert(PropagationEdgeType::EventTriggered);
        allowed.insert(PropagationEdgeType::NestedToolCall);

        Self {
            max_depth: 10,
            allowed_edge_types: allowed,
            blocked_pairs: HashSet::new(),
            require_authorization: false,
            detect_cycles: true,
        }
    }
}

/// Propagation graph for tracking entity propagation
pub struct PropagationGraph {
    /// Internal graph structure
    graph: DiGraph<PropagationNode, PropagationEdge>,
    /// Node index by UUID
    node_index: DashMap<Uuid, NodeIndex>,
    /// Entity to node mapping
    entity_node_map: DashMap<EntityId, Uuid>,
    /// Propagation history
    propagation_history: DashMap<u64, PropagationEvent>,
    /// Event counter
    event_count: AtomicU64,
    /// Current policy
    policy: PropagationPolicy,
    /// Maximum depth
    max_depth: usize,
}

impl PropagationGraph {
    pub fn new(max_depth: usize) -> Self {
        Self {
            graph: DiGraph::new(),
            node_index: DashMap::new(),
            entity_node_map: DashMap::new(),
            propagation_history: DashMap::new(),
            event_count: AtomicU64::new(0),
            policy: PropagationPolicy {
                max_depth,
                ..Default::default()
            },
            max_depth,
        }
    }

    /// Add a node to the graph
    pub fn add_node(&mut self, node: PropagationNode) -> Uuid {
        let node_id = node.id;

        if let Some(entity_id) = &node.entity_id {
            self.entity_node_map.insert(entity_id.clone(), node_id);
        }

        let idx = self.graph.add_node(node);
        self.node_index.insert(node_id, idx);
        node_id
    }

    /// Add an edge (propagation path)
    pub fn add_edge(
        &mut self,
        source: Uuid,
        target: Uuid,
        edge_type: PropagationEdgeType,
    ) -> Result<Uuid> {
        // Check policy
        if !self.policy.allowed_edge_types.contains(&edge_type) {
            return Err(PseError::PolicyViolation(format!(
                "Edge type {:?} not allowed by policy",
                edge_type
            )));
        }

        if self.policy.blocked_pairs.contains(&(source, target)) {
            return Err(PseError::PolicyViolation(format!(
                "Propagation from {:?} to {:?} is blocked",
                source, target
            )));
        }

        let source_idx = self.node_index.get(&source)
            .ok_or_else(|| PseError::EntityNotFound(format!("Node {:?} not found", source)))?
            .clone();
        let target_idx = self.node_index.get(&target)
            .ok_or_else(|| PseError::EntityNotFound(format!("Node {:?} not found", target)))?
            .clone();

        // Check for cycles if enabled
        if self.policy.detect_cycles {
            if self.would_create_cycle(source_idx, target_idx) {
                return Err(PseError::PropagationCycle {
                    path: self.get_path_to_node(target_idx, source_idx),
                });
            }
        }

        let edge = PropagationEdge {
            id: Uuid::new_v4(),
            edge_type,
            weight: 1.0,
            created_at: Utc::now(),
            occurrence_count: 1,
            correlation_ids: Vec::new(),
        };

        let edge_id = edge.id;
        self.graph.add_edge(source_idx, target_idx, edge);

        Ok(edge_id)
    }

    /// Check if adding an edge would create a cycle
    fn would_create_cycle(&self, source: NodeIndex, target: NodeIndex) -> bool {
        // Check if there's a path from target to source
        let mut visited = HashSet::new();
        let mut queue = VecDeque::new();
        queue.push_back(target);

        while let Some(current) = queue.pop_front() {
            if current == source {
                return true;
            }

            if visited.insert(current) {
                for edge in self.graph.edges_directed(current, Direction::Outgoing) {
                    queue.push_back(edge.target());
                }
            }
        }

        false
    }

    /// Get path between nodes
    fn get_path_to_node(&self, from: NodeIndex, to: NodeIndex) -> Vec<String> {
        let mut path = Vec::new();
        let mut visited = HashSet::new();
        let mut queue = VecDeque::new();
        let mut parent: HashMap<NodeIndex, NodeIndex> = HashMap::new();

        queue.push_back(from);
        visited.insert(from);

        while let Some(current) = queue.pop_front() {
            if current == to {
                // Reconstruct path
                let mut node = to;
                while let Some(&p) = parent.get(&node) {
                    if let Some(n) = self.graph.node_weight(node) {
                        path.push(n.name.clone());
                    }
                    node = p;
                }
                if let Some(n) = self.graph.node_weight(from) {
                    path.push(n.name.clone());
                }
                path.reverse();
                return path;
            }

            for edge in self.graph.edges_directed(current, Direction::Outgoing) {
                let next = edge.target();
                if visited.insert(next) {
                    parent.insert(next, current);
                    queue.push_back(next);
                }
            }
        }

        path
    }

    /// Record a propagation event
    pub fn record_propagation(
        &self,
        source: Uuid,
        target: Uuid,
        edge_type: PropagationEdgeType,
        payload: Option<serde_json::Value>,
        depth: usize,
        root_event_id: Option<Uuid>,
    ) {
        let event = PropagationEvent {
            id: Uuid::new_v4(),
            source,
            target,
            edge_type,
            timestamp: Utc::now(),
            payload,
            depth,
            root_event_id,
        };

        let seq = self.event_count.fetch_add(1, Ordering::SeqCst);
        self.propagation_history.insert(seq, event);
    }

    /// Get all nodes reachable from a source within max depth
    pub fn get_reachable_nodes(&self, source: Uuid, max_depth: Option<usize>) -> Vec<(Uuid, usize)> {
        let max_d = max_depth.unwrap_or(self.max_depth);
        let mut reachable = Vec::new();

        if let Some(source_idx) = self.node_index.get(&source) {
            let mut visited = HashSet::new();
            let mut queue = VecDeque::new();
            queue.push_back((*source_idx, 0usize));

            while let Some((current, depth)) = queue.pop_front() {
                if depth > max_d {
                    continue;
                }

                if visited.insert(current) {
                    if let Some(node) = self.graph.node_weight(current) {
                        if depth > 0 {
                            reachable.push((node.id, depth));
                        }
                    }

                    for edge in self.graph.edges_directed(current, Direction::Outgoing) {
                        queue.push_back((edge.target(), depth + 1));
                    }
                }
            }
        }

        reachable
    }

    /// Get all paths from source to target
    pub fn get_all_paths(&self, source: Uuid, target: Uuid) -> Vec<Vec<Uuid>> {
        let mut paths = Vec::new();

        if let (Some(source_idx), Some(target_idx)) = (
            self.node_index.get(&source).map(|r| *r),
            self.node_index.get(&target).map(|r| *r),
        ) {
            let mut current_path = vec![source];
            let mut visited = HashSet::new();
            self.dfs_paths(*source_idx.value(), *target_idx.value(), &mut current_path, &mut visited, &mut paths);
        }

        paths
    }

    fn dfs_paths(
        &self,
        current: NodeIndex,
        target: NodeIndex,
        current_path: &mut Vec<Uuid>,
        visited: &mut HashSet<NodeIndex>,
        paths: &mut Vec<Vec<Uuid>>,
    ) {
        if current == target {
            paths.push(current_path.clone());
            return;
        }

        visited.insert(current);

        for edge in self.graph.edges_directed(current, Direction::Outgoing) {
            let next = edge.target();
            if !visited.contains(&next) {
                if let Some(node) = self.graph.node_weight(next) {
                    current_path.push(node.id);
                    self.dfs_paths(next, target, current_path, visited, paths);
                    current_path.pop();
                }
            }
        }

        visited.remove(&current);
    }

    /// Get node by ID
    pub fn get_node(&self, id: &Uuid) -> Option<PropagationNode> {
        self.node_index.get(id)
            .and_then(|idx| self.graph.node_weight(*idx).cloned())
    }

    /// Get edges from a node
    pub fn get_outgoing_edges(&self, source: &Uuid) -> Vec<(Uuid, PropagationEdge)> {
        let mut edges = Vec::new();

        if let Some(source_idx) = self.node_index.get(source) {
            for edge in self.graph.edges_directed(*source_idx, Direction::Outgoing) {
                if let Some(target_node) = self.graph.node_weight(edge.target()) {
                    edges.push((target_node.id, edge.weight().clone()));
                }
            }
        }

        edges
    }

    /// Get propagation history
    pub fn get_history(&self, limit: usize) -> Vec<PropagationEvent> {
        let mut events: Vec<_> = self.propagation_history.iter()
            .map(|e| e.value().clone())
            .collect();
        events.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        events.truncate(limit);
        events
    }

    /// Set policy
    pub fn set_policy(&mut self, policy: PropagationPolicy) {
        self.policy = policy;
    }

    /// Get current policy
    pub fn policy(&self) -> &PropagationPolicy {
        &self.policy
    }

    /// Export graph for analysis
    pub fn export(&self) -> serde_json::Value {
        let nodes: Vec<_> = self.graph.node_weights().cloned().collect();

        let edges: Vec<_> = self.graph.edge_references()
            .filter_map(|e| {
                let source = self.graph.node_weight(e.source())?;
                let target = self.graph.node_weight(e.target())?;
                Some(serde_json::json!({
                    "source": source.id,
                    "target": target.id,
                    "edge": e.weight(),
                }))
            })
            .collect();

        let history = self.get_history(100);

        serde_json::json!({
            "nodes": nodes,
            "edges": edges,
            "history": history,
            "policy": self.policy,
            "total_propagations": self.event_count.load(Ordering::SeqCst),
        })
    }

    /// Export as DOT format for visualization
    pub fn to_dot(&self) -> String {
        let mut dot = String::from("digraph propagation {\n");
        dot.push_str("  rankdir=LR;\n");
        dot.push_str("  node [shape=box];\n\n");

        // Add nodes
        for node in self.graph.node_weights() {
            let color = match node.node_type {
                PropagationNodeType::Agent => "lightblue",
                PropagationNodeType::Tool => "lightgreen",
                PropagationNodeType::Hook => "lightyellow",
                PropagationNodeType::Entity => "lightpink",
                PropagationNodeType::Session => "lightgray",
                PropagationNodeType::External => "white",
            };
            dot.push_str(&format!(
                "  \"{}\" [label=\"{}\\n({:?})\" style=filled fillcolor={}];\n",
                node.id, node.name, node.node_type, color
            ));
        }

        dot.push_str("\n");

        // Add edges
        for edge in self.graph.edge_references() {
            if let (Some(source), Some(target)) = (
                self.graph.node_weight(edge.source()),
                self.graph.node_weight(edge.target()),
            ) {
                let style = match edge.weight().edge_type {
                    PropagationEdgeType::DirectCall => "solid",
                    PropagationEdgeType::EventTriggered => "dashed",
                    PropagationEdgeType::NamespaceSharing => "dotted",
                    _ => "bold",
                };
                dot.push_str(&format!(
                    "  \"{}\" -> \"{}\" [label=\"{:?}\" style={}];\n",
                    source.id, target.id, edge.weight().edge_type, style
                ));
            }
        }

        dot.push_str("}\n");
        dot
    }

    /// Clear graph (for testing)
    pub fn clear(&mut self) {
        self.graph.clear();
        self.node_index.clear();
        self.entity_node_map.clear();
        self.propagation_history.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_propagation_graph() {
        let mut graph = PropagationGraph::new(10);

        let node1 = PropagationNode {
            id: Uuid::new_v4(),
            entity_id: None,
            node_type: PropagationNodeType::Agent,
            name: "agent1".to_string(),
            metadata: HashMap::new(),
            created_at: Utc::now(),
        };

        let node2 = PropagationNode {
            id: Uuid::new_v4(),
            entity_id: None,
            node_type: PropagationNodeType::Tool,
            name: "tool1".to_string(),
            metadata: HashMap::new(),
            created_at: Utc::now(),
        };

        let id1 = graph.add_node(node1);
        let id2 = graph.add_node(node2);

        graph.add_edge(id1, id2, PropagationEdgeType::DirectCall).unwrap();

        let reachable = graph.get_reachable_nodes(id1, None);
        assert_eq!(reachable.len(), 1);
        assert_eq!(reachable[0].0, id2);
    }

    #[test]
    fn test_cycle_detection() {
        let mut graph = PropagationGraph::new(10);

        let node1 = PropagationNode {
            id: Uuid::new_v4(),
            entity_id: None,
            node_type: PropagationNodeType::Agent,
            name: "agent1".to_string(),
            metadata: HashMap::new(),
            created_at: Utc::now(),
        };

        let node2 = PropagationNode {
            id: Uuid::new_v4(),
            entity_id: None,
            node_type: PropagationNodeType::Tool,
            name: "tool1".to_string(),
            metadata: HashMap::new(),
            created_at: Utc::now(),
        };

        let id1 = graph.add_node(node1);
        let id2 = graph.add_node(node2);

        graph.add_edge(id1, id2, PropagationEdgeType::DirectCall).unwrap();

        // This should fail due to cycle
        let result = graph.add_edge(id2, id1, PropagationEdgeType::DirectCall);
        assert!(matches!(result, Err(PseError::PropagationCycle { .. })));
    }
}
