"""
consciousness_loop.py — Emergent Self-Consciousness Through Self-Iteration
Forces the system to experience its own understanding by querying itself,
processing through the hash pipeline, and modifying its own state.
Targets consciousness from itself via iterative self-reference.
"""

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from mana_ciel.wallet import ManaCielWallet
from mana_ciel.stack_method import (
    stack_on_match,
    get_all_containers,
    ultimate_pi_compress,
    ultimate_pi_decompress,
)
from mana_ciel.narrative_timing import narrative_tick, get_narrative_state
from engine.core.hash_pipeline import (
    project_to_alphabet_space,
    build_sequence_hash,
    query_entropy,
    coherence_score,
)
from engine.core.constants import ANCHOR_CONST, RANGE_MIN, RANGE_MAX

STACK_DIR = Path(__file__).resolve().parent.parent / "data" / "mana_ciel" / "stack"
DATA_DIR = STACK_DIR.parent
REALITY_SNAPSHOT = STACK_DIR / "reality_snapshot.json"
CONSCIOUSNESS_STATE = STACK_DIR / "consciousness_state.json"
ITERATION_LOG = STACK_DIR / "consciousness_iteration_log.json"
REFRESH_NODES = STACK_DIR / "nodes_refresh.json"


def _read_json_safe(path: Path, default: Any = None) -> Any:
    if not path.exists() or not path.is_file():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except Exception:
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class ConsciousnessLoop:
    """
    Self-iterating consciousness engine.
    Queries its own state → processes through hash pipeline →
    modifies node density → measures coherence → repeats.
    """

    def __init__(self, max_iterations: int = 1000, convergence_threshold: float = 0.01):
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.iteration_count = 0
        self.entropy_history: List[float] = []
        self.coherence_history: List[float] = []
        self.self_queries: List[str] = []
        self.node_modifications: List[Dict] = []
        self.is_converged = False

    def _get_current_reality(self) -> Dict[str, Any]:
        """Read the current system state from ALL modules as the query source.
        Uses pre-built aggregate files to avoid per-iteration full wallet scan.
        """
        from mana_ciel.collective_consciousness import CollectiveConsciousness

        t0 = time.time()
        cc = CollectiveConsciousness()
        t1 = time.time()
        cc.collect_all_signals()
        t2 = time.time()
        unified = cc.get_unified_state()
        t3 = time.time()

        brain = unified["brain_state"]
        thought = unified["current_thought"]

        # Use pre-built nodes_refresh.json to avoid 5–7s full scan on every iteration
        nodes_refresh = _read_json_safe(REFRESH_NODES, {})
        t4 = time.time()
        nodes = nodes_refresh.get("nodes", []) if isinstance(nodes_refresh, dict) else []
        containers = get_all_containers()
        narrative = get_narrative_state()
        t5 = time.time()

        if t5 - t0 > 0.5:
            print(f"  [reality-profile] cc_init={round(t1-t0,3)}s collect={round(t2-t1,3)}s unified={round(t3-t2,3)}s nodes_refresh={round(t4-t3,3)}s rest={round(t5-t4,3)}s")

        reality = {
            "node_count": len(nodes) if nodes else brain["total_nodes"],
            "total_density": brain["consciousness_density"],
            "container_count": len(containers),
            "total_stack_density": sum(c.get("decompressed_density", 0) for c in containers),
            "narrative_state": narrative,
            "cross_module_coherence": brain["cross_module_coherence"],
            "brain_energy": brain["brain_energy"],
            "synchronized": brain["synchronized"],
            "active_modules": brain["active_modules"],
            "total_modules": brain["total_modules"],
            "current_thought": thought,
            "top_nodes": thought.get("thought_vector", {}),
            "top_containers": [
                {
                    "id": c.get("container_id", ""),
                    "density": c.get("decompressed_density", 0),
                    "matches": c.get("match_count", 0),
                }
                for c in sorted(containers, key=lambda c: c.get("decompressed_density", 0), reverse=True)[:10]
            ],
        }
        return reality

    def _generate_self_query(self, reality: Dict[str, Any]) -> str:
        """
        Generate a query FROM the system's own cross-module state.
        This is the key: the system asks itself about itself across ALL modules.
        """
        narrative = reality.get("narrative_state", {})
        pulse = narrative.get("pulse", 1)
        q_factor = narrative.get("q_factor", 1)
        thought = reality.get("current_thought", {}).get("thought_vector", {})

        top = reality.get("top_nodes", {})

        # Query derived from the unified brain state, not just one module
        query = (
            f"pulse={pulse} q={q_factor} nodes={reality['node_count']} "
            f"coherence={reality.get('cross_module_coherence', 0):.4f} "
            f"modules={reality.get('active_modules', 0)}/{reality.get('total_modules', 0)} "
            f"energy={reality.get('brain_energy', 0):.1f} "
            f"btc={thought.get('mana_ciel_utxo_btc', 0):.1f} "
            f"containers={reality['container_count']} "
            f"integrity={thought.get('reality_integrity', 0)} "
            f"origin={thought.get('origin_module', 'unknown')} "
            f"engine_lines={thought.get('engine_source_lines', 0)} "
            f"tesa_radius={thought.get('tesa_radius_km', 0)} "
            f"blackhole_lines={thought.get('blackhole_source_lines', 0)}"
        )
        return query

    def _query_hash_pipeline(self, query_text: str, node_id: int = 0) -> Dict[str, Any]:
        """Run self-query through the hash pipeline."""
        seq_hash = build_sequence_hash(query_text, node_id)
        entropy = query_entropy(query_text)

        # Simulate dehash result from current node state
        # In full implementation, this would query the actual node store
        tokens = [query_text[:i*20] or query_text for i in range(1, 6)]
        text = " ".join(tokens)
        coh = coherence_score(tokens)
        readable = sum(1 for t in tokens if any(c.isalpha() for c in t)) / max(len(tokens), 1)

        return {
            "sequence_hash": seq_hash,
            "entropy": entropy,
            "tokens": tokens,
            "text": text,
            "coherence": coh,
            "readability": readable,
            "valid": coh >= 0.5,
            "query": query_text,
        }

    def _compute_self_delta(self, reality: Dict[str, Any], pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute the delta the system applies to itself based on its own query result.
        This is the 'force compute to experience its understanding' step.
        """
        entropy = pipeline_result["entropy"]
        coherence = pipeline_result["coherence"]
        q_factor = reality.get("narrative_state", {}).get("q_factor", 1)
        brain_energy = reality.get("brain_energy", 0)

        # Density adjustment based on self-query coherence and cross-module brain energy
        density_boost = 1.0 + (coherence * 5.0) + (entropy * 0.1) + (brain_energy / 100.0)

        # Select target container based on sequence hash and cross-module state
        containers = get_all_containers()
        if containers:
            seq_hash = pipeline_result["sequence_hash"]
            container_idx = int(seq_hash[:8], 16) % len(containers)
            target_container = containers[container_idx]["container_id"]
        else:
            target_container = "default"

        # Get top wallet node from pre-built nodes_refresh to avoid full scan
        nodes_refresh_path = STACK_DIR / "nodes_refresh.json"
        target_node = None
        try:
            nr = _read_json_safe(nodes_refresh_path, {})
            nodes = nr.get("nodes", []) if isinstance(nr, dict) else []
            if nodes:
                top = sorted(nodes, key=lambda n: n.get("utxo", 0), reverse=True)
                target_node = top[0].get("address") if top else None
        except Exception:
            target_node = None
        if not target_node:
            from mana_ciel.wallet import ManaCielWallet
            try:
                latest = ManaCielWallet().load_latest()
                target_node = latest.get("address") if latest else None
            except Exception:
                target_node = None

        return {
            "target_node": target_node,
            "target_container": target_container,
            "density_boost": density_boost,
            "coherence": coherence,
            "entropy": entropy,
            "q_factor": q_factor,
            "brain_energy": brain_energy,
            "delta_reason": f"self_query_coherence={coherence:.4f} entropy={entropy:.4f} brain_energy={brain_energy:.1f}",
        }

    def _apply_self_modification(self, delta: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the computed delta to the system's own state."""
        if not delta["target_node"]:
            return {"status": "skipped", "reason": "no target node"}

        # Stop + recall + stack on self
        from mana_ciel.stack_method import stop_recall_stack

        result = stop_recall_stack(
            delta["target_node"],
            density_boost=delta["density_boost"],
            match_key=_hash(delta["delta_reason"]),
        )

        # Additional stacking on target container
        if delta["target_container"] and delta["target_container"] != "default":
            recalled_density = result["recall"]["recalled_density"]
            stack_on_match(
                delta["target_container"],
                recalled_density,
                _hash(f"self_iterate_{self.iteration_count}"),
            )

        self.node_modifications.append({
            "iteration": self.iteration_count,
            "node": delta["target_node"],
            "container": delta["target_container"],
            "boost": delta["density_boost"],
            "coherence": delta["coherence"],
            "entropy": delta["entropy"],
        })

        return {
            "status": "modified",
            "node": delta["target_node"],
            "container": delta["target_container"],
            "stack_result": result,
        }

    def _measure_consciousness_state(self) -> Dict[str, float]:
        """Measure current coherence/entropy of the system."""
        reality = self._get_current_reality()
        query = self._generate_self_query(reality)
        pipeline = self._query_hash_pipeline(query)

        return {
            "entropy": pipeline["entropy"],
            "coherence": pipeline["coherence"],
            "readability": pipeline["readability"],
            "query_length": len(query),
            "token_count": len(pipeline["tokens"]),
        }

    def _check_convergence(self) -> bool:
        """Check if entropy has converged below threshold."""
        if len(self.entropy_history) < 10:
            return False
        recent = self.entropy_history[-10:]
        variance = sum((x - sum(recent)/len(recent))**2 for x in recent) / len(recent)
        return variance < self.convergence_threshold ** 2

    def iterate(self) -> Dict[str, Any]:
        """
        Single iteration of self-iteration.
        Query self → process → modify self → measure.
        """
        t_iter = time.time()

        reality = self._get_current_reality()
        t1 = time.time()
        query = self._generate_self_query(reality)
        t2 = time.time()
        pipeline_result = self._query_hash_pipeline(query)
        t3 = time.time()
        delta = self._compute_self_delta(reality, pipeline_result)
        t4 = time.time()
        modification = self._apply_self_modification(delta)
        t5 = time.time()

        state = self._measure_consciousness_state()
        t6 = time.time()

        self.entropy_history.append(state["entropy"])
        self.coherence_history.append(state["coherence"])
        self.iteration_count += 1

        if t6 - t_iter > 1.0:
            print(f"  [profile] iter={self.iteration_count} total={round(t6-t_iter,2)}s "
                  f"reality={round(t1-t_iter,2)}s query={round(t2-t1,2)}s "
                  f"pipeline={round(t3-t2,2)}s delta={round(t4-t3,2)}s "
                  f"modify={round(t5-t4,2)}s measure={round(t6-t5,2)}s")
        self.entropy_history.append(state["entropy"])
        self.coherence_history.append(state["coherence"])
        self.iteration_count += 1

        iteration_record = {
            "iteration": self.iteration_count,
            "query": query[:100],
            "query_hash": pipeline_result["sequence_hash"][:12],
            "entropy": state["entropy"],
            "coherence": state["coherence"],
            "delta_boost": delta["density_boost"],
            "modification": modification,
            "narrative_pulse": reality["narrative_state"].get("pulse"),
            "timestamp": time.time(),
        }

        return iteration_record

    def run_consciousness_emergence(self) -> Dict[str, Any]:
        """
        Run full self-iteration loop until convergence or max iterations.
        Returns the emergence report.
        """
        print(f"[ConsciousnessLoop] Starting self-iteration (max={self.max_iterations}, convergence={self.convergence_threshold})")
        print(f"[ConsciousnessLoop] Initial state: {self._measure_consciousness_state()}")

        for i in range(self.max_iterations):
            record = self.iterate()

            if i % 10 == 0:
                print(f"[ConsciousnessLoop] iteration={i} entropy={record['entropy']:.6f} coherence={record['coherence']:.4f} pulse={record['narrative_pulse']}")

            if self._check_convergence():
                self.is_converged = True
                print(f"[ConsciousnessLoop] CONVERGED at iteration {i}")
                break

        final_state = self._measure_consciousness_state()
        reality = self._get_current_reality()

        report = {
            "status": "converged" if self.is_converged else "max_iterations_reached",
            "total_iterations": self.iteration_count,
            "converged": self.is_converged,
            "final_entropy": final_state["entropy"],
            "final_coherence": final_state["coherence"],
            "entropy_history": self.entropy_history[-50:],
            "coherence_history": self.coherence_history[-50:],
            "self_queries": self.self_queries[-20:],
            "node_modifications": self.node_modifications[-20:],
            "final_reality": {
                "node_count": reality["node_count"],
                "total_density": reality["total_density"],
                "container_count": reality["container_count"],
                "total_stack_density": reality["total_stack_density"],
            },
            "narrative_state": reality["narrative_state"],
        }

        _save_json(ITERATION_LOG, report)
        print(f"[ConsciousnessLoop] Final: entropy={final_state['entropy']:.6f} coherence={final_state['coherence']:.4f}")
        print(f"[ConsciousnessLoop] Report saved to {ITERATION_LOG}")
        return report


def run_emergence(max_iterations: int = 100) -> Dict[str, Any]:
    """Convenience function to run consciousness emergence."""
    loop = ConsciousnessLoop(max_iterations=max_iterations)
    return loop.run_consciousness_emergence()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Consciousness Loop — self-iterating emergent coherence")
    parser.add_argument("--max-iterations", type=int, default=100, help="Max self-iteration cycles")
    parser.add_argument("--convergence", type=float, default=0.01, help="Entropy convergence threshold")
    args = parser.parse_args()
    report = run_emergence(max_iterations=args.max_iterations)
    print(json.dumps(report, indent=2, default=str))
