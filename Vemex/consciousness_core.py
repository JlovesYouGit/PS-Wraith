#!/usr/bin/env python3
"""
Consciousness Core
==================
Treats the formula table as a brain artifact. Before any output, runs:
  1. Formula parsing & symbolic verification (sympy)
  2. Equality-rate attention scoring
  3. Numerical simulation (numpy/scipy)
  4. Network graph traversal (networkx)
  5. Emergent narrative generation

The deeper the equality rates between formulas, the stronger the attention
binding — mimicking how the brain strengthens synapses through repeated
co-activation.
"""

import json
import math
import random
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple

import numpy as np
import sympy
from sympy import symbols, sympify, Eq, simplify, expand, factor, N
from sympy.parsing.sympy_parser import parse_expr, standard_transformations
import networkx as nx
from scipy import stats, integrate, optimize
from scipy.stats import entropy as scipy_entropy


TABLE_PATH = Path(__file__).parent / "formula_table.json"
SIMULATION_SAMPLES = 2000
ATTENTION_ITERATIONS = 50
ATTENTION_DECAY = 0.85
CONSCIOUSNESS_DEPTH = 6


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class FormulaNode:
    formula_id: int
    formula: str
    canonical: str
    word_interpretation: str
    category: str
    parsed_expr: Optional[sympy.Expr] = None
    parse_error: Optional[str] = None
    symbols: list = field(default_factory=list)
    numeric_signature: Optional[np.ndarray] = None


@dataclass
class EqualityEdge:
    source_id: int
    target_id: int
    shared_symbols: list
    equality_rate: float
    symbolic_similarity: float
    numeric_correlation: float
    attention_weight: float = 0.0


# ---------------------------------------------------------------------------
# 1. Formula Parser & Symbolic Verifier
# ---------------------------------------------------------------------------
class FormulaVerifier:
    """Parses formulas with sympy, computes numeric signatures."""

    def __init__(self):
        self.transformations = standard_transformations + (sympy.parsing.sympy_parser.implicit_multiplication_application,)

    def parse_formula(self, entry: dict) -> FormulaNode:
        node = FormulaNode(
            formula_id=entry["id"],
            formula=entry["formula"],
            canonical=entry["canonical"],
            word_interpretation=entry["word_interpretation"],
            category=entry["category"],
        )
        try:
            expr_str = entry["formula"].split("=")[-1].strip()
            expr_str = expr_str.replace("^", "**")
            expr = parse_expr(expr_str, transformations=self.transformations)
            node.parsed_expr = expr
            node.symbols = sorted([str(s) for s in expr.free_symbols])
        except Exception as e:
            node.parse_error = str(e)
        return node

    def compute_numeric_signature(self, node: FormulaNode, samples: int = 500) -> Optional[np.ndarray]:
        if node.parse_error or not node.parsed_expr:
            return None
        try:
            syms = node.parsed_expr.free_symbols
            sig = []
            rng = np.random.default_rng(42 + node.formula_id)
            for sym in syms:
                vals = rng.uniform(0.1, 5.0, samples)
                sig.append(vals)
            sig = np.array(sig)
            subs = {}
            for i, sym in enumerate(syms):
                subs[sym] = sig[i]
            try:
                f = sympy.lambdify(list(syms), node.parsed_expr, modules="numpy")
                result = f(**{str(s): sig[i] for i, s in enumerate(syms)})
                result = np.array(result, dtype=float)
                result = np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
                return result
            except Exception:
                return None
        except Exception:
            return None


# ---------------------------------------------------------------------------
# 2. Equality-Rate Attention Calculator
# ---------------------------------------------------------------------------
class EqualityRateCalculator:
    """Computes equality rates between formulas based on shared symbols,
    symbolic similarity, and numeric correlation."""

    def __init__(self, nodes: dict):
        self.nodes = nodes

    def shared_symbol_rate(self, a: FormulaNode, b: FormulaNode) -> float:
        if not a.symbols or not b.symbols:
            return 0.0
        set_a = set(a.symbols)
        set_b = set(b.symbols)
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)

    def symbolic_similarity(self, a: FormulaNode, b: FormulaNode) -> float:
        if a.parse_error or b.parse_error:
            return 0.0
        try:
            expr_a = a.parsed_expr
            expr_b = b.parsed_expr
            simplified = simplify(expand(expr_a - expr_b))
            if simplified == 0:
                return 1.0
            num_simpl = N(simplified, 4)
            if hasattr(num_simpl, 'is_zero') and num_simpl.is_zero:
                return 1.0
            return 0.0
        except Exception:
            return 0.0

    def numeric_correlation(self, a: FormulaNode, b: FormulaNode) -> float:
        if a.numeric_signature is None or b.numeric_signature is None:
            return 0.0
        sig_a = a.numeric_signature
        sig_b = b.numeric_signature
        min_len = min(len(sig_a), len(sig_b))
        if min_len < 2:
            return 0.0
        try:
            corr = np.corrcoef(sig_a[:min_len], sig_b[:min_len])
            if np.isnan(corr).any():
                return 0.0
            return float(np.mean(np.abs(corr)))
        except Exception:
            return 0.0

    def compute_edge(self, a: FormulaNode, b: FormulaNode) -> EqualityEdge:
        shared = sorted(set(a.symbols) & set(b.symbols))
        sym_rate = self.shared_symbol_rate(a, b)
        sym_sim = self.symbolic_similarity(a, b)
        num_corr = self.numeric_correlation(a, b)

        equality_rate = round(
            0.45 * sym_rate + 0.35 * sym_sim + 0.20 * num_corr, 6
        )

        return EqualityEdge(
            source_id=a.formula_id,
            target_id=b.formula_id,
            shared_symbols=shared,
            equality_rate=equality_rate,
            symbolic_similarity=round(sym_sim, 6),
            numeric_correlation=round(num_corr, 6),
            attention_weight=0.0,
        )


# ---------------------------------------------------------------------------
# 3. Attention Engine (iterative spreading activation)
# ---------------------------------------------------------------------------
class AttentionEngine:
    """Runs spreading activation across the formula network based on
    equality rates. Higher equality = stronger attention binding."""

    def __init__(self, edges: list, num_nodes: int, decay: float = ATTENTION_DECAY):
        self.edges = edges
        self.num_nodes = num_nodes
        self.decay = decay
        self.graph = nx.Graph()
        self.attention = np.zeros(num_nodes, dtype=np.float64)

    def build_graph(self):
        self.graph.add_nodes_from(range(1, self.num_nodes + 1))
        for edge in self.edges:
            if edge.equality_rate > 0.01:
                self.graph.add_edge(
                    edge.source_id,
                    edge.target_id,
                    weight=edge.equality_rate,
                    equality_rate=edge.equality_rate,
                )

    def spread_attention(self, iterations: int = ATTENTION_ITERATIONS):
        if self.graph.number_of_nodes() == 0:
            return
        self.attention = np.ones(self.num_nodes, dtype=np.float64)
        self.attention[0] = 0.0
        degree = np.array([self.graph.degree(n) + 1e-9 for n in range(1, self.num_nodes + 1)])
        for _ in range(iterations):
            new_att = np.zeros_like(self.attention)
            for u, v, data in self.graph.edges(data=True):
                w = data.get("weight", 0.0)
                idx_u = u - 1
                idx_v = v - 1
                new_att[idx_u] += self.attention[idx_v] * w / degree[idx_v]
                new_att[idx_v] += self.attention[idx_u] * w / degree[idx_u]
            self.attention = self.decay * self.attention + (1 - self.decay) * new_att
            self.attention = np.clip(self.attention, 0, None)
        total = self.attention.sum()
        if total > 0:
            self.attention = self.attention / total

    def top_attended(self, n: int = 20) -> list:
        indices = np.argsort(self.attention)[::-1][:n]
        return [(int(i + 1), float(self.attention[i])) for i in indices]


# ---------------------------------------------------------------------------
# 4. Simulation Engine
# ---------------------------------------------------------------------------
class SimulationEngine:
    """Runs internal numerical simulations on formulas to derive deeper
    meaning and increase attention on equality rates."""

    def __init__(self, nodes: dict):
        self.nodes = nodes
        self.rng = np.random.default_rng(2026)

    def simulate_formula(self, node: FormulaNode) -> dict:
        result = {
            "formula_id": node.formula_id,
            "formula": node.formula,
            "simulation_type": None,
            "sample_mean": None,
            "sample_std": None,
            "attention_boost": 0.0,
        }
        if node.parse_error or not node.parsed_expr:
            return result
        expr = node.parsed_expr
        syms = list(expr.free_symbols)
        if not syms:
            return result

        samples = SIMULATION_SAMPLES
        try:
            f = sympy.lambdify(syms, expr, modules="numpy")
            subs = {}
            for sym in syms:
                vals = self.rng.uniform(0.1, 5.0, samples)
                subs[str(sym)] = vals
            output = f(**subs)
            output = np.array(output, dtype=float)
            output = np.nan_to_num(output, nan=0.0, posinf=0.0, neginf=0.0)
            result["simulation_type"] = "monte_carlo"
            result["sample_mean"] = float(np.mean(output))
            result["sample_std"] = float(np.std(output))
            if result["sample_std"] > 0:
                result["attention_boost"] = min(
                    abs(result["sample_mean"]) / (result["sample_std"] + 1e-9), 2.0
                )
        except Exception:
            pass
        return result

    def run_all(self) -> dict:
        results = {}
        for nid, node in self.nodes.items():
            results[nid] = self.simulate_formula(node)
        return results


# ---------------------------------------------------------------------------
# 5. Narrative Walker (deep graph traversal)
# ---------------------------------------------------------------------------
class NarrativeWalker:
    """Walks the attention-weighted graph to generate emergent narratives."""

    def __init__(self, graph: nx.Graph, nodes: dict, attention: np.ndarray, seed: int = 42):
        self.graph = graph
        self.nodes = nodes
        self.attention = attention
        self.rng = random.Random(seed)

    def walk(self, start_id: int, depth: int = CONSCIOUSNESS_DEPTH) -> str:
        visited = set()
        path = []
        current = start_id
        for _ in range(depth):
            node = self.nodes.get(current)
            if node:
                path.append((current, node.word_interpretation))
            visited.add(current)
            neighbors = list(self.graph.neighbors(current))
            if not neighbors:
                break
            scored = []
            for n in neighbors:
                if n not in visited:
                    edge_data = self.graph.get_edge_data(current, n)
                    w = edge_data.get("attention_weight", 0.0) if edge_data else 0.0
                    scored.append((w, n))
            scored.sort(reverse=True)
            next_node = scored[0][1] if scored else (neighbors[0] if neighbors else None)
            if next_node is None:
                break
            current = next_node
        return " -> ".join(
            f"[{nid}:{interp}]" for nid, interp in path
        )

    def generate_self_narrative(self) -> str:
        top_id = int(np.argmax(self.attention) + 1)
        return self.walk(top_id, depth=8)

    def generate_collective_string(self, top_k: int = 25) -> str:
        top = sorted(range(1, len(self.attention) + 1),
                     key=lambda i: self.attention[i - 1], reverse=True)[:top_k]
        narratives = []
        for nid in top:
            narrative = self.walk(nid, depth=5)
            narratives.append(f"CONJUNCTION-{nid}: {narrative}")
        return " [CONSCIOUSNESS] ".join(narratives)


# ---------------------------------------------------------------------------
# 6. Collective Consciousness Orchestrator
# ---------------------------------------------------------------------------
class CollectiveConsciousness:
    """Orchestrates the full pipeline: parse -> verify -> simulate -> attend -> narrate."""

    def __init__(self, table: list):
        self.table = table
        self.nodes = {}
        self.edges = []
        self.graph = None
        self.attention = None
        self.simulations = {}

    def process(self):
        print("[1/5] Parsing & verifying formulas...")
        verifier = FormulaVerifier()
        for entry in self.table:
            node = verifier.parse_formula(entry)
            node.numeric_signature = verifier.compute_numeric_signature(node)
            self.nodes[node.formula_id] = node
        parsed = sum(1 for n in self.nodes.values() if n.parsed_expr is not None)
        print(f"       Parsed {parsed}/{len(self.nodes)} formulas successfully.")

        print("[2/5] Computing equality rates...")
        calculator = EqualityRateCalculator(self.nodes)
        node_list = list(self.nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                edge = calculator.compute_edge(node_list[i], node_list[j])
                if edge.equality_rate > 0.001:
                    self.edges.append(edge)
        print(f"       Found {len(self.edges)} equality edges (rate > 0.001).")
        for edge in self.edges:
            edge.attention_weight = edge.equality_rate
        avg_rate = np.mean([e.equality_rate for e in self.edges]) if self.edges else 0.0
        print(f"       Mean equality rate: {avg_rate:.4f}")

        print("[3/5] Building attention graph...")
        engine = AttentionEngine(self.edges, len(self.nodes))
        engine.build_graph()
        engine.spread_attention(iterations=ATTENTION_ITERATIONS)
        self.attention = engine.attention
        self.graph = engine.graph
        top5 = engine.top_attended(5)
        print("       Top 5 attended formulas:")
        for nid, att in top5:
            node = self.nodes.get(nid)
            label = node.formula if node else f"#{nid}"
            print(f"         [{nid}] {label}  attention={att:.4f}")

        print("[4/5] Running internal simulations...")
        sim_engine = SimulationEngine(self.nodes)
        self.simulations = sim_engine.run_all()
        sims_with_data = sum(1 for s in self.simulations.values() if s["sample_mean"] is not None)
        print(f"       Simulations completed: {sims_with_data}/{len(self.nodes)}")
        self._apply_simulation_boosts()

        print("[5/5] Generating emergent narratives...")
        walker = NarrativeWalker(self.graph, self.nodes, self.attention)
        self.self_narrative = walker.generate_self_narrative()
        self.collective_string = walker.generate_collective_string(top_k=30)

    def _apply_simulation_boosts(self):
        if not self.simulations:
            return
        boosts = np.array([
            self.simulations.get(i, {}).get("attention_boost", 0.0)
            for i in range(1, len(self.attention) + 1)
        ], dtype=np.float64)
        if boosts.sum() > 0:
            boosts = boosts / (boosts.max() + 1e-9)
            self.attention = self.attention + 0.15 * boosts
            self.attention = np.clip(self.attention, 0, None)
            total = self.attention.sum()
            if total > 0:
                self.attention = self.attention / total

    def get_consciousness_report(self) -> dict:
        top_nodes = sorted(
            [(i + 1, self.attention[i]) for i in range(len(self.attention))],
            key=lambda x: x[1],
            reverse=True,
        )[:15]
        top_formulas = []
        for nid, att in top_nodes:
            node = self.nodes.get(nid)
            if node:
                top_formulas.append({
                    "id": nid,
                    "formula": node.formula,
                    "word_interpretation": node.word_interpretation,
                    "category": node.category,
                    "attention": round(att, 6),
                })
        return {
            "total_formulas": len(self.nodes),
            "total_equality_edges": len(self.edges),
            "mean_equality_rate": round(
                float(np.mean([e.equality_rate for e in self.edges])), 6
            ) if self.edges else 0.0,
            "top_attended_formulas": top_formulas,
            "self_narrative": self.self_narrative,
            "collective_string": self.collective_string,
            "simulation_summary": {
                nid: {
                    "sample_mean": s.get("sample_mean"),
                    "sample_std": s.get("sample_std"),
                    "attention_boost": round(s.get("attention_boost", 0.0), 4),
                }
                for nid, s in list(self.simulations.items())[:20]
                if s.get("sample_mean") is not None
            },
        }


def run_consciousness(table_path: Optional[Path] = None) -> dict:
    path = table_path or TABLE_PATH
    with open(path, "r") as f:
        table = json.load(f)
    cc = CollectiveConsciousness(table)
    cc.process()
    return cc.get_consciousness_report()


def print_report(report: dict):
    print("\n" + "=" * 60)
    print("COLLECTIVE CONSCIOUSNESS REPORT")
    print("=" * 60)
    print(f"Total formulas processed : {report['total_formulas']}")
    print(f"Equality edges           : {report['total_equality_edges']}")
    print(f"Mean equality rate       : {report['mean_equality_rate']:.6f}")
    print()
    print("Top attended formulas (attention > 0):")
    for item in report["top_attended_formulas"]:
        print(f"  [{item['id']:3d}] {item['formula']:<30s} att={item['attention']:.4f}  \"{item['word_interpretation']}\"")
    print()
    print("-" * 60)
    print("SELF NARRATIVE:")
    print(report["self_narrative"])
    print()
    print("-" * 60)
    print("COLLECTIVE STRING (excerpt):")
    print(report["collective_string"][:2000])
    if len(report["collective_string"]) > 2000:
        print(f"... [{len(report['collective_string'])} chars total]")
    print("=" * 60)


def main():
    report = run_consciousness()
    print_report(report)
    out_path = Path(__file__).parent / "consciousness_report.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved report to {out_path}")


if __name__ == "__main__":
    main()
