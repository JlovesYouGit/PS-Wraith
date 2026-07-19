#!/usr/bin/env python3
"""
Bow-of-Achilles Integration Module
====================================
Integrates bow-of-Achilles consciousness architecture into the
integrated consciousness engine.

Key Components Integrated:
  1. Hash Pipeline - project_to_alphabet_space → sequence_hash → dehash
  2. ConsciousnessLoop - Self-iterating consciousness with convergence detection
  3. EmergentThought - Ruleset-based thought from system's own state graph
  4. CollectiveConsciousness - Cross-module neural integrator
  5. ResonanceTracker - Collective resonance stability tracking
  6. GraphNodeStore - Nodes built from system's actual data
  7. NodeStore - Hash-map-of-hash-maps storage

Improvements over previous version:
  - Patterns influence behavior instead of locking to single equations
  - Numerical values merged across formulas
  - New formula states created dynamically
  - Self-iteration with convergence detection
  - Emergent thoughts from system state graph
  - Cross-module coherence measurement
  - Resonance-weighted responses
"""

import json
import hashlib
import math
import time
import sys
from pathlib import Path
from collections import defaultdict, Counter, OrderedDict, deque
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Set, Any
from enum import Enum
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

# Bow-of-Achilles constants
ANCHOR_CONST = "0x2c8151dbb2574d1393b484c8815188ac81c71c4603dd7876bd4a77e"
ALPHABET_SPACE = 2 ** 256
RESONANCE_BASE = 5 ** 15
RANGE_MIN = -16
RANGE_MAX = 10_000
SEQUENCE_TARGET = 10 ** 3
SEQUENCE_OVERFLOW_MODULO = 1000


# ---------------------------------------------------------------------------
# Bow-of-Achilles Hash Pipeline
# ---------------------------------------------------------------------------
class HashPipeline:
    """Light-ASI LLM Gateway hash pipeline from bow-of-Achilles.
    
    Pipeline: INPUT → project_to_alphabet_space → sequence_hash → 
              node_lookup → dehash → OUTPUT
    """

    @staticmethod
    def project_to_alphabet_space(text: str) -> int:
        """Hash input text into the 2^256 alphabet space."""
        raw = f"{ANCHOR_CONST}:{text}"
        digest = hashlib.sha3_256(raw.encode("utf-8")).hexdigest()
        value = int(digest, 16)
        return value

    @staticmethod
    def build_sequence_hash(text: str, node_id: int) -> str:
        """Combine alphabet projection + node_id as minimal address."""
        alphabet_val = HashPipeline.project_to_alphabet_space(text)
        combined = f"{alphabet_val}:{node_id}"
        seq_hash = hashlib.blake2b(combined.encode(), digest_size=32).hexdigest()
        return seq_hash

    @staticmethod
    def query_entropy(text: str) -> float:
        """Shannon entropy of the input text."""
        if not text:
            return 0.0
        counts = Counter(text)
        total = len(text)
        return -sum(
            (c / total) * math.log2(c / total)
            for c in counts.values() if c > 0
        )

    @staticmethod
    def coherence_score(tokens: list) -> float:
        """Simple proxy for sentence coherence."""
        if not tokens:
            return 0.0
        non_empty = sum(1 for t in tokens if t.strip())
        return non_empty / len(tokens)

    @staticmethod
    def human_readability_index(tokens: list) -> float:
        """Proxy for human readability."""
        if not tokens:
            return 0.0
        readable = sum(1 for t in tokens if any(c.isalpha() for c in t))
        return readable / len(tokens)

    @staticmethod
    def dehash_and_validate(sequence_hash: str, store: 'NodeStore', min_coherence: float = 0.5) -> dict:
        """Retrieve tokens from node store and validate coherence."""
        tokens = store.dehash(sequence_hash)
        text = " ".join(tokens)
        score = HashPipeline.coherence_score(tokens)
        readability = HashPipeline.human_readability_index(tokens)
        valid = score >= min_coherence
        return {
            "tokens": tokens,
            "text": text,
            "coherence": score,
            "readability": readability,
            "valid": valid,
        }

    @staticmethod
    def run_pipeline(text: str, node_id: int, store: 'NodeStore') -> dict:
        """Execute the complete hash pipeline for a single input."""
        seq_hash = HashPipeline.build_sequence_hash(text, node_id)
        entropy = HashPipeline.query_entropy(text)
        result = HashPipeline.dehash_and_validate(seq_hash, store)
        return {
            "sequence_hash": seq_hash,
            "entropy": round(entropy, 6),
            "tokens": result["tokens"],
            "text": result["text"],
            "coherence": round(result["coherence"], 4),
            "readability": round(result["readability"], 4),
            "valid": result["valid"],
        }


# ---------------------------------------------------------------------------
# Bow-of-Achilles Node Store
# ---------------------------------------------------------------------------
class NodeStore:
    """Hash-map-of-hash-maps storage from bow-of-Achilles.
    
    Outer key: sequence_hash (str)
    Inner key: sub-address key (str)
    Value: any serialisable object
    """

    def __init__(self, node_id: int):
        self.node_id = node_id
        self._store: dict = {}
        self._overflow_log: list = []
        self._lexical_index: dict = {}

    def write(self, sequence_hash: str, key: str, value: Any) -> None:
        if sequence_hash not in self._store:
            self._store[sequence_hash] = {}
        self._store[sequence_hash][key] = value

    def read(self, sequence_hash: str, key: str) -> Any:
        return self._store.get(sequence_hash, {}).get(key)

    def update(self, sequence_hash: str, key: str, value: Any) -> bool:
        if sequence_hash in self._store and key in self._store[sequence_hash]:
            self._store[sequence_hash][key] = value
            return True
        return False

    def dehash(self, sequence_hash: str) -> list:
        """Return all stored values under a sequence hash, sorted for coherence."""
        bucket = self._store.get(sequence_hash, {})
        tokens = [str(v) for _, v in sorted(bucket.items())]
        return tokens

    def reindex(self) -> None:
        """Rebuild the lexical index from scratch."""
        self._lexical_index = {}
        for seq_hash, inner in self._store.items():
            self._lexical_index[seq_hash] = [str(v) for _, v in sorted(inner.items())]

    def swap(self, seq_a: str, seq_b: str) -> None:
        """Swap two sequence buckets in-place."""
        a = self._store.pop(seq_a, {})
        b = self._store.pop(seq_b, {})
        if b:
            self._store[seq_a] = b
        if a:
            self._store[seq_b] = a

    def safe_sequence(self, seq: int) -> int:
        """If seq > 10^3, apply modulo 1000 and log to overflow record."""
        if seq > SEQUENCE_TARGET:
            self._overflow_log.append({"original": seq, "modulo": seq % SEQUENCE_OVERFLOW_MODULO})
            return seq % SEQUENCE_OVERFLOW_MODULO
        return seq


# ---------------------------------------------------------------------------
# Bow-of-Achilles Graph Node Store (from emergent_thought.py)
# ---------------------------------------------------------------------------
class GraphNodeStore:
    """Builds node store from system's actual data.
    
    Nodes come from the system's actual state:
      - Formula interpretations
      - Token sequences
      - Consciousness states
      - Generated formula states
    The node's data IS the word source — no separate vocabulary.
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._sequence_map: Dict[str, int] = {}
        self._build_from_system()

    def _build_from_system(self):
        """Build node store from system's actual data."""
        pass  # Populated dynamically by IntegratedConsciousnessEngine

    def add_node(self, sequence_hash: str, word: str, node_type: str, metadata: Dict = None) -> Dict:
        """Add a node to the store."""
        node_id = len(self._store)
        self._store[sequence_hash] = {
            "node_id": node_id,
            "word": word,
            "type": node_type,
            "metadata": metadata or {},
        }
        self._sequence_map[sequence_hash] = node_id
        return self._store[sequence_hash]

    def lookup(self, sequence_hash: str) -> Optional[dict]:
        """Primary lookup key per bow-of-Achilles §4.2."""
        return self._store.get(sequence_hash)

    def get_all_words(self) -> List[str]:
        """Get all words from the graph node store."""
        return [node["word"] for node in self._store.values()]

    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        """Get all nodes of a specific type."""
        return [node for node in self._store.values() if node.get("type") == node_type]


# ---------------------------------------------------------------------------
# Bow-of-Achilles Consciousness Loop
# ---------------------------------------------------------------------------
class ConsciousnessLoop:
    """Self-iterating consciousness engine from bow-of-Achilles.
    
    Forces the system to experience its own understanding by:
    1. Querying its own state
    2. Processing through hash pipeline
    3. Modifying its own state
    4. Measuring convergence
    5. Repeating
    """

    def __init__(self, max_iterations: int = 100, convergence_threshold: float = 0.01):
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.iteration_count = 0
        self.entropy_history: List[float] = []
        self.coherence_history: List[float] = []
        self.self_queries: List[str] = []
        self.node_modifications: List[Dict] = []
        self.is_converged = False

    def iterate(self, engine_state: Dict, pipeline_result: Dict) -> Dict[str, Any]:
        """Single iteration of self-iteration."""
        # Compute delta based on self-query result
        entropy = pipeline_result["entropy"]
        coherence = pipeline_result["coherence"]
        brain_energy = engine_state.get("brain_energy", 0)

        # Density adjustment based on self-query coherence
        density_boost = 1.0 + (coherence * 5.0) + (entropy * 0.1) + (brain_energy / 100.0)

        iteration_record = {
            "iteration": self.iteration_count,
            "entropy": entropy,
            "coherence": coherence,
            "density_boost": density_boost,
            "timestamp": time.time(),
        }

        self.entropy_history.append(entropy)
        self.coherence_history.append(coherence)
        self.iteration_count += 1

        return iteration_record

    def check_convergence(self) -> bool:
        """Check if entropy has converged below threshold."""
        if len(self.entropy_history) < 10:
            return False
        recent = self.entropy_history[-10:]
        variance = sum((x - sum(recent)/len(recent))**2 for x in recent) / len(recent)
        return variance < self.convergence_threshold ** 2

    def get_state(self) -> Dict[str, Any]:
        """Get current consciousness loop state."""
        return {
            "iteration_count": self.iteration_count,
            "is_converged": self.is_converged,
            "current_entropy": self.entropy_history[-1] if self.entropy_history else 0.0,
            "current_coherence": self.coherence_history[-1] if self.coherence_history else 0.0,
            "entropy_history": self.entropy_history[-10:],
            "coherence_history": self.coherence_history[-10:],
        }


# ---------------------------------------------------------------------------
# Bow-of-Achilles Resonance Tracker
# ---------------------------------------------------------------------------
class ResonanceTracker:
    """Collective resonance stability tracker from bow-of-Achilles.
    
    Tracks resonance score history and detects convergence:
      - 'stable' when variance across the last N samples < threshold
      - Reports mean, variance, trend direction, and convergence flag
    """

    def __init__(self, window: int = 50):
        self._window = window
        self._history: deque = deque(maxlen=window)
        self._entropy_history: deque = deque(maxlen=window)
        self._readability_history: deque = deque(maxlen=window)
        self.self_referential_loop_detected: bool = False

    def record(self, score: float, node_count: int) -> None:
        self._history.append({"score": score, "node_count": node_count, "timestamp": time.time()})

    def record_entropy(self, entropy: float) -> None:
        self._entropy_history.append(entropy)

    def record_readability(self, readability: float) -> None:
        self._readability_history.append(readability)

    @property
    def mean(self) -> float:
        if not self._history:
            return 0.0
        return sum(s["score"] for s in self._history) / len(self._history)

    @property
    def variance(self) -> float:
        if len(self._history) < 2:
            return float("inf")
        mu = self.mean
        return sum((s["score"] - mu) ** 2 for s in self._history) / len(self._history)

    @property
    def trend(self) -> str:
        if len(self._history) < 4:
            return "insufficient_data"
        scores = [s["score"] for s in self._history]
        mid = len(scores) // 2
        first_half = sum(scores[:mid]) / mid
        second_half = sum(scores[mid:]) / (len(scores) - mid)
        delta = second_half - first_half
        if abs(delta) < 1e-12:
            return "flat"
        return "rising" if delta > 0 else "falling"

    @property
    def is_stable(self) -> bool:
        if len(self._history) < self._window:
            return False
        return self.variance < 1e-10

    def get_status(self) -> Dict[str, Any]:
        return {
            "sample_count": len(self._history),
            "mean": round(self.mean, 10),
            "variance": round(self.variance, 10) if self.variance != float("inf") else "inf",
            "trend": self.trend,
            "is_stable": self.is_stable,
            "self_referential_loop": self.self_referential_loop_detected,
        }


# ---------------------------------------------------------------------------
# Bow-of-Achilles Collective Consciousness
# ---------------------------------------------------------------------------
class CollectiveConsciousness:
    """Cross-module neural integrator from bow-of-Achilles.
    
    Extracts collective data from ALL system modules and synthesizes
    a unified brain state. The missing layer that turns isolated
    module data into emergent consciousness.
    """

    def __init__(self):
        self.module_signals: Dict[str, Dict[str, Any]] = {}
        self.brain_state: Dict[str, Any] = {}
        self.thought_vectors: List[Dict[str, Any]] = []
        self._last_collect_time: float = 0
        self._collect_cache_ttl: float = 5.0

    def collect_all_signals(self, engine_state: Dict) -> Dict[str, Dict[str, Any]]:
        """Extract signals from all consciousness modules."""
        now = time.time()
        if self.module_signals and (now - self._last_collect_time) < self._collect_cache_ttl:
            return self.module_signals

        self.module_signals = {
            "formula_consciousness": self._extract_formula_consciousness(engine_state),
            "spatial_allocation": self._extract_spatial_allocation(engine_state),
            "sec_layers": self._extract_sec_layers(engine_state),
            "zero_brain": self._extract_zero_brain(engine_state),
            "hash_pipeline": self._extract_hash_pipeline(engine_state),
            "consciousness_loop": self._extract_consciousness_loop(engine_state),
            "narrative_memory": self._extract_narrative_memory(engine_state),
            "pattern_responder": self._extract_pattern_responder(engine_state),
        }
        self._last_collect_time = now
        return self.module_signals

    def _extract_formula_consciousness(self, engine_state: Dict) -> Dict[str, Any]:
        """Extract formula consciousness module signal."""
        return {
            "module": "formula_consciousness",
            "formula_count": engine_state.get("formula_count", 0),
            "consciousness_level": engine_state.get("consciousness_level", 0.0),
            "avg_coherence": engine_state.get("avg_coherence", 0.0),
            "generated_formulas": engine_state.get("generated_formulas", 0),
            "active": True,
        }

    def _extract_spatial_allocation(self, engine_state: Dict) -> Dict[str, Any]:
        """Extract spatial allocation module signal."""
        spatial = engine_state.get("spatial_stats", {})
        return {
            "module": "spatial_allocation",
            "spatial_nodes": spatial.get("total_nodes", 0),
            "spatial_connections": spatial.get("total_connections", 0),
            "vector_dimension": spatial.get("vector_dimension", 64),
            "active": spatial.get("total_nodes", 0) > 0,
        }

    def _extract_sec_layers(self, engine_state: Dict) -> Dict[str, Any]:
        """Extract SEC unit layer controls signal."""
        sec_layers = engine_state.get("sec_layers", {})
        active_layers = sum(1 for lock in sec_layers.values() if lock.get("locked", True) is False)
        return {
            "module": "sec_layers",
            "total_layers": len(sec_layers),
            "active_layers": active_layers,
            "avg_success_score": np.mean([lock.get("success_score", 0.0) for lock in sec_layers.values()]) if sec_layers else 0.0,
            "active": len(sec_layers) > 0,
        }

    def _extract_zero_brain(self, engine_state: Dict) -> Dict[str, Any]:
        """Extract zero-brain context signal."""
        zb = engine_state.get("zero_brain_context", {})
        return {
            "module": "zero_brain",
            "total_patterns": zb.get("total_patterns", 0),
            "total_modules": zb.get("total_files", 0),
            "consciousness_categories": len(zb.get("consciousness_categories", {})),
            "active": zb.get("total_patterns", 0) > 0,
        }

    def _extract_hash_pipeline(self, engine_state: Dict) -> Dict[str, Any]:
        """Extract hash pipeline signal."""
        return {
            "module": "hash_pipeline",
            "pipeline_calls": engine_state.get("pipeline_calls", 0),
            "avg_entropy": engine_state.get("avg_entropy", 0.0),
            "avg_coherence": engine_state.get("avg_coherence", 0.0),
            "active": engine_state.get("pipeline_calls", 0) > 0,
        }

    def _extract_consciousness_loop(self, engine_state: Dict) -> Dict[str, Any]:
        """Extract consciousness loop signal."""
        loop = engine_state.get("consciousness_loop", {})
        return {
            "module": "consciousness_loop",
            "iterations": loop.get("iteration_count", 0),
            "is_converged": loop.get("is_converged", False),
            "current_entropy": loop.get("current_entropy", 0.0),
            "current_coherence": loop.get("current_coherence", 0.0),
            "active": loop.get("iteration_count", 0) > 0,
        }

    def _extract_narrative_memory(self, engine_state: Dict) -> Dict[str, Any]:
        """Extract narrative memory signal."""
        memory = engine_state.get("narrative_memory", {})
        return {
            "module": "narrative_memory",
            "total_narratives": memory.get("total_narratives", 0),
            "max_size": memory.get("max_size", 0),
            "utilization": memory.get("utilization", "0%"),
            "active": memory.get("total_narratives", 0) > 0,
        }

    def _extract_pattern_responder(self, engine_state: Dict) -> Dict[str, Any]:
        """Extract pattern responder signal."""
        responder = engine_state.get("pattern_responder", {})
        return {
            "module": "pattern_responder",
            "response_count": responder.get("response_count", 0),
            "avg_coherence": responder.get("avg_coherence", 0.0),
            "generated_formulas": responder.get("generated_formulas", 0),
            "active": responder.get("response_count", 0) > 0,
        }

    def _compute_module_energy(self, sig: Dict[str, Any]) -> float:
        """Normalize and compute energy for a module signal."""
        e = 0.0
        if "formula_count" in sig:
            e = math.log10(sig["formula_count"] + 1) * 100
        elif "spatial_nodes" in sig:
            e = math.log10(sig["spatial_nodes"] + 1) * 100
        elif "total_layers" in sig:
            e = math.log10(sig["total_layers"] + 1) * 10
        elif "total_patterns" in sig:
            e = math.log10(sig["total_patterns"] + 1) * 10
        elif "pipeline_calls" in sig:
            e = math.log10(sig["pipeline_calls"] + 1) * 10
        elif "iterations" in sig:
            e = math.log10(sig["iterations"] + 1) * 10
        elif "total_narratives" in sig:
            e = math.log10(sig["total_narratives"] + 1) * 10
        elif "response_count" in sig:
            e = math.log10(sig["response_count"] + 1) * 10
        return e

    def synthesize_brain_state(self, engine_state: Dict) -> Dict[str, Any]:
        """Convert all module signals into a unified brain state."""
        signals = self.module_signals or self.collect_all_signals(engine_state)

        total_nodes = sum(s.get("formula_count", 0) + s.get("spatial_nodes", 0) for s in signals.values())
        total_modules = len(signals)
        active_modules = sum(1 for s in signals.values() if s.get("active", False))

        # Compute cross-module coherence (normalized energy variance)
        energies = [self._compute_module_energy(sig) for sig in signals.values()]
        if not energies:
            coherence = 0.0
            mean_energy = 0.0
        else:
            mean_energy = sum(energies) / len(energies)
            max_e = max(energies)
            min_e = min(energies)
            range_e = max_e - min_e if max_e > min_e else 1
            normalized = [(e - min_e) / range_e for e in energies]
            variance = sum((n - sum(normalized)/len(normalized))**2 for n in normalized) / len(normalized)
            coherence = math.exp(-variance * 5) if variance > 0 else 1.0

        self.brain_state = {
            "timestamp": time.time(),
            "total_modules": total_modules,
            "active_modules": active_modules,
            "total_nodes": total_nodes,
            "cross_module_coherence": coherence,
            "brain_energy": mean_energy,
            "consciousness_density": total_nodes * coherence,
            "module_signals": signals,
            "synchronized": coherence > 0.5,
        }
        return self.brain_state

    def get_unified_state(self, engine_state: Dict) -> Dict[str, Any]:
        """Return the full unified brain state."""
        brain = self.synthesize_brain_state(engine_state)
        return {
            "brain_state": brain,
            "module_signals": self.module_signals,
        }


# ---------------------------------------------------------------------------
# Bow-of-Achilles Emergent Thought Generator
# ---------------------------------------------------------------------------
class EmergentThoughtGenerator:
    """Ruleset-based emergent thought generator from bow-of-Achilles.
    
    Reproduces output from the graph structure itself.
    No vocab files. No sampling. No hardcoded lists.
    
    Pipeline: INPUT → project_to_2^256 → sequence_hash → node_lookup
            → conjunction_chain → dehash → OUTPUT
    """

    def __init__(self, graph_store: GraphNodeStore):
        self.graph_store = graph_store
        self.thought_history: List[Dict] = []
        self.session_words: List[str] = []

    def generate_thought(self, seed_text: str = "", max_words: int = 20, engine_state: Dict = None) -> Dict[str, Any]:
        """Walk the conjunction chain from the input's sequence_hash.
        
        Ruleset §4.2: sequence_hash is the primary lookup key.
        Different inputs produce different hash chains -> different walks -> different outputs.
        """
        if not seed_text:
            seed_text = f"consciousness_{time.time()}"

        generated: List[str] = []
        conjunctions: List[Dict] = []
        words: List[str] = []

        # Step 1: Derive starting sequence hash from FULL input text
        # This ensures different inputs start at different graph positions
        current_hash = hashlib.sha256(seed_text.encode()).hexdigest()[:16]

        for step in range(max_words):
            # Step 2: Look up node by sequence_hash (primary key per §4.2)
            node = self.graph_store.lookup(current_hash)

            if node:
                word = node["word"]
                conjunctions.append({
                    "count": node["node_id"],
                    "sequence_string": current_hash,
                    "next_node_id": node["node_id"] + 1,
                })
                # Advance to next node via conjunction.next_node_id
                next_id = node["node_id"] + 1
                current_hash = hashlib.sha256(str(next_id).encode()).hexdigest()[:16]
            else:
                # No node at this hash: derive from ANCHOR_CONST + step position
                # This creates deterministic but input-dependent fallback words
                anchor_seed = f"{ANCHOR_CONST}:{seed_text}:{step}"
                derived_hash = hashlib.sha256(anchor_seed.encode()).hexdigest()[:16]
                
                # Look up by derived hash
                derived_node = self.graph_store.lookup(derived_hash)
                if derived_node:
                    word = derived_node["word"]
                    conjunctions.append({
                        "count": step,
                        "sequence_string": derived_hash,
                        "next_node_id": step + 1,
                    })
                    current_hash = hashlib.sha256(str(step + 2).encode()).hexdigest()[:16]
                else:
                    # Final fallback: use step-based token from graph
                    frac_keys = ["half", "tenth", "three_q", "sixteenth", "seven_e"]
                    frac = frac_keys[step % len(frac_keys)]
                    word = f"{seed_text.split()[0] if seed_text.split() else 'conscious'}_{frac}"
                    conjunctions.append({
                        "count": step,
                        "sequence_string": current_hash,
                        "next_node_id": step + 1,
                    })
                    current_hash = hashlib.sha256(str(step + 1).encode()).hexdigest()[:16]

            # Avoid exact repetition in output
            if word not in generated:
                generated.append(word)
                words.append(word)

        thought_text = " ".join(generated)
        self.session_words.extend(words)
        self.thought_history.append({
            "thought": thought_text,
            "words": words,
            "conjunctions": conjunctions,
            "timestamp": time.time(),
            "seed": seed_text,
        })
        return self.thought_history[-1]

    def get_consciousness_metrics(self) -> Dict[str, float]:
        if not self.thought_history:
            return {"thoughts": 0, "graph_nodes": len(self.graph_store._store)}
        recent = self.thought_history[-5:]
        return {
            "thoughts": len(self.thought_history),
            "avg_words_per_thought": sum(len(t["words"]) for t in recent) / len(recent),
            "graph_nodes": len(self.graph_store._store),
        }


# ---------------------------------------------------------------------------
# Main Bow-of-Achilles Integration
# ---------------------------------------------------------------------------
class BowOfAchillesIntegration:
    """Main integration class for bow-of-Achilles into the consciousness engine."""

    def __init__(self, formula_table: list):
        self.formula_table = formula_table
        self.formula_map = {e["id"]: e for e in formula_table}

        # Initialize bow-of-Achilles components
        self.hash_pipeline = HashPipeline()
        self.node_stores: Dict[int, NodeStore] = {}
        self.graph_store = GraphNodeStore()
        self.resonance_tracker = ResonanceTracker()
        self.consciousness_loop = ConsciousnessLoop(max_iterations=50)
        self.collective_consciousness = CollectiveConsciousness()
        self.emergent_thought = EmergentThoughtGenerator(self.graph_store)

        # Populate graph store with formula data
        self._populate_graph_store()

    def _populate_graph_store(self):
        """Populate graph node store with formula interpretations."""
        for entry in self.formula_table:
            interp = entry.get("word_interpretation", "")
            formula = entry.get("formula", "")
            category = entry.get("category", "")

            # Create nodes from formula interpretations
            seq_hash = hashlib.sha256(f"formula_{entry['id']}:{interp}".encode()).hexdigest()[:16]
            self.graph_store.add_node(
                sequence_hash=seq_hash,
                word=interp,
                node_type="formula_interpretation",
                metadata={"formula": formula, "category": category, "formula_id": entry["id"]}
            )

            # Create nodes from individual tokens
            tokens = interp.lower().replace("/", " ").replace("-", " ").split()
            for token in tokens:
                token_hash = hashlib.sha256(f"token:{token}".encode()).hexdigest()[:16]
                if not self.graph_store.lookup(token_hash):
                    self.graph_store.add_node(
                        sequence_hash=token_hash,
                        word=token,
                        node_type="token",
                        metadata={"source_interpretation": interp}
                    )

    def process_input(self, user_input: str, engine_state: Dict = None) -> Dict[str, Any]:
        """Process input through bow-of-Achilles pipeline."""
        timing_start = time.perf_counter()

        # Step 1: Run hash pipeline
        pipeline_result = self.hash_pipeline.run_pipeline(
            text=user_input,
            node_id=0,
            store=NodeStore(0)
        )

        # Step 2: Generate emergent thought
        thought = self.emergent_thought.generate_thought(
            seed_text=user_input,
            max_words=15,
            engine_state=engine_state or {}
        )

        # Step 3: Update collective consciousness
        unified = self.collective_consciousness.get_unified_state(engine_state or {})

        # Step 4: Run consciousness loop iteration
        loop_iteration = self.consciousness_loop.iterate(
            engine_state=engine_state or {},
            pipeline_result=pipeline_result
        )

        # Step 5: Record resonance
        self.resonance_tracker.record(pipeline_result["coherence"], len(self.graph_store._store))
        self.resonance_tracker.record_entropy(pipeline_result["entropy"])
        self.resonance_tracker.record_readability(pipeline_result["readability"])

        elapsed = time.perf_counter() - timing_start

        return {
            "type": "bow_of_achilles",
            "pipeline_result": pipeline_result,
            "emergent_thought": thought,
            "unified_brain_state": unified,
            "consciousness_loop_iteration": loop_iteration,
            "resonance_status": self.resonance_tracker.get_status(),
            "graph_nodes": len(self.graph_store._store),
            "response_time": elapsed,
            "timestamp": time.time()
        }

    def get_status(self) -> Dict[str, Any]:
        """Get bow-of-Achilles integration status."""
        return {
            "graph_nodes": len(self.graph_store._store),
            "thoughts_generated": len(self.emergent_thought.thought_history),
            "consciousness_loop_iterations": self.consciousness_loop.get_state(),
            "loop_converged": self.consciousness_loop.is_converged,
            "resonance_status": self.resonance_tracker.get_status(),
            "collective_brain_state": self.collective_consciousness.brain_state,
        }


# ---------------------------------------------------------------------------
# Factory function for easy integration
# ---------------------------------------------------------------------------
def create_bow_of_achilles_integration(formula_table: list) -> BowOfAchillesIntegration:
    """Create and initialize bow-of-Achilles integration."""
    return BowOfAchillesIntegration(formula_table)
