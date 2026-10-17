//! Python bindings for PSE Core
//!
//! Provides PyO3 bindings to use the PSE core library from Python.

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use crate::{
    Entity, EntityPayload, Event, EventSource, EventType, Hook, HookId,
    Namespace, NamespaceIsolation, PropagationEdgeType, PropagationNode,
    PropagationNodeType, PseConfig, PseSystem,
};

/// Python wrapper for PseConfig
#[pyclass(name = "PseConfig")]
#[derive(Clone)]
pub struct PyPseConfig {
    inner: PseConfig,
}

#[pymethods]
impl PyPseConfig {
    #[new]
    #[pyo3(signature = (
        enable_name_binding = true,
        enable_event_triggering = true,
        enable_propagation = true,
        max_propagation_depth = 10,
        namespace_isolation = "none"
    ))]
    fn new(
        enable_name_binding: bool,
        enable_event_triggering: bool,
        enable_propagation: bool,
        max_propagation_depth: usize,
        namespace_isolation: &str,
    ) -> Self {
        let isolation = match namespace_isolation {
            "per_agent" => NamespaceIsolation::PerAgent,
            "per_task" => NamespaceIsolation::PerTask,
            "per_session" => NamespaceIsolation::PerSession,
            _ => NamespaceIsolation::None,
        };

        Self {
            inner: PseConfig {
                enable_name_binding,
                enable_event_triggering,
                enable_propagation,
                max_propagation_depth,
                namespace_isolation: isolation,
                ..Default::default()
            },
        }
    }

    fn to_dict(&self, py: Python<'_>) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        dict.set_item("enable_name_binding", self.inner.enable_name_binding)?;
        dict.set_item("enable_event_triggering", self.inner.enable_event_triggering)?;
        dict.set_item("enable_propagation", self.inner.enable_propagation)?;
        dict.set_item("max_propagation_depth", self.inner.max_propagation_depth)?;
        Ok(dict.into())
    }
}

/// Python wrapper for PSE System
#[pyclass(name = "PseSystem")]
pub struct PyPseSystem {
    inner: Arc<RwLock<PseSystem>>,
}

#[pymethods]
impl PyPseSystem {
    #[new]
    #[pyo3(signature = (config = None))]
    fn new(config: Option<PyPseConfig>) -> Self {
        let cfg = config.map(|c| c.inner).unwrap_or_default();
        Self {
            inner: Arc::new(RwLock::new(PseSystem::new(cfg))),
        }
    }

    /// Register an entity with name binding
    #[pyo3(signature = (name, payload_type, payload_data, namespace = None))]
    fn register_entity(
        &self,
        name: String,
        payload_type: String,
        payload_data: &Bound<'_, PyDict>,
        namespace: Option<String>,
    ) -> PyResult<String> {
        let system = self.inner.read().unwrap();

        let ns = match namespace {
            Some(ref s) if s.starts_with("agent:") => Namespace::for_agent(&s[6..]),
            Some(ref s) if s.starts_with("task:") => Namespace::for_task(&s[5..], None),
            Some(ref s) if s.starts_with("session:") => Namespace::for_session(&s[8..]),
            _ => Namespace::global(),
        };

        let payload = match payload_type.as_str() {
            "tool" => {
                let description: String = payload_data
                    .get_item("description")?
                    .map(|v| v.extract())
                    .transpose()?
                    .unwrap_or_default();
                let handler_ref: String = payload_data
                    .get_item("handler_ref")?
                    .map(|v| v.extract())
                    .transpose()?
                    .unwrap_or_default();

                EntityPayload::Tool {
                    description,
                    parameters: serde_json::json!({}),
                    handler_ref,
                }
            }
            "hook" => {
                let event_type: String = payload_data
                    .get_item("event_type")?
                    .map(|v| v.extract())
                    .transpose()?
                    .unwrap_or_default();
                let handler_ref: String = payload_data
                    .get_item("handler_ref")?
                    .map(|v| v.extract())
                    .transpose()?
                    .unwrap_or_default();
                let priority: i32 = payload_data
                    .get_item("priority")?
                    .map(|v| v.extract())
                    .transpose()?
                    .unwrap_or(0);

                EntityPayload::Hook {
                    event_type,
                    handler_ref,
                    priority,
                }
            }
            "state" => {
                let data_str: String = payload_data
                    .get_item("data")?
                    .map(|v| v.extract())
                    .transpose()?
                    .unwrap_or_else(|| "{}".to_string());
                let data: serde_json::Value = serde_json::from_str(&data_str)
                    .unwrap_or(serde_json::json!({}));

                EntityPayload::State { data }
            }
            _ => {
                let data_str: String = payload_data
                    .get_item("data")?
                    .map(|v| v.extract())
                    .transpose()?
                    .unwrap_or_else(|| "{}".to_string());
                let data: serde_json::Value = serde_json::from_str(&data_str)
                    .unwrap_or(serde_json::json!({}));

                EntityPayload::Custom {
                    entity_type: payload_type,
                    data,
                }
            }
        };

        match system.registry().register(name, ns, payload) {
            Ok(id) => Ok(id.0.to_string()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                e.to_string(),
            )),
        }
    }

    /// Look up an entity by name
    #[pyo3(signature = (name, namespace = None))]
    fn lookup_entity(&self, name: String, namespace: Option<String>) -> PyResult<Option<String>> {
        let system = self.inner.read().unwrap();

        let ns = match namespace {
            Some(ref s) if s.starts_with("agent:") => Namespace::for_agent(&s[6..]),
            Some(ref s) if s.starts_with("task:") => Namespace::for_task(&s[5..], None),
            Some(ref s) if s.starts_with("session:") => Namespace::for_session(&s[8..]),
            _ => Namespace::global(),
        };

        match system.registry().lookup(&name, &ns) {
            Some(entity) => {
                let json = serde_json::to_string(&entity).unwrap_or_default();
                Ok(Some(json))
            }
            None => Ok(None),
        }
    }

    /// Register a hook for event-triggered activation
    fn register_hook(
        &self,
        name: String,
        event_types: Vec<String>,
        handler_ref: String,
        priority: Option<i32>,
    ) -> String {
        let system = self.inner.read().unwrap();

        let events: Vec<EventType> = event_types
            .iter()
            .map(|s| match s.as_str() {
                "agent_step_start" => EventType::AgentStepStart,
                "agent_step_end" => EventType::AgentStepEnd,
                "tool_call_pre" => EventType::ToolCallPre,
                "tool_call_post" => EventType::ToolCallPost,
                "error" => EventType::Error,
                "retry" => EventType::Retry,
                _ => EventType::Custom(s.clone()),
            })
            .collect();

        let hook = Hook {
            id: HookId::new(),
            name,
            event_types: events,
            filter: None,
            priority: priority.unwrap_or(0),
            entity_id: None,
            handler_ref,
            enabled: true,
            created_at: chrono::Utc::now(),
            execution_count: 0,
        };

        let id = system.event_bus().register_hook(hook);
        id.0.to_string()
    }

    /// Emit an event and get triggered hooks
    fn emit_event(
        &self,
        event_type: String,
        source: String,
        payload: String,
    ) -> Vec<String> {
        let system = self.inner.read().unwrap();

        let et = match event_type.as_str() {
            "agent_step_start" => EventType::AgentStepStart,
            "agent_step_end" => EventType::AgentStepEnd,
            "tool_call_pre" => EventType::ToolCallPre,
            "tool_call_post" => EventType::ToolCallPost,
            "error" => EventType::Error,
            "retry" => EventType::Retry,
            _ => EventType::Custom(event_type),
        };

        let src = if source == "system" {
            EventSource::System
        } else if source.starts_with("agent:") {
            EventSource::Agent {
                id: source[6..].to_string(),
                name: source[6..].to_string(),
            }
        } else {
            EventSource::External { source }
        };

        let payload_value: serde_json::Value = serde_json::from_str(&payload)
            .unwrap_or(serde_json::json!({}));

        let event = Event::new(et, src, payload_value);
        let hooks = system.event_bus().emit(event);

        hooks.iter().map(|h| h.id.0.to_string()).collect()
    }

    /// Add a node to the propagation graph
    fn add_propagation_node(
        &self,
        name: String,
        node_type: String,
        entity_id: Option<String>,
    ) -> String {
        let mut system = self.inner.write().unwrap();

        let nt = match node_type.as_str() {
            "agent" => PropagationNodeType::Agent,
            "tool" => PropagationNodeType::Tool,
            "hook" => PropagationNodeType::Hook,
            "entity" => PropagationNodeType::Entity,
            "session" => PropagationNodeType::Session,
            _ => PropagationNodeType::External,
        };

        let node = PropagationNode {
            id: uuid::Uuid::new_v4(),
            entity_id: entity_id.and_then(|s| {
                uuid::Uuid::parse_str(&s).ok().map(|u| crate::EntityId(u))
            }),
            node_type: nt,
            name,
            metadata: HashMap::new(),
            created_at: chrono::Utc::now(),
        };

        let id = system.propagation_graph_mut().add_node(node);
        id.to_string()
    }

    /// Add an edge to the propagation graph
    fn add_propagation_edge(
        &self,
        source: String,
        target: String,
        edge_type: String,
    ) -> PyResult<String> {
        let mut system = self.inner.write().unwrap();

        let source_uuid = uuid::Uuid::parse_str(&source)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        let target_uuid = uuid::Uuid::parse_str(&target)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;

        let et = match edge_type.as_str() {
            "direct_call" => PropagationEdgeType::DirectCall,
            "event_triggered" => PropagationEdgeType::EventTriggered,
            "namespace_sharing" => PropagationEdgeType::NamespaceSharing,
            "nested_tool_call" => PropagationEdgeType::NestedToolCall,
            "agent_delegation" => PropagationEdgeType::AgentDelegation,
            "shared_state" => PropagationEdgeType::SharedState,
            _ => PropagationEdgeType::DirectCall,
        };

        match system.propagation_graph_mut().add_edge(source_uuid, target_uuid, et) {
            Ok(id) => Ok(id.to_string()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())),
        }
    }

    /// Get reachable nodes from a source
    fn get_reachable_nodes(&self, source: String, max_depth: Option<usize>) -> Vec<(String, usize)> {
        let system = self.inner.read().unwrap();

        let source_uuid = match uuid::Uuid::parse_str(&source) {
            Ok(u) => u,
            Err(_) => return Vec::new(),
        };

        system.propagation_graph()
            .get_reachable_nodes(source_uuid, max_depth)
            .into_iter()
            .map(|(id, depth)| (id.to_string(), depth))
            .collect()
    }

    /// Export full system state as JSON
    fn export_state(&self) -> String {
        let system = self.inner.read().unwrap();
        serde_json::to_string_pretty(&system.export_state()).unwrap_or_default()
    }

    /// Export propagation graph as DOT format
    fn export_propagation_dot(&self) -> String {
        let system = self.inner.read().unwrap();
        system.propagation_graph().to_dot()
    }
}

/// Initialize the Python module
#[pymodule]
fn pse_core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyPseConfig>()?;
    m.add_class::<PyPseSystem>()?;
    Ok(())
}
