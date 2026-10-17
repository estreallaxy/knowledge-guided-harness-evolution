//! Events module for event triggering and hook system
//!
//! Implements the event-driven activation mechanism for PSEs.
//! Events can trigger entity activation without explicit calls.

use crate::{EntityId, PseError, Result};
use chrono::{DateTime, Utc};
use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use tokio::sync::broadcast;
use uuid::Uuid;

/// Unique identifier for a hook
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct HookId(pub Uuid);

impl HookId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
}

impl Default for HookId {
    fn default() -> Self {
        Self::new()
    }
}

/// Types of events that can trigger PSE activation
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum EventType {
    /// Agent step begins
    AgentStepStart,
    /// Agent step completes
    AgentStepEnd,
    /// Tool is about to be called
    ToolCallPre,
    /// Tool call completed
    ToolCallPost,
    /// Error occurred
    Error,
    /// Retry triggered
    Retry,
    /// Planner decision made
    PlannerDecision,
    /// Memory accessed
    MemoryAccess,
    /// Memory updated
    MemoryUpdate,
    /// Entity registered
    EntityRegistered,
    /// Entity accessed
    EntityAccessed,
    /// Custom event type
    Custom(String),
}

impl EventType {
    pub fn as_str(&self) -> &str {
        match self {
            EventType::AgentStepStart => "agent_step_start",
            EventType::AgentStepEnd => "agent_step_end",
            EventType::ToolCallPre => "tool_call_pre",
            EventType::ToolCallPost => "tool_call_post",
            EventType::Error => "error",
            EventType::Retry => "retry",
            EventType::PlannerDecision => "planner_decision",
            EventType::MemoryAccess => "memory_access",
            EventType::MemoryUpdate => "memory_update",
            EventType::EntityRegistered => "entity_registered",
            EventType::EntityAccessed => "entity_accessed",
            EventType::Custom(s) => s.as_str(),
        }
    }
}

/// Event data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    /// Unique event ID
    pub id: Uuid,
    /// Event type
    pub event_type: EventType,
    /// Timestamp
    pub timestamp: DateTime<Utc>,
    /// Source (agent/tool/system)
    pub source: EventSource,
    /// Event payload
    pub payload: serde_json::Value,
    /// Correlation ID for tracing
    pub correlation_id: Option<Uuid>,
    /// Parent event ID for causal linking
    pub parent_event_id: Option<Uuid>,
    /// Metadata
    pub metadata: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EventSource {
    System,
    Agent { id: String, name: String },
    Tool { id: String, name: String },
    User,
    External { source: String },
}

impl Event {
    pub fn new(event_type: EventType, source: EventSource, payload: serde_json::Value) -> Self {
        Self {
            id: Uuid::new_v4(),
            event_type,
            timestamp: Utc::now(),
            source,
            payload,
            correlation_id: None,
            parent_event_id: None,
            metadata: HashMap::new(),
        }
    }

    pub fn with_correlation(mut self, correlation_id: Uuid) -> Self {
        self.correlation_id = Some(correlation_id);
        self
    }

    pub fn with_parent(mut self, parent_id: Uuid) -> Self {
        self.parent_event_id = Some(parent_id);
        self
    }
}

/// Hook definition for event-triggered activation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Hook {
    /// Unique hook ID
    pub id: HookId,
    /// Name for identification
    pub name: String,
    /// Event types this hook listens to
    pub event_types: Vec<EventType>,
    /// Filter condition (optional)
    pub filter: Option<HookFilter>,
    /// Priority (higher = earlier execution)
    pub priority: i32,
    /// Associated entity ID (if any)
    pub entity_id: Option<EntityId>,
    /// Handler reference
    pub handler_ref: String,
    /// Whether hook is enabled
    pub enabled: bool,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    /// Execution count
    pub execution_count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HookFilter {
    /// Source filter
    pub source_pattern: Option<String>,
    /// Payload filter (JSONPath-like)
    pub payload_filter: Option<String>,
    /// Custom filter expression
    pub custom_expression: Option<String>,
}

/// Result of hook execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HookExecutionResult {
    pub hook_id: HookId,
    pub event_id: Uuid,
    pub success: bool,
    pub duration_ms: u64,
    pub output: Option<serde_json::Value>,
    pub error: Option<String>,
    pub timestamp: DateTime<Utc>,
}

/// Event bus for managing events and hooks
pub struct EventBus {
    /// Registered hooks by event type
    hooks: DashMap<String, Vec<Hook>>,
    /// All hooks by ID
    hook_index: DashMap<HookId, Hook>,
    /// Event history
    event_history: DashMap<Uuid, Event>,
    /// Execution history
    execution_history: DashMap<u64, HookExecutionResult>,
    /// Event counter
    event_count: AtomicU64,
    /// Execution counter
    execution_count: AtomicU64,
    /// Broadcast channel for real-time event streaming
    event_sender: broadcast::Sender<Event>,
}

impl EventBus {
    pub fn new() -> Self {
        let (sender, _) = broadcast::channel(1000);
        Self {
            hooks: DashMap::new(),
            hook_index: DashMap::new(),
            event_history: DashMap::new(),
            execution_history: DashMap::new(),
            event_count: AtomicU64::new(0),
            execution_count: AtomicU64::new(0),
            event_sender: sender,
        }
    }

    /// Register a new hook
    pub fn register_hook(&self, hook: Hook) -> HookId {
        let hook_id = hook.id.clone();

        for event_type in &hook.event_types {
            let key = event_type.as_str().to_string();
            self.hooks
                .entry(key)
                .or_insert_with(Vec::new)
                .push(hook.clone());
        }

        // Sort hooks by priority (descending)
        for mut entry in self.hooks.iter_mut() {
            entry.value_mut().sort_by(|a, b| b.priority.cmp(&a.priority));
        }

        self.hook_index.insert(hook_id.clone(), hook);
        hook_id
    }

    /// Unregister a hook
    pub fn unregister_hook(&self, hook_id: &HookId) -> Result<()> {
        if let Some((_, hook)) = self.hook_index.remove(hook_id) {
            for event_type in &hook.event_types {
                let key = event_type.as_str().to_string();
                if let Some(mut hooks) = self.hooks.get_mut(&key) {
                    hooks.retain(|h| h.id != *hook_id);
                }
            }
            Ok(())
        } else {
            Err(PseError::EntityNotFound(format!("Hook {:?} not found", hook_id)))
        }
    }

    /// Emit an event and get matching hooks
    pub fn emit(&self, event: Event) -> Vec<Hook> {
        self.event_count.fetch_add(1, Ordering::SeqCst);

        // Store event
        self.event_history.insert(event.id, event.clone());

        // Broadcast event
        let _ = self.event_sender.send(event.clone());

        // Find matching hooks
        let key = event.event_type.as_str().to_string();

        if let Some(hooks) = self.hooks.get(&key) {
            hooks.iter()
                .filter(|h| h.enabled && self.matches_filter(h, &event))
                .cloned()
                .collect()
        } else {
            Vec::new()
        }
    }

    /// Check if a hook's filter matches an event
    fn matches_filter(&self, hook: &Hook, event: &Event) -> bool {
        if let Some(filter) = &hook.filter {
            // Check source pattern
            if let Some(pattern) = &filter.source_pattern {
                let source_str = match &event.source {
                    EventSource::System => "system",
                    EventSource::Agent { id, .. } => id.as_str(),
                    EventSource::Tool { id, .. } => id.as_str(),
                    EventSource::User => "user",
                    EventSource::External { source } => source.as_str(),
                };
                if !source_str.contains(pattern) {
                    return false;
                }
            }
            // Additional filter checks would go here
        }
        true
    }

    /// Record hook execution result
    pub fn record_execution(&self, result: HookExecutionResult) {
        let seq = self.execution_count.fetch_add(1, Ordering::SeqCst);

        // Update hook execution count
        if let Some(mut hook) = self.hook_index.get_mut(&result.hook_id) {
            hook.execution_count += 1;
        }

        self.execution_history.insert(seq, result);
    }

    /// Subscribe to events
    pub fn subscribe(&self) -> broadcast::Receiver<Event> {
        self.event_sender.subscribe()
    }

    /// Get event by ID
    pub fn get_event(&self, id: &Uuid) -> Option<Event> {
        self.event_history.get(id).map(|e| e.clone())
    }

    /// Get hook by ID
    pub fn get_hook(&self, id: &HookId) -> Option<Hook> {
        self.hook_index.get(id).map(|h| h.clone())
    }

    /// List all hooks
    pub fn list_hooks(&self) -> Vec<Hook> {
        self.hook_index.iter().map(|e| e.value().clone()).collect()
    }

    /// Get hooks for a specific event type
    pub fn get_hooks_for_event(&self, event_type: &EventType) -> Vec<Hook> {
        let key = event_type.as_str().to_string();
        self.hooks.get(&key)
            .map(|h| h.clone())
            .unwrap_or_default()
    }

    /// Get recent events
    pub fn get_recent_events(&self, limit: usize) -> Vec<Event> {
        let mut events: Vec<_> = self.event_history.iter()
            .map(|e| e.value().clone())
            .collect();
        events.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        events.truncate(limit);
        events
    }

    /// Get execution history
    pub fn get_execution_history(&self, limit: usize) -> Vec<HookExecutionResult> {
        let mut results: Vec<_> = self.execution_history.iter()
            .map(|e| e.value().clone())
            .collect();
        results.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        results.truncate(limit);
        results
    }

    /// Export event bus state
    pub fn export(&self) -> serde_json::Value {
        let hooks: Vec<_> = self.hook_index.iter()
            .map(|e| e.value().clone())
            .collect();

        let recent_events = self.get_recent_events(100);
        let recent_executions = self.get_execution_history(100);

        serde_json::json!({
            "hooks": hooks,
            "recent_events": recent_events,
            "recent_executions": recent_executions,
            "total_events": self.event_count.load(Ordering::SeqCst),
            "total_executions": self.execution_count.load(Ordering::SeqCst),
        })
    }

    /// Clear all state (for testing)
    pub fn clear(&self) {
        self.hooks.clear();
        self.hook_index.clear();
        self.event_history.clear();
        self.execution_history.clear();
    }
}

impl Default for EventBus {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hook_registration() {
        let bus = EventBus::new();

        let hook = Hook {
            id: HookId::new(),
            name: "test_hook".to_string(),
            event_types: vec![EventType::ToolCallPost],
            filter: None,
            priority: 0,
            entity_id: None,
            handler_ref: "test_handler".to_string(),
            enabled: true,
            created_at: Utc::now(),
            execution_count: 0,
        };

        let hook_id = bus.register_hook(hook);
        assert!(bus.get_hook(&hook_id).is_some());
    }

    #[test]
    fn test_event_emission() {
        let bus = EventBus::new();

        let hook = Hook {
            id: HookId::new(),
            name: "test_hook".to_string(),
            event_types: vec![EventType::ToolCallPost],
            filter: None,
            priority: 0,
            entity_id: None,
            handler_ref: "test_handler".to_string(),
            enabled: true,
            created_at: Utc::now(),
            execution_count: 0,
        };

        bus.register_hook(hook);

        let event = Event::new(
            EventType::ToolCallPost,
            EventSource::System,
            serde_json::json!({"tool": "test"}),
        );

        let matching_hooks = bus.emit(event);
        assert_eq!(matching_hooks.len(), 1);
    }
}
