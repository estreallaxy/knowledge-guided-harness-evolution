//! PSE Core Library
//!
//! Implements the core primitives for Persistent Semantic Entities:
//! - Registry: Name binding and namespace management
//! - Events: Event triggering and hook system
//! - Propagation: Cross-boundary entity propagation

pub mod registry;
pub mod events;
pub mod propagation;
pub mod utils;

#[cfg(feature = "python-bindings")]
pub mod python;

pub use registry::{Registry, Entity, EntityId, Namespace};
pub use events::{EventBus, Event, EventType, Hook, HookId};
pub use propagation::{PropagationGraph, PropagationEdge, PropagationPolicy};

use thiserror::Error;

#[derive(Error, Debug)]
pub enum PseError {
    #[error("Entity not found: {0}")]
    EntityNotFound(String),

    #[error("Namespace conflict: {0}")]
    NamespaceConflict(String),

    #[error("Propagation cycle detected: {path:?}")]
    PropagationCycle { path: Vec<String> },

    #[error("Event handler error: {0}")]
    EventHandlerError(String),

    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    #[error("Policy violation: {0}")]
    PolicyViolation(String),
}

pub type Result<T> = std::result::Result<T, PseError>;

/// Core configuration for PSE system
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct PseConfig {
    /// Enable name binding persistence
    pub enable_name_binding: bool,
    /// Enable event triggering
    pub enable_event_triggering: bool,
    /// Enable cross-boundary propagation
    pub enable_propagation: bool,
    /// Maximum propagation depth
    pub max_propagation_depth: usize,
    /// Namespace isolation mode
    pub namespace_isolation: NamespaceIsolation,
    /// Logging level
    pub log_level: LogLevel,
}

#[derive(Debug, Clone, Copy, serde::Serialize, serde::Deserialize, PartialEq)]
pub enum NamespaceIsolation {
    /// No isolation - global namespace
    None,
    /// Per-agent isolation
    PerAgent,
    /// Per-task isolation
    PerTask,
    /// Per-session isolation
    PerSession,
}

#[derive(Debug, Clone, Copy, serde::Serialize, serde::Deserialize)]
pub enum LogLevel {
    /// Standard logs only
    L0,
    /// Enhanced with registry/event/propagation
    L1,
    /// Full trace with causal links
    L2,
}

impl Default for PseConfig {
    fn default() -> Self {
        Self {
            enable_name_binding: true,
            enable_event_triggering: true,
            enable_propagation: true,
            max_propagation_depth: 10,
            namespace_isolation: NamespaceIsolation::None,
            log_level: LogLevel::L1,
        }
    }
}

/// Main PSE system coordinator
pub struct PseSystem {
    config: PseConfig,
    registry: Registry,
    event_bus: EventBus,
    propagation_graph: PropagationGraph,
}

impl PseSystem {
    pub fn new(config: PseConfig) -> Self {
        Self {
            registry: Registry::new(config.namespace_isolation),
            event_bus: EventBus::new(),
            propagation_graph: PropagationGraph::new(config.max_propagation_depth),
            config,
        }
    }

    pub fn config(&self) -> &PseConfig {
        &self.config
    }

    pub fn registry(&self) -> &Registry {
        &self.registry
    }

    pub fn registry_mut(&mut self) -> &mut Registry {
        &mut self.registry
    }

    pub fn event_bus(&self) -> &EventBus {
        &self.event_bus
    }

    pub fn event_bus_mut(&mut self) -> &mut EventBus {
        &mut self.event_bus
    }

    pub fn propagation_graph(&self) -> &PropagationGraph {
        &self.propagation_graph
    }

    pub fn propagation_graph_mut(&mut self) -> &mut PropagationGraph {
        &mut self.propagation_graph
    }

    /// Export system state for analysis
    pub fn export_state(&self) -> serde_json::Value {
        serde_json::json!({
            "config": self.config,
            "registry": self.registry.export(),
            "events": self.event_bus.export(),
            "propagation": self.propagation_graph.export(),
        })
    }
}
