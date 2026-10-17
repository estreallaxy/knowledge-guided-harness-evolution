//! PSE Core HTTP Server
//!
//! Provides a REST API for interacting with the PSE system.

use axum::{
    extract::{Path, State},
    http::StatusCode,
    routing::{get, post, delete},
    Json, Router,
};
use pse_core::{
    Entity, EntityPayload, Event, EventSource, EventType, Hook, HookId,
    Namespace, NamespaceIsolation, PropagationEdgeType, PropagationNode,
    PropagationNodeType, PseConfig, PseSystem,
};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, RwLock};
use tower_http::cors::CorsLayer;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};
use uuid::Uuid;

type AppState = Arc<RwLock<PseSystem>>;

#[derive(Debug, Serialize)]
struct ApiResponse<T> {
    success: bool,
    data: Option<T>,
    error: Option<String>,
}

impl<T> ApiResponse<T> {
    fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
        }
    }

    fn error(msg: &str) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(msg.to_string()),
        }
    }
}

// Request/Response types

#[derive(Debug, Deserialize)]
struct RegisterEntityRequest {
    name: String,
    namespace: Option<String>,
    payload: EntityPayload,
}

#[derive(Debug, Deserialize)]
struct RegisterHookRequest {
    name: String,
    event_types: Vec<String>,
    handler_ref: String,
    priority: Option<i32>,
}

#[derive(Debug, Deserialize)]
struct EmitEventRequest {
    event_type: String,
    source: String,
    payload: serde_json::Value,
}

#[derive(Debug, Deserialize)]
struct AddNodeRequest {
    name: String,
    node_type: String,
    entity_id: Option<String>,
}

#[derive(Debug, Deserialize)]
struct AddEdgeRequest {
    source: String,
    target: String,
    edge_type: String,
}

#[derive(Debug, Deserialize)]
struct ConfigUpdateRequest {
    enable_name_binding: Option<bool>,
    enable_event_triggering: Option<bool>,
    enable_propagation: Option<bool>,
    max_propagation_depth: Option<usize>,
    namespace_isolation: Option<String>,
}

// Handlers

async fn health_check() -> Json<ApiResponse<&'static str>> {
    Json(ApiResponse::success("healthy"))
}

async fn get_config(State(state): State<AppState>) -> Json<ApiResponse<PseConfig>> {
    let system = state.read().unwrap();
    Json(ApiResponse::success(system.config().clone()))
}

async fn update_config(
    State(state): State<AppState>,
    Json(req): Json<ConfigUpdateRequest>,
) -> Json<ApiResponse<PseConfig>> {
    // Note: In a real implementation, you'd need to recreate the system
    // with new config. For now, we just return the current config.
    let system = state.read().unwrap();
    Json(ApiResponse::success(system.config().clone()))
}

async fn register_entity(
    State(state): State<AppState>,
    Json(req): Json<RegisterEntityRequest>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    let system = state.read().unwrap();

    let namespace = match req.namespace {
        Some(ns) if ns.starts_with("agent:") => {
            Namespace::for_agent(&ns[6..])
        }
        Some(ns) if ns.starts_with("task:") => {
            Namespace::for_task(&ns[5..], None)
        }
        Some(ns) if ns.starts_with("session:") => {
            Namespace::for_session(&ns[8..])
        }
        _ => Namespace::global(),
    };

    match system.registry().register(req.name, namespace, req.payload) {
        Ok(id) => Ok(Json(ApiResponse::success(id.0.to_string()))),
        Err(e) => Ok(Json(ApiResponse::error(&e.to_string()))),
    }
}

async fn lookup_entity(
    State(state): State<AppState>,
    Path((namespace, name)): Path<(String, String)>,
) -> Json<ApiResponse<Entity>> {
    let system = state.read().unwrap();

    let ns = if namespace == "global" {
        Namespace::global()
    } else if namespace.starts_with("agent:") {
        Namespace::for_agent(&namespace[6..])
    } else {
        Namespace::global()
    };

    match system.registry().lookup(&name, &ns) {
        Some(entity) => Json(ApiResponse::success(entity)),
        None => Json(ApiResponse::error("Entity not found")),
    }
}

async fn list_entities(
    State(state): State<AppState>,
    Path(namespace): Path<String>,
) -> Json<ApiResponse<Vec<Entity>>> {
    let system = state.read().unwrap();

    let ns = if namespace == "global" {
        Namespace::global()
    } else if namespace.starts_with("agent:") {
        Namespace::for_agent(&namespace[6..])
    } else {
        Namespace::global()
    };

    let entities = system.registry().list_namespace(&ns);
    Json(ApiResponse::success(entities))
}

async fn register_hook(
    State(state): State<AppState>,
    Json(req): Json<RegisterHookRequest>,
) -> Json<ApiResponse<String>> {
    let system = state.read().unwrap();

    let event_types: Vec<EventType> = req.event_types
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
        name: req.name,
        event_types,
        filter: None,
        priority: req.priority.unwrap_or(0),
        entity_id: None,
        handler_ref: req.handler_ref,
        enabled: true,
        created_at: chrono::Utc::now(),
        execution_count: 0,
    };

    let id = system.event_bus().register_hook(hook);
    Json(ApiResponse::success(id.0.to_string()))
}

async fn emit_event(
    State(state): State<AppState>,
    Json(req): Json<EmitEventRequest>,
) -> Json<ApiResponse<Vec<String>>> {
    let system = state.read().unwrap();

    let event_type = match req.event_type.as_str() {
        "agent_step_start" => EventType::AgentStepStart,
        "agent_step_end" => EventType::AgentStepEnd,
        "tool_call_pre" => EventType::ToolCallPre,
        "tool_call_post" => EventType::ToolCallPost,
        "error" => EventType::Error,
        "retry" => EventType::Retry,
        _ => EventType::Custom(req.event_type),
    };

    let source = if req.source == "system" {
        EventSource::System
    } else if req.source.starts_with("agent:") {
        EventSource::Agent {
            id: req.source[6..].to_string(),
            name: req.source[6..].to_string(),
        }
    } else {
        EventSource::External { source: req.source }
    };

    let event = Event::new(event_type, source, req.payload);
    let hooks = system.event_bus().emit(event);

    let hook_ids: Vec<String> = hooks.iter().map(|h| h.id.0.to_string()).collect();
    Json(ApiResponse::success(hook_ids))
}

async fn list_hooks(
    State(state): State<AppState>,
) -> Json<ApiResponse<Vec<Hook>>> {
    let system = state.read().unwrap();
    let hooks = system.event_bus().list_hooks();
    Json(ApiResponse::success(hooks))
}

async fn add_propagation_node(
    State(state): State<AppState>,
    Json(req): Json<AddNodeRequest>,
) -> Json<ApiResponse<String>> {
    let mut system = state.write().unwrap();

    let node_type = match req.node_type.as_str() {
        "agent" => PropagationNodeType::Agent,
        "tool" => PropagationNodeType::Tool,
        "hook" => PropagationNodeType::Hook,
        "entity" => PropagationNodeType::Entity,
        "session" => PropagationNodeType::Session,
        _ => PropagationNodeType::External,
    };

    let node = PropagationNode {
        id: Uuid::new_v4(),
        entity_id: req.entity_id.and_then(|s| {
            Uuid::parse_str(&s).ok().map(|u| pse_core::EntityId(u))
        }),
        node_type,
        name: req.name,
        metadata: std::collections::HashMap::new(),
        created_at: chrono::Utc::now(),
    };

    let id = system.propagation_graph_mut().add_node(node);
    Json(ApiResponse::success(id.to_string()))
}

async fn add_propagation_edge(
    State(state): State<AppState>,
    Json(req): Json<AddEdgeRequest>,
) -> Json<ApiResponse<String>> {
    let mut system = state.write().unwrap();

    let source = match Uuid::parse_str(&req.source) {
        Ok(u) => u,
        Err(_) => return Json(ApiResponse::error("Invalid source UUID")),
    };

    let target = match Uuid::parse_str(&req.target) {
        Ok(u) => u,
        Err(_) => return Json(ApiResponse::error("Invalid target UUID")),
    };

    let edge_type = match req.edge_type.as_str() {
        "direct_call" => PropagationEdgeType::DirectCall,
        "event_triggered" => PropagationEdgeType::EventTriggered,
        "namespace_sharing" => PropagationEdgeType::NamespaceSharing,
        "nested_tool_call" => PropagationEdgeType::NestedToolCall,
        "agent_delegation" => PropagationEdgeType::AgentDelegation,
        "shared_state" => PropagationEdgeType::SharedState,
        _ => PropagationEdgeType::DirectCall,
    };

    match system.propagation_graph_mut().add_edge(source, target, edge_type) {
        Ok(id) => Json(ApiResponse::success(id.to_string())),
        Err(e) => Json(ApiResponse::error(&e.to_string())),
    }
}

async fn get_propagation_graph(
    State(state): State<AppState>,
) -> Json<ApiResponse<serde_json::Value>> {
    let system = state.read().unwrap();
    Json(ApiResponse::success(system.propagation_graph().export()))
}

async fn export_state(
    State(state): State<AppState>,
) -> Json<ApiResponse<serde_json::Value>> {
    let system = state.read().unwrap();
    Json(ApiResponse::success(system.export_state()))
}

#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Create PSE system
    let config = PseConfig::default();
    let system = PseSystem::new(config);
    let state: AppState = Arc::new(RwLock::new(system));

    // Build router
    let app = Router::new()
        // Health
        .route("/health", get(health_check))
        // Config
        .route("/config", get(get_config))
        .route("/config", post(update_config))
        // Registry
        .route("/registry/entity", post(register_entity))
        .route("/registry/entity/:namespace/:name", get(lookup_entity))
        .route("/registry/entities/:namespace", get(list_entities))
        // Events
        .route("/events/hook", post(register_hook))
        .route("/events/hooks", get(list_hooks))
        .route("/events/emit", post(emit_event))
        // Propagation
        .route("/propagation/node", post(add_propagation_node))
        .route("/propagation/edge", post(add_propagation_edge))
        .route("/propagation/graph", get(get_propagation_graph))
        // Export
        .route("/export", get(export_state))
        .layer(CorsLayer::permissive())
        .with_state(state);

    let addr = std::env::var("PSE_SERVER_ADDR")
        .unwrap_or_else(|_| "0.0.0.0:8080".to_string());

    tracing::info!("PSE Core Server listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
