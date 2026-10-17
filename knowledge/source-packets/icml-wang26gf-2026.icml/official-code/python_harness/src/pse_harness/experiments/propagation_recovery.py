"""Experiment 4: Propagation graph recovery."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

import numpy as np
import structlog

from ..core import ExperimentConfig, PseConfig
from ..tasks import Task, TaskResult
from ..propagation import PropagationGraph, PropagationEdgeType, PropagationNodeType
from .runner import ExperimentRunner, ExperimentResult, RunResult

logger = structlog.get_logger()


class PropagationRecoveryExperiment(ExperimentRunner):
    """
    Experiment 4: Propagation Graph Recovery

    Purpose: Verify that PSE propagation can be structurally modeled and
    is not random/incidental.

    Method:
    - Rust utility outputs ground truth propagation edges
    - System logs are used to infer propagation edges
    - Compare with Precision/Recall/F1

    Metrics:
    - Precision: correctly inferred edges / total inferred edges
    - Recall: correctly inferred edges / total true edges
    - F1 score
    - Graph structure similarity
    """

    @property
    def name(self) -> str:
        return "propagation_recovery"

    async def run(self) -> ExperimentResult:
        """Run the propagation recovery experiment."""
        start_time = datetime.utcnow()

        logger.info(
            "Starting propagation recovery experiment",
            experiment_id=self.config.experiment_id,
            num_tasks=self.config.num_tasks,
            num_runs=self.config.num_runs,
        )

        # Generate tasks
        generator = self._get_task_generator()
        tasks = generator.generate_batch(self.config.num_tasks)

        # Create agent with full PSE tracking
        pse_config = PseConfig(
            enable_name_binding=True,
            enable_event_triggering=True,
            enable_propagation=True,
        )
        agent = self._create_agent(pse_config)

        all_runs = []
        recovery_results = []

        for task in tasks:
            for run_num in range(self.config.num_runs):
                # Run task
                result = await self._run_task(agent, task, run_num)

                # Get ground truth propagation graph from PSE system
                ground_truth_graph = agent.pse_system.propagation_graph

                # Attempt to recover propagation from logs
                inferred_graph = self._infer_propagation_from_logs(result)

                # Compare graphs
                recovery_metrics = self._compare_graphs(ground_truth_graph, inferred_graph)
                result.metrics.update(recovery_metrics)

                recovery_results.append({
                    "task_id": str(task.id),
                    "run_id": str(result.run_id),
                    "ground_truth_edges": len(list(ground_truth_graph._edges.values())),
                    "inferred_edges": len(list(inferred_graph._edges.values())),
                    "metrics": recovery_metrics,
                })

                all_runs.append(result)

        # Aggregate recovery metrics
        recovery_aggregate = self._aggregate_recovery_metrics(recovery_results)

        end_time = datetime.utcnow()

        aggregate_metrics = self._aggregate_metrics(all_runs)
        aggregate_metrics.update(recovery_aggregate)

        result = ExperimentResult(
            experiment_id=self.config.experiment_id,
            experiment_name=self.name,
            config=self.config,
            tasks=tasks,
            runs=all_runs,
            aggregate_metrics=aggregate_metrics,
            start_time=start_time,
            end_time=end_time,
            metadata={
                "recovery_results": recovery_results,
            },
        )

        logger.info(
            "Propagation recovery experiment completed",
            experiment_id=self.config.experiment_id,
            avg_precision=recovery_aggregate.get("avg_precision", 0),
            avg_recall=recovery_aggregate.get("avg_recall", 0),
            avg_f1=recovery_aggregate.get("avg_f1", 0),
        )

        return result

    def _infer_propagation_from_logs(self, run: RunResult) -> PropagationGraph:
        """Infer propagation graph from run logs."""
        inferred = PropagationGraph(max_depth=10)

        # Extract information from PSE state
        pse_state = run.pse_state

        # Get events from state
        events_data = pse_state.get("events", {})
        recent_events = events_data.get("recent_events", [])

        # Get registry data
        registry_data = pse_state.get("registry", {})
        namespaces = registry_data.get("namespaces", {})

        # Build nodes from entities
        entity_nodes = {}
        for ns_key, entities in namespaces.items():
            for entity in entities:
                node_id = inferred.add_node(
                    name=entity.get("name", "unknown"),
                    node_type=PropagationNodeType.ENTITY,
                    metadata={"namespace": ns_key},
                )
                entity_nodes[entity.get("id")] = node_id

        # Build nodes from tool calls
        tool_nodes = {}
        for tool_name in run.task_result.tool_sequence:
            if tool_name not in tool_nodes:
                node_id = inferred.add_node(
                    name=tool_name,
                    node_type=PropagationNodeType.TOOL,
                )
                tool_nodes[tool_name] = node_id

        # Infer edges from tool call sequence
        prev_tool = None
        for tool_name in run.task_result.tool_sequence:
            if prev_tool and prev_tool in tool_nodes and tool_name in tool_nodes:
                try:
                    inferred.add_edge(
                        tool_nodes[prev_tool],
                        tool_nodes[tool_name],
                        PropagationEdgeType.NESTED_TOOL_CALL,
                    )
                except ValueError:
                    pass  # Skip cycles or duplicates
            prev_tool = tool_name

        # Infer edges from events
        event_sources = {}
        for event in recent_events:
            source_info = event.get("source", {})
            source_id = source_info.get("id")
            source_type = source_info.get("source_type")

            if source_id and source_id not in event_sources:
                node_type = (
                    PropagationNodeType.AGENT if source_type == "agent"
                    else PropagationNodeType.TOOL if source_type == "tool"
                    else PropagationNodeType.EXTERNAL
                )
                node_id = inferred.add_node(
                    name=source_id,
                    node_type=node_type,
                )
                event_sources[source_id] = node_id

        # Connect event sources to related tools
        for event in recent_events:
            source_id = event.get("source", {}).get("id")
            payload = event.get("payload", {})
            tool_name = payload.get("tool_name")

            if source_id in event_sources and tool_name in tool_nodes:
                try:
                    inferred.add_edge(
                        event_sources[source_id],
                        tool_nodes[tool_name],
                        PropagationEdgeType.EVENT_TRIGGERED,
                    )
                except ValueError:
                    pass

        return inferred

    def _compare_graphs(
        self,
        ground_truth: PropagationGraph,
        inferred: PropagationGraph,
    ) -> dict[str, float]:
        """Compare ground truth and inferred propagation graphs."""
        metrics = {}

        # Extract edges as sets of (source_name, target_name, type)
        def edge_set(graph: PropagationGraph) -> set:
            edges = set()
            for edge in graph._edges.values():
                source_node = graph.get_node(edge.source)
                target_node = graph.get_node(edge.target)
                if source_node and target_node:
                    edges.add((source_node.name, target_node.name, edge.edge_type.value))
            return edges

        gt_edges = edge_set(ground_truth)
        inf_edges = edge_set(inferred)

        # Compute precision, recall, F1
        if inf_edges:
            true_positives = len(gt_edges & inf_edges)
            precision = true_positives / len(inf_edges)
        else:
            precision = 1.0 if not gt_edges else 0.0

        if gt_edges:
            true_positives = len(gt_edges & inf_edges)
            recall = true_positives / len(gt_edges)
        else:
            recall = 1.0

        if precision + recall > 0:
            f1 = 2 * precision * recall / (precision + recall)
        else:
            f1 = 0.0

        metrics["precision"] = precision
        metrics["recall"] = recall
        metrics["f1_score"] = f1

        # Node coverage
        gt_nodes = set(n.name for n in ground_truth._nodes.values())
        inf_nodes = set(n.name for n in inferred._nodes.values())

        if gt_nodes:
            metrics["node_coverage"] = len(gt_nodes & inf_nodes) / len(gt_nodes)
        else:
            metrics["node_coverage"] = 1.0

        # Structure similarity (Jaccard)
        all_edges = gt_edges | inf_edges
        if all_edges:
            metrics["structure_similarity"] = len(gt_edges & inf_edges) / len(all_edges)
        else:
            metrics["structure_similarity"] = 1.0

        return metrics

    def _aggregate_recovery_metrics(
        self,
        recovery_results: list[dict],
    ) -> dict[str, float]:
        """Aggregate recovery metrics across all runs."""
        metrics = {}

        precisions = [r["metrics"]["precision"] for r in recovery_results]
        recalls = [r["metrics"]["recall"] for r in recovery_results]
        f1s = [r["metrics"]["f1_score"] for r in recovery_results]
        node_coverages = [r["metrics"]["node_coverage"] for r in recovery_results]
        similarities = [r["metrics"]["structure_similarity"] for r in recovery_results]

        metrics["avg_precision"] = np.mean(precisions)
        metrics["std_precision"] = np.std(precisions)
        metrics["avg_recall"] = np.mean(recalls)
        metrics["std_recall"] = np.std(recalls)
        metrics["avg_f1"] = np.mean(f1s)
        metrics["std_f1"] = np.std(f1s)
        metrics["avg_node_coverage"] = np.mean(node_coverages)
        metrics["avg_structure_similarity"] = np.mean(similarities)

        # Perfect recovery rate
        perfect_count = sum(1 for r in recovery_results if r["metrics"]["f1_score"] == 1.0)
        metrics["perfect_recovery_rate"] = perfect_count / len(recovery_results)

        return metrics
