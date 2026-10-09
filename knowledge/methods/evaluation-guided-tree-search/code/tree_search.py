#!/usr/bin/env python3
"""Evaluation-guided tree search (UCB1) over candidate mutations.

Mechanism source: AFlow, "AFlow: Automating Agentic Workflow Generation"
(arXiv:2410.10762, ICLR 2025 Oral).

This is a harness-agnostic skeleton of the mechanism:
- Candidates (workflow variants) live in a tree; each node stores its evaluation score;
- Selection descends by UCB1; a node is expanded (one rotation step of mutation
  operators) until all operators are tried, then selection descends into children;
- Backpropagation updates visit counts and total score up the path;
- Evaluator and mutation operators are injected; uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field
from typing import Callable

# Evaluator: candidate text in, scalar score out (higher is better).
Evaluator = Callable[[str], float]


@dataclass(frozen=True)
class Operator:
    """A named mutation: candidate text in, new candidate text out."""

    name: str
    mutate: Callable[[str], str]


@dataclass
class Node:
    """One candidate in the search tree, with its score and visit statistics."""

    candidate: str
    score: float
    parent: "Node | None" = None
    children: list["Node"] = field(default_factory=list)
    visits: int = 0
    total: float = 0.0
    expansions: int = 0  # how many operator applications have been tried at this node

    def ucb1(self, c: float = 1.4) -> float:
        if self.visits == 0 or self.parent is None:
            return float("inf")
        exploit = self.total / self.visits
        explore = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploit + explore


class TreeSearch:
    """UCB1-guided expansion of candidates evaluated by an injected evaluator."""

    def __init__(self, evaluator: Evaluator, operators: list[Operator], c: float = 1.4):
        if not operators:
            raise ValueError("at least one mutation operator is required")
        self.evaluator = evaluator
        self.operators = operators
        self.c = c
        self.root: Node | None = None
        # (iteration, operator name, score) for every expansion, in order.
        self.history: list[tuple[int, str, float]] = []

    def _select(self, node: Node) -> Node:
        """Descend while the node has been fully expanded; otherwise expand here."""
        while node.children and node.expansions >= len(self.operators):
            node = max(node.children, key=lambda child: child.ucb1(self.c))
        return node

    def _expand(self, node: Node) -> tuple[Node, Operator]:
        operator = self.operators[node.expansions % len(self.operators)]
        node.expansions += 1
        child = Node(candidate=operator.mutate(node.candidate), score=0.0, parent=node)
        node.children.append(child)
        return child, operator

    def _backprop(self, node: Node | None, score: float) -> None:
        while node is not None:
            node.visits += 1
            node.total += score
            node = node.parent

    def all_nodes(self) -> list[Node]:
        if self.root is None:
            return []
        nodes: list[Node] = []
        stack = [self.root]
        while stack:
            current = stack.pop()
            nodes.append(current)
            stack.extend(current.children)
        return nodes

    def best(self) -> Node | None:
        nodes = self.all_nodes()
        if not nodes:
            return None
        return max(nodes, key=lambda node: node.score)

    def run(self, seed: str, budget: int) -> Node:
        """Evaluate the seed, then expand ``budget`` children guided by UCB1."""
        root_score = self.evaluator(seed)
        self.root = Node(candidate=seed, score=root_score)
        self._backprop(self.root, root_score)
        for iteration in range(1, budget + 1):
            leaf = self._select(self.root)
            child, operator = self._expand(leaf)
            child.score = self.evaluator(child.candidate)
            self._backprop(child, child.score)
            self.history.append((iteration, operator.name, child.score))
        return self.root


TARGET = 10.0


def demo_evaluator(candidate: str) -> float:
    """Closeness to the target value: 1 / (1 + |x - TARGET|), in (0, 1]."""
    value = float(candidate)
    return 1.0 / (1.0 + abs(value - TARGET))


def demo_operators() -> list[Operator]:
    """Three numeric mutations (+1, *2, /2); the search improves 1 toward the target 10."""
    return [
        Operator("inc", lambda c: f"{float(c) + 1.0:g}"),
        Operator("double", lambda c: f"{float(c) * 2.0:g}"),
        Operator("half", lambda c: f"{float(c) / 2.0:g}"),
    ]


def demo_command(args: argparse.Namespace) -> None:
    """Minimal demo: search from 1 toward TARGET=10.0 with a fixed expansion budget."""
    search = TreeSearch(evaluator=demo_evaluator, operators=demo_operators())
    search.run(seed="1", budget=args.budget)

    best = search.best()
    print(f"Target: {TARGET} (evaluator: 1 / (1 + |x - target|))")
    print(f"Budget: {args.budget} expansions, nodes: {len(search.all_nodes())}")
    print(f"Best candidate: {best.candidate} (score {best.score:.4f})")

    print("Top-3 nodes:")
    top = sorted(search.all_nodes(), key=lambda node: -node.score)[:3]
    for node in top:
        print(f"  {node.candidate}: {node.score:.4f} (visits {node.visits})")

    print("Last 5 expansions:")
    for iteration, operator_name, score in search.history[-5:]:
        print(f"  #{iteration} {operator_name} -> score {score:.4f}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluation-guided tree search (UCB1) over candidate mutations."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Search numeric variants from 1 toward 10")
    demo.add_argument("--budget", type=int, default=40, help="number of expansions (default: 40)")
    demo.set_defaults(handler=demo_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
