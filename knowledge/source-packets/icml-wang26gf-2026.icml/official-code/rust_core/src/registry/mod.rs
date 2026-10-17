//! Registry module for name binding and entity management
//!
//! Implements the core name binding mechanism that allows PSEs to persist
//! through string/symbol registration.

use crate::{NamespaceIsolation, PseError, Result};
use chrono::{DateTime, Utc};
use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use uuid::Uuid;

/// Unique identifier for an entity
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct EntityId(pub Uuid);

impl EntityId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
}

impl Default for EntityId {
    fn default() -> Self {
        Self::new()
    }
}

/// Namespace for entity isolation
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Namespace {
    /// Namespace identifier
    pub id: String,
    /// Parent namespace (for hierarchical isolation)
    pub parent: Option<Box<Namespace>>,
    /// Isolation level
    pub isolation: NamespaceIsolation,
}

impl Namespace {
    pub fn global() -> Self {
        Self {
            id: "global".to_string(),
            parent: None,
            isolation: NamespaceIsolation::None,
        }
    }

    pub fn for_agent(agent_id: &str) -> Self {
        Self {
            id: format!("agent:{}", agent_id),
            parent: Some(Box::new(Self::global())),
            isolation: NamespaceIsolation::PerAgent,
        }
    }

    pub fn for_task(task_id: &str, agent_id: Option<&str>) -> Self {
        Self {
            id: format!("task:{}", task_id),
            parent: agent_id.map(|a| Box::new(Self::for_agent(a))),
            isolation: NamespaceIsolation::PerTask,
        }
    }

    pub fn for_session(session_id: &str) -> Self {
        Self {
            id: format!("session:{}", session_id),
            parent: Some(Box::new(Self::global())),
            isolation: NamespaceIsolation::PerSession,
        }
    }

    pub fn full_path(&self) -> String {
        match &self.parent {
            Some(p) => format!("{}::{}", p.full_path(), self.id),
            None => self.id.clone(),
        }
    }
}

/// Semantic entity that can persist through name binding
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entity {
    /// Unique identifier
    pub id: EntityId,
    /// Bound name (the key for persistence)
    pub name: String,
    /// Namespace this entity belongs to
    pub namespace: Namespace,
    /// Entity payload (behavior definition, state, etc.)
    pub payload: EntityPayload,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    /// Last access timestamp
    pub last_accessed: DateTime<Utc>,
    /// Access count
    pub access_count: u64,
    /// Metadata
    pub metadata: HashMap<String, serde_json::Value>,
    /// Whether this entity is currently active
    pub active: bool,
}

/// Payload types for entities
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EntityPayload {
    /// Tool definition
    Tool {
        description: String,
        parameters: serde_json::Value,
        handler_ref: String,
    },
    /// Hook/callback
    Hook {
        event_type: String,
        handler_ref: String,
        priority: i32,
    },
    /// State/memory
    State {
        data: serde_json::Value,
    },
    /// Policy/constraint
    Policy {
        rules: Vec<PolicyRule>,
    },
    /// Custom entity
    Custom {
        entity_type: String,
        data: serde_json::Value,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyRule {
    pub condition: String,
    pub action: String,
    pub priority: i32,
}

/// Registry for managing named entities
pub struct Registry {
    /// Entity storage by namespace and name
    entities: DashMap<String, DashMap<String, Entity>>,
    /// Global entity index by ID
    entity_index: DashMap<EntityId, (String, String)>,
    /// Default isolation mode
    default_isolation: NamespaceIsolation,
    /// Registration counter
    registration_count: AtomicU64,
    /// Lookup counter
    lookup_count: AtomicU64,
    /// History of registrations for audit
    registration_history: DashMap<u64, RegistrationEvent>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegistrationEvent {
    pub sequence: u64,
    pub timestamp: DateTime<Utc>,
    pub entity_id: EntityId,
    pub name: String,
    pub namespace: String,
    pub event_type: RegistrationEventType,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RegistrationEventType {
    Register,
    Update,
    Unregister,
    Access,
}

impl Registry {
    pub fn new(default_isolation: NamespaceIsolation) -> Self {
        Self {
            entities: DashMap::new(),
            entity_index: DashMap::new(),
            default_isolation,
            registration_count: AtomicU64::new(0),
            lookup_count: AtomicU64::new(0),
            registration_history: DashMap::new(),
        }
    }

    /// Register a new entity with a name binding
    pub fn register(&self, name: String, namespace: Namespace, payload: EntityPayload) -> Result<EntityId> {
        let ns_key = namespace.full_path();

        // Check for existing entity
        if let Some(ns_map) = self.entities.get(&ns_key) {
            if ns_map.contains_key(&name) {
                return Err(PseError::NamespaceConflict(format!(
                    "Entity '{}' already exists in namespace '{}'",
                    name, ns_key
                )));
            }
        }

        let now = Utc::now();
        let entity = Entity {
            id: EntityId::new(),
            name: name.clone(),
            namespace: namespace.clone(),
            payload,
            created_at: now,
            last_accessed: now,
            access_count: 0,
            metadata: HashMap::new(),
            active: true,
        };

        let entity_id = entity.id.clone();

        // Insert into namespace map
        self.entities
            .entry(ns_key.clone())
            .or_insert_with(DashMap::new)
            .insert(name.clone(), entity);

        // Update index
        self.entity_index.insert(entity_id.clone(), (ns_key.clone(), name.clone()));

        // Record history
        let seq = self.registration_count.fetch_add(1, Ordering::SeqCst);
        self.registration_history.insert(seq, RegistrationEvent {
            sequence: seq,
            timestamp: now,
            entity_id: entity_id.clone(),
            name,
            namespace: ns_key,
            event_type: RegistrationEventType::Register,
        });

        Ok(entity_id)
    }

    /// Lookup an entity by name and namespace
    pub fn lookup(&self, name: &str, namespace: &Namespace) -> Option<Entity> {
        let ns_key = namespace.full_path();
        self.lookup_count.fetch_add(1, Ordering::SeqCst);

        // First try exact namespace
        if let Some(ns_map) = self.entities.get(&ns_key) {
            if let Some(entity) = ns_map.get(name) {
                return Some(entity.clone());
            }
        }

        // Then try parent namespaces (hierarchical lookup)
        let mut current_ns = namespace.parent.as_ref();
        while let Some(ns) = current_ns {
            let parent_key = ns.full_path();
            if let Some(ns_map) = self.entities.get(&parent_key) {
                if let Some(entity) = ns_map.get(name) {
                    return Some(entity.clone());
                }
            }
            current_ns = ns.parent.as_ref();
        }

        None
    }

    /// Get entity by ID
    pub fn get_by_id(&self, id: &EntityId) -> Option<Entity> {
        if let Some(location) = self.entity_index.get(id) {
            let (ns_key, name) = location.value();
            if let Some(ns_map) = self.entities.get(ns_key) {
                return ns_map.get(name).map(|e| e.clone());
            }
        }
        None
    }

    /// Update entity access time
    pub fn record_access(&self, id: &EntityId) {
        if let Some(location) = self.entity_index.get(id) {
            let (ns_key, name) = location.value();
            if let Some(ns_map) = self.entities.get(ns_key) {
                if let Some(mut entity) = ns_map.get_mut(name) {
                    entity.last_accessed = Utc::now();
                    entity.access_count += 1;
                }
            }
        }
    }

    /// Unregister an entity
    pub fn unregister(&self, name: &str, namespace: &Namespace) -> Result<()> {
        let ns_key = namespace.full_path();

        if let Some(ns_map) = self.entities.get(&ns_key) {
            if let Some((_, entity)) = ns_map.remove(name) {
                self.entity_index.remove(&entity.id);

                let seq = self.registration_count.fetch_add(1, Ordering::SeqCst);
                self.registration_history.insert(seq, RegistrationEvent {
                    sequence: seq,
                    timestamp: Utc::now(),
                    entity_id: entity.id,
                    name: name.to_string(),
                    namespace: ns_key,
                    event_type: RegistrationEventType::Unregister,
                });

                return Ok(());
            }
        }

        Err(PseError::EntityNotFound(format!(
            "Entity '{}' not found in namespace '{}'",
            name, ns_key
        )))
    }

    /// List all entities in a namespace
    pub fn list_namespace(&self, namespace: &Namespace) -> Vec<Entity> {
        let ns_key = namespace.full_path();

        if let Some(ns_map) = self.entities.get(&ns_key) {
            ns_map.iter().map(|e| e.value().clone()).collect()
        } else {
            Vec::new()
        }
    }

    /// Get all namespaces
    pub fn list_namespaces(&self) -> Vec<String> {
        self.entities.iter().map(|e| e.key().clone()).collect()
    }

    /// Get registration history for audit
    pub fn get_history(&self, start_seq: u64, limit: usize) -> Vec<RegistrationEvent> {
        let mut events: Vec<_> = self.registration_history
            .iter()
            .filter(|e| *e.key() >= start_seq)
            .map(|e| e.value().clone())
            .collect();
        events.sort_by_key(|e| e.sequence);
        events.truncate(limit);
        events
    }

    /// Export registry state for analysis
    pub fn export(&self) -> serde_json::Value {
        let mut namespaces = HashMap::new();

        for ns_entry in self.entities.iter() {
            let entities: Vec<_> = ns_entry.value()
                .iter()
                .map(|e| e.value().clone())
                .collect();
            namespaces.insert(ns_entry.key().clone(), entities);
        }

        serde_json::json!({
            "namespaces": namespaces,
            "total_registrations": self.registration_count.load(Ordering::SeqCst),
            "total_lookups": self.lookup_count.load(Ordering::SeqCst),
        })
    }

    /// Clear all entities (for testing)
    pub fn clear(&self) {
        self.entities.clear();
        self.entity_index.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register_and_lookup() {
        let registry = Registry::new(NamespaceIsolation::None);
        let ns = Namespace::global();

        let id = registry.register(
            "test_tool".to_string(),
            ns.clone(),
            EntityPayload::Tool {
                description: "Test tool".to_string(),
                parameters: serde_json::json!({}),
                handler_ref: "test_handler".to_string(),
            },
        ).unwrap();

        let entity = registry.lookup("test_tool", &ns).unwrap();
        assert_eq!(entity.id, id);
        assert_eq!(entity.name, "test_tool");
    }

    #[test]
    fn test_namespace_isolation() {
        let registry = Registry::new(NamespaceIsolation::PerAgent);

        let ns1 = Namespace::for_agent("agent1");
        let ns2 = Namespace::for_agent("agent2");

        registry.register(
            "tool".to_string(),
            ns1.clone(),
            EntityPayload::State { data: serde_json::json!({"agent": 1}) },
        ).unwrap();

        registry.register(
            "tool".to_string(),
            ns2.clone(),
            EntityPayload::State { data: serde_json::json!({"agent": 2}) },
        ).unwrap();

        let e1 = registry.lookup("tool", &ns1).unwrap();
        let e2 = registry.lookup("tool", &ns2).unwrap();

        assert_ne!(e1.id, e2.id);
    }
}
