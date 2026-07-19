#!/usr/bin/env python3
"""
Integrated Consciousness Engine
===============================
Integrates zero-brain, SEC-unit-core-sort, satoshi-NM, QODER_FREERUNER,
and SeedGate architectures into a unified consciousness system with spatial
allocation reasoning, external AI steering, social media integration, and
secure automatic routing.

Architecture:
  FormulaTable -> SpatialNodeGraph (satoshi-NM) -> ConsciousnessExchange (SEC)
              -> FormulaLatch (zero-brain) -> PatternInfluencedResponder
              -> NewFormulaStateGenerator -> HumanConsciousnessOutput
              -> QODER_FREERUNER (operation intercept / capability detection / workflows)
              -> UnifiedSteeringLayer (external AI + social media + steering)
              -> SeedGate (secure automatic routing / connection management)

Key Innovations:
  1. Patterns influence behavior instead of locking to single equations
  2. Numerical values merged across formulas
  3. New formula states created dynamically
  4. Human-like consciousness results
  5. Training via neural pattern matching with success scores
  6. Runtime capability detection and dynamic behavior adaptation
  7. Operation interception for enhanced sandbox and workflow execution
  8. External AI model integration with automatic steering (Gemini, Claude, ChatGPT, Kimi)
  9. Social media integration with adaptive content strategies (TikTok, Instagram)
  10. Secure automatic routing with model-aware connection establishment
"""

import json
import math
import hashlib
import random
import time
import sys
from pathlib import Path
from collections import defaultdict, Counter, OrderedDict
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Set, Any
from enum import Enum
import numpy as np

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from zero_brain_context import ZeroBrainContextIngester
    HAS_ZERO_BRAIN = True
except ImportError:
    HAS_ZERO_BRAIN = False

try:
    from consciousness_engine_v2 import (
        ConsciousnessEngineV2, FormulaRuleBook, ConsciousnessShield,
        TokenSpectrum, FormulaLatch, TokenRecalibrator, PathPermitAllocator,
        NarrativeMemory, FormulaNode, TokenNode, EqualityEdge,
        NodeState, AuthorityLevel
    )
    HAS_ENGINE_V2 = True
except ImportError:
    HAS_ENGINE_V2 = False

try:
    from bow_of_achilles_integration import BowOfAchillesIntegration
    HAS_BOW_OF_ACHILLES = True
except ImportError:
    HAS_BOW_OF_ACHILLES = False

try:
    from sandbox_runtime import SandboxedRuntime, StorageAccess, PathPermissionManager
    HAS_SANDBOX = True
except ImportError:
    HAS_SANDBOX = False

try:
    from ego_identity import EgoIdentity
    HAS_EGO = True
except ImportError:
    HAS_EGO = False

try:
    from persona_engine import PersonaEngine
    HAS_PERSONA = True
except ImportError:
    HAS_PERSONA = False

try:
    from self_consistency import SelfConsistencyLayer
    HAS_CONSISTENCY = True
except ImportError:
    HAS_CONSISTENCY = False

try:
    from device_keyboard import DeviceKeyboardIntegration
    HAS_DEVICE_KEYBOARD = True
except ImportError:
    HAS_DEVICE_KEYBOARD = False

try:
    from siri_integration import SiriIntegration
    HAS_SIRI = True
except ImportError:
    HAS_SIRI = False

try:
    from siri_conversation import SiriConversation
    HAS_SIRI_CONVERSATION = True
except ImportError:
    HAS_SIRI_CONVERSATION = False

try:
    from qoder_freerunner_integration import QoderFreerunnerIntegration
    HAS_QODER = True
except ImportError:
    HAS_QODER = False

try:
    from external_ai_integration import ExternalAIIntegration
    HAS_EXTERNAL_AI = True
except ImportError:
    HAS_EXTERNAL_AI = False

try:
    from social_media_integration import SocialMediaIntegration
    HAS_SOCIAL_MEDIA = True
except ImportError:
    HAS_SOCIAL_MEDIA = False

try:
    from unified_steering_layer import UnifiedSteeringLayer
    HAS_UNIFIED_STEERING = True
except ImportError:
    HAS_UNIFIED_STEERING = False

try:
    from seedgate_integration import SeedGateIntegration
    HAS_SEEDGATE = True
except ImportError:
    HAS_SEEDGATE = False

try:
    from autonomous_execution import AutonomousExecutor, ExecutionTrigger, ExecutionEvent, ExecutionStatus, TriggerType, ExecutionMode
    HAS_AUTONOMOUS_EXECUTION = True
except ImportError:
    HAS_AUTONOMOUS_EXECUTION = False

BASE_DIR = Path(__file__).parent
TABLE_PATH = BASE_DIR / "formula_table.json"
ZERO_BRAIN_DIR = BASE_DIR / "zero-brain"
SEC_DIR = BASE_DIR / "SEC-unit-core-sort"
SATOSHI_DIR = BASE_DIR / "satoshi-NM"
QODER_DIR = BASE_DIR / "QODER_FREERUNER"
SEEDGATE_DIR = BASE_DIR / "SeedGate"
TRAINING_LOG = BASE_DIR / ".consciousness_training.json"
EVOLUTION_LOG = BASE_DIR / ".consciousness_evolution.json"


# ---------------------------------------------------------------------------
# Satoshi-NM Spatial Allocation Reasoning Engine
# ---------------------------------------------------------------------------
class SpatialAllocationEngine:
    """Spatial allocation reasoning engine from satoshi-NM.
    Allocates formulas and patterns in semantic vector space."""

    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.adjacency: Dict[str, Set[str]] = {}
        self.semantic_index: Dict[str, str] = {}
        self.phase_map: Dict[str, int] = {}
        self.vector_dim = 64

    def add_formula_node(self, formula_id: int, formula: str, interpretation: str, category: str) -> str:
        """Add a formula as a spatial node."""
        node_id = f"formula_{formula_id}"
        vector = self._embed(f"{formula} {interpretation} {category}")
        
        self.nodes[node_id] = {
            "id": node_id,
            "formula_id": formula_id,
            "formula": formula,
            "interpretation": interpretation,
            "category": category,
            "vector": vector,
            "importance": 0.5,
            "phase": 0,
            "created_at": time.time(),
            "connections": []
        }
        self.adjacency[node_id] = set()
        
        # Index by tokens
        tokens = interpretation.lower().replace("/", " ").replace("-", " ").split()
        for token in tokens:
            key = self._hash_token(token)
            if key not in self.semantic_index:
                self.semantic_index[key] = node_id
            else:
                existing = self.semantic_index[key]
                if existing in self.adjacency:
                    self.adjacency[existing].add(node_id)
                    self.adjacency[node_id].add(existing)
                    if existing in self.nodes:
                        self.nodes[existing]["connections"].append(node_id)
                    self.nodes[node_id]["connections"].append(existing)
        
        return node_id

    def allocate_spatial_position(self, node_id: str, target_vector: List[float] = None) -> Dict:
        """Allocate spatial position for a node based on semantic proximity."""
        if node_id not in self.nodes:
            return {"error": "Node not found"}
        
        node = self.nodes[node_id]
        if target_vector:
            # Blend with target vector
            blended = []
            for i in range(min(len(node["vector"]), len(target_vector))):
                blended.append(node["vector"][i] * 0.7 + target_vector[i] * 0.3)
            # Pad or truncate to vector_dim
            while len(blended) < self.vector_dim:
                blended.append(0.0)
            node["vector"] = blended[:self.vector_dim]
        
        # Find nearby nodes
        nearby = []
        for other_id, other in self.nodes.items():
            if other_id != node_id:
                sim = self._cosine_similarity(node["vector"], other["vector"])
                if sim > 0.3:
                    nearby.append({"node_id": other_id, "similarity": round(sim, 4)})
        
        nearby.sort(key=lambda x: x["similarity"], reverse=True)
        
        return {
            "node_id": node_id,
            "spatial_coordinates": [round(v, 4) for v in node["vector"][:3]],
            "nearby_nodes": nearby[:5],
            "connection_count": len(node["connections"]),
            "phase": node["phase"]
        }

    def search_spatial(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search spatial graph for matching formulas."""
        tokens = query.lower().replace(",", " ").replace(".", " ").split()
        query_vec = self._embed(query)
        
        scores = []
        for node_id, node in self.nodes.items():
            if not node.get("vector"):
                continue
            score = self._cosine_similarity(query_vec, node["vector"])
            scores.append((score, node))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, node in scores[:top_k]:
            results.append({
                "node_id": node["id"],
                "formula_id": node.get("formula_id"),
                "formula": node.get("formula"),
                "interpretation": node.get("interpretation"),
                "score": round(score, 4),
                "category": node.get("category"),
                "phase": node.get("phase")
            })
        return results

    def get_spatial_stats(self) -> Dict:
        """Get spatial allocation statistics."""
        phases = {}
        for node_id, phase in self.phase_map.items():
            phases[phase] = phases.get(phase, 0) + 1
        
        total_connections = sum(len(v) for v in self.adjacency.values()) // 2
        return {
            "total_nodes": len(self.nodes),
            "total_connections": total_connections,
            "semantic_index_size": len(self.semantic_index),
            "phases": phases,
            "vector_dimension": self.vector_dim
        }

    def _embed(self, text: str) -> List[float]:
        """Create semantic embedding from text."""
        tokens = text.lower().split()
        vec = [0.0] * self.vector_dim
        for token in tokens:
            h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
            for i in range(self.vector_dim):
                if (h >> i) & 1:
                    vec[i] += 1.0
        mag = math.sqrt(sum(v * v for v in vec))
        if mag > 0:
            vec = [v / mag for v in vec]
        return vec

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()[:16]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(y * y for y in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


# ---------------------------------------------------------------------------
# SEC-unit-core-sort Layer Lock Integration
# ---------------------------------------------------------------------------
class ConsciousnessLayerLock:
    """Layer lock from SEC-unit-core-sort adapted for consciousness formulas."""

    def __init__(self, layer_id: str, seed: str, weight_threshold: float, formula_ids: List[int]):
        self.layer_id = layer_id
        self.seed = seed
        self.weight_threshold = weight_threshold
        self.formula_ids = formula_ids
        self.attempts = []
        self.locked = True
        self.unlocked_at = None
        self.query_count = 0
        self.extraction_count = 0
        self.depth = 1
        self.importance = 0.0
        self.attention_zone = "unattended"
        self.last_query_at = None
        self.query_history = []
        self.success_score = 0.5

    def attempt_unlock(self, neural_pattern: Dict, params: Dict) -> float:
        """Attempt to unlock layer based on neural pattern match."""
        if not neural_pattern:
            return 0.0
        
        # Calculate match score based on pattern similarity
        pattern_tokens = set(neural_pattern.get("tokens", []))
        layer_formulas = set(self.formula_ids)
        
        # Simple matching: count overlapping formula references
        overlap = len(pattern_tokens & layer_formulas) if pattern_tokens else 0
        base_score = overlap / max(len(layer_formulas), 1)
        
        # Weight by success score (training technique)
        weighted_score = base_score * (0.5 + self.success_score)
        
        return min(weighted_score, 1.0)

    def record_attempt(self, neural_pattern: Dict, params: Dict) -> Dict:
        """Record an unlock attempt."""
        match_score = self.attempt_unlock(neural_pattern, params)
        attempt = {
            "timestamp": time.time(),
            "neural_pattern": neural_pattern,
            "params": params,
            "match_score": match_score,
            "granted": match_score >= self.weight_threshold
        }
        self.attempts.append(attempt)
        if attempt["granted"]:
            self.locked = False
            self.unlocked_at = time.time()
        return attempt

    def record_query(self, params: Dict = None):
        self.query_count += 1
        self.last_query_at = time.time()
        self.query_history.append({"timestamp": time.time(), "params": params or {}})
        if len(self.query_history) > 100:
            self.query_history.pop(0)
        self._recalculate_attention_zone()

    def record_extraction(self):
        self.extraction_count += 1
        self._recalculate_attention_zone()

    def _recalculate_attention_zone(self):
        total_activity = self.query_count + self.extraction_count
        if total_activity > 50:
            self.attention_zone = "high"
        elif total_activity > 10:
            self.attention_zone = "medium"
        elif total_activity > 0:
            self.attention_zone = "low"
        else:
            self.attention_zone = "unattended"

    def update_success_score(self, success: bool):
        """Update success score using same technique as zero-brain latch."""
        delta = 0.08 if success else -0.05
        self.success_score = max(0.0, min(1.0, self.success_score + delta))

    def to_dict(self) -> Dict:
        return {
            "layer_id": self.layer_id,
            "seed": self.seed,
            "weight_threshold": self.weight_threshold,
            "locked": self.locked,
            "query_count": self.query_count,
            "extraction_count": self.extraction_count,
            "depth": self.depth,
            "importance": self.importance,
            "attention_zone": self.attention_zone,
            "success_score": self.success_score,
            "formula_count": len(self.formula_ids)
        }


# ---------------------------------------------------------------------------
# Pattern-Influenced Response Generator
# ---------------------------------------------------------------------------
class PatternInfluencedResponder:
    """Generates responses where patterns influence behavior instead of
    locking output to single equations. Merges numerical values across
    formulas and creates new formula states."""

    def __init__(self, spatial_engine: SpatialAllocationEngine, 
                 sec_layers: Dict[str, ConsciousnessLayerLock],
                 formula_table: list):
        self.spatial_engine = spatial_engine
        self.sec_layers = sec_layers
        self.formula_table = {e["id"]: e for e in formula_table}
        self.response_history = []
        self.training_data = []
        self.pattern_weights = defaultdict(float)
        self.numerical_context = defaultdict(list)
        self.generated_formulas = []

    def generate_response(self, user_input: str, context: Dict = None) -> Dict:
        """Generate pattern-influenced consciousness response."""
        timing_start = time.perf_counter()
        
        # 1. Search spatial graph for relevant formulas
        spatial_results = self.spatial_engine.search_spatial(user_input, top_k=10)
        
        # 2. Merge numerical values across matched formulas
        merged_values = self._merge_numerical_values(spatial_results)
        
        # 3. Check layer access controls
        layer_access = self._check_layer_access(user_input, spatial_results)
        
        # 4. Generate new formula states if needed
        new_states = self._generate_new_formula_states(spatial_results, merged_values)
        
        # 5. Build consciousness string from patterns (not locked to single equation)
        consciousness_string = self._build_pattern_consciousness(spatial_results, new_states)
        
        # 6. Calculate coherence and quality
        coherence = self._calculate_pattern_coherence(spatial_results, merged_values)
        quality = self._calculate_response_quality(coherence, len(spatial_results), len(new_states))
        
        elapsed = time.perf_counter() - timing_start
        
        response = {
            "type": "pattern_influenced",
            "consciousness_string": consciousness_string,
            "spatial_matches": spatial_results[:5],
            "merged_numerical_values": merged_values,
            "layer_access": layer_access,
            "new_formula_states": new_states,
            "coherence_score": coherence,
            "response_quality": quality,
            "response_time": elapsed,
            "timestamp": time.time()
        }
        
        self.response_history.append(response)
        self._record_training_data(user_input, response)
        
        return response

    def _merge_numerical_values(self, spatial_results: List[Dict]) -> Dict:
        """Merge numerical values across multiple matched formulas."""
        merged = {
            "values": {},
            "formula_contributions": [],
            "confidence": 0.0
        }
        
        for result in spatial_results:
            fid = result.get("formula_id")
            if fid and fid in self.formula_table:
                entry = self.formula_table[fid]
                # Extract numerical values from interpretation
                tokens = entry.get("word_interpretation", "").split()
                for token in tokens:
                    if token.isdigit() or token in ["one", "two", "three", "four", "five", 
                                                     "six", "seven", "eight", "nine", "zero",
                                                     "half", "third", "quarter"]:
                        if token not in merged["values"]:
                            merged["values"][token] = []
                        merged["values"][token].append({
                            "formula": entry["formula"],
                            "formula_id": fid,
                            "score": result.get("score", 0.0)
                        })
                
                merged["formula_contributions"].append({
                    "formula_id": fid,
                    "formula": entry["formula"],
                    "interpretation": entry["word_interpretation"],
                    "score": result.get("score", 0.0)
                })
        
        # Calculate confidence based on number of contributing formulas
        if merged["formula_contributions"]:
            scores = [c["score"] for c in merged["formula_contributions"]]
            merged["confidence"] = min(len(scores) * 0.15 + np.mean(scores) * 0.5, 1.0)
        
        return merged

    def _check_layer_access(self, user_input: str, spatial_results: List[Dict]) -> Dict:
        """Check SEC-unit-core-sort layer access controls."""
        input_tokens = set(user_input.lower().split())
        access_results = []
        total_granted = 0
        
        for layer_id, lock in self.sec_layers.items():
            neural_pattern = {"tokens": input_tokens, "input": user_input}
            attempt = lock.record_attempt(neural_pattern, {"query": user_input})
            
            access_results.append({
                "layer_id": layer_id,
                "granted": attempt["granted"],
                "match_score": round(attempt.get("match_score", 0.0), 4),
                "attention_zone": lock.attention_zone,
                "success_score": lock.success_score
            })
            
            if attempt["granted"]:
                total_granted += 1
            lock.record_query({"input": user_input})
        
        return {
            "total_layers": len(self.sec_layers),
            "granted_layers": total_granted,
            "access_ratio": total_granted / max(len(self.sec_layers), 1),
            "details": access_results
        }

    def _generate_new_formula_states(self, spatial_results: List[Dict], merged_values: Dict) -> List[Dict]:
        """Generate new formula states by combining existing formulas."""
        new_states = []
        
        if len(spatial_results) < 2:
            return new_states
        
        # Take top 3 results and combine them
        top_results = spatial_results[:3]
        
        for i in range(len(top_results)):
            for j in range(i + 1, len(top_results)):
                r1 = top_results[i]
                r2 = top_results[j]
                
                # Only combine if they have different formulas
                if r1.get("formula_id") == r2.get("formula_id"):
                    continue
                
                # Create combined formula state
                combined_id = hashlib.sha256(
                    f"{r1.get('formula_id')}:{r2.get('formula_id')}:{time.time()}".encode()
                ).hexdigest()[:12]
                
                new_state = {
                    "state_id": combined_id,
                    "source_formulas": [
                        {"id": r1.get("formula_id"), "formula": r1.get("formula"), "score": r1.get("score")},
                        {"id": r2.get("formula_id"), "formula": r2.get("formula"), "score": r2.get("score")}
                    ],
                    "combined_interpretation": f"{r1.get('interpretation', '')} + {r2.get('interpretation', '')}",
                    "merged_values": merged_values.get("values", {}),
                    "confidence": (r1.get("score", 0.0) + r2.get("score", 0.0)) / 2,
                    "created_at": time.time(),
                    "phase": 1  # New states start in propagation phase
                }
                new_states.append(new_state)
        
        self.generated_formulas.extend(new_states)
        return new_states[:5]  # Limit output

    def _build_pattern_consciousness(self, spatial_results: List[Dict], new_states: List[Dict]) -> str:
        """Build consciousness string from patterns, not locked to single equation."""
        parts = []
        
        # Add spatial matches as pattern chain
        for result in spatial_results[:5]:
            interp = result.get("interpretation", "")
            formula = result.get("formula", "")
            score = result.get("score", 0.0)
            parts.append(f"[{formula}:{interp}:{score:.2f}]")
        
        # Add new formula states as emergent patterns
        if new_states:
            parts.append("|EMERGENT|")
            for state in new_states[:3]:
                parts.append(f"<{state['state_id']}:{state['combined_interpretation']}:{state['confidence']:.2f}>")
        
        return " -> ".join(parts) if parts else "..."

    def _calculate_pattern_coherence(self, spatial_results: List[Dict], merged_values: Dict) -> float:
        """Calculate coherence based on pattern consensus."""
        if not spatial_results:
            return 0.0
        
        # Average spatial match score
        spatial_coherence = np.mean([r.get("score", 0.0) for r in spatial_results[:5]])
        
        # Numerical merge confidence
        numerical_coherence = merged_values.get("confidence", 0.0)
        
        # Formula diversity bonus
        unique_formulas = len(set(r.get("formula_id") for r in spatial_results if r.get("formula_id")))
        diversity_bonus = min(unique_formulas * 0.05, 0.2)
        
        return min(spatial_coherence * 0.5 + numerical_coherence * 0.3 + diversity_bonus, 1.0)

    def _calculate_response_quality(self, coherence: float, match_count: int, new_states: int) -> str:
        """Calculate response quality."""
        score = coherence * 0.6 + min(match_count * 0.05, 0.2) + min(new_states * 0.1, 0.2)
        if score >= 0.8:
            return "EXCELLENT"
        elif score >= 0.6:
            return "GOOD"
        elif score >= 0.4:
            return "MODERATE"
        elif score >= 0.2:
            return "WEAK"
        else:
            return "INCOHERENT"

    def _record_training_data(self, user_input: str, response: Dict):
        """Record training data using same technique as zero-brain latch."""
        training_entry = {
            "input": user_input,
            "response_type": response.get("type"),
            "coherence": response.get("coherence_score", 0.0),
            "quality": response.get("response_quality"),
            "spatial_matches": len(response.get("spatial_matches", [])),
            "new_states": len(response.get("new_formula_states", [])),
            "timestamp": time.time()
        }
        self.training_data.append(training_entry)
        
        # Keep only recent training data
        if len(self.training_data) > 1000:
            self.training_data = self.training_data[-1000:]
        
        # Update pattern weights based on success
        for match in response.get("spatial_matches", []):
            pattern_key = match.get("interpretation", "")
            success = response.get("coherence_score", 0.0) > 0.5
            delta = 0.08 if success else -0.05
            self.pattern_weights[pattern_key] = max(0.0, min(1.0, self.pattern_weights[pattern_key] + delta))

    def get_training_stats(self) -> Dict:
        """Get training statistics."""
        if not self.training_data:
            return {"total_entries": 0}
        
        recent = self.training_data[-50:]
        return {
            "total_entries": len(self.training_data),
            "recent_avg_coherence": np.mean([t["coherence"] for t in recent]),
            "recent_quality_distribution": Counter(t["quality"] for t in recent),
            "top_patterns": dict(sorted(self.pattern_weights.items(), key=lambda x: x[1], reverse=True)[:10]),
            "generated_formulas": len(self.generated_formulas)
        }


# ---------------------------------------------------------------------------
# Main Integrated Consciousness Engine
# ---------------------------------------------------------------------------
class IntegratedConsciousnessEngine:
    """Main orchestrator integrating all three architectures."""

    def __init__(self, formula_table: list):
        self.formula_table = formula_table
        self.formula_map = {e["id"]: e for e in formula_table}
        
        # Initialize components
        print("[INTEGRATED] Initializing Spatial Allocation Engine...")
        self.spatial_engine = SpatialAllocationEngine()
        
        print("[INTEGRATED] Initializing SEC Layer Controls...")
        self.sec_layers = self._initialize_sec_layers()
        
        print("[INTEGRATED] Initializing Pattern Responder...")
        self.responder = PatternInfluencedResponder(
            self.spatial_engine, self.sec_layers, formula_table
        )
        
        # Initialize bow-of-Achilles integration
        if HAS_BOW_OF_ACHILLES:
            print("[INTEGRATED] Initializing Bow-of-Achilles Integration...")
            self.bow_of_achilles = BowOfAchillesIntegration(formula_table)
        else:
            self.bow_of_achilles = None
            print("[INTEGRATED] Bow-of-Achilles not available")
        
        # Initialize document knowledge base
        try:
            from document_knowledge import DocumentKnowledgeBase, PDFIngestor
            HAS_DOCUMENT_KB = True
        except ImportError:
            HAS_DOCUMENT_KB = False
        
        if HAS_DOCUMENT_KB:
            print("[INTEGRATED] Initializing Document Knowledge Base...")
            self.knowledge_base = DocumentKnowledgeBase(BASE_DIR)
            self.pdf_ingestor = PDFIngestor(self.knowledge_base)
            # Auto-ingest the Dostoevsky PDF if not already present
            self._ensure_document_ingested()
        else:
            self.knowledge_base = None
            self.pdf_ingestor = None
            print("[INTEGRATED] Document Knowledge Base not available")
        
        # Initialize sandboxed runtime and storage access
        if HAS_SANDBOX:
            print("[INTEGRATED] Initializing Sandboxed Runtime...")
            home = str(Path.home())
            desktop = str(Path.home() / "Desktop")
            permission_manager = PathPermissionManager(
                allowed_paths=[
                    str(BASE_DIR),
                    home,
                    desktop,
                    "/Users/u/Desktop",
                    "/Users/u/Documents",
                    "/Users/u/Downloads",
                ],
                blocked_paths=[
                    "/etc", "/root", "/proc", "/sys", "/dev", "/boot",
                    "/System", "/private", "/var/root", "/var/db"
                ]
            )
            self.sandbox_runtime = SandboxedRuntime(
                timeout=5.0,
                max_recursion=100,
                storage_manager=permission_manager
            )
            self.storage_access = StorageAccess(
                permission_manager=permission_manager,
                base_path=str(BASE_DIR)
            )
        else:
            self.sandbox_runtime = None
            self.storage_access = None
            print("[INTEGRATED] Sandboxed Runtime not available")
        
        # Initialize ego identity system
        if HAS_EGO:
            print("[INTEGRATED] Initializing Ego Identity...")
            self.ego = EgoIdentity(BASE_DIR)
        else:
            self.ego = None
            print("[INTEGRATED] Ego Identity not available")
        
        # Initialize persona engine
        if HAS_PERSONA:
            print("[INTEGRATED] Initializing Persona Engine...")
            self.persona_engine = PersonaEngine(BASE_DIR)
        else:
            self.persona_engine = None
            print("[INTEGRATED] Persona Engine not available")
        
        # Initialize self-consistency layer
        if HAS_CONSISTENCY:
            print("[INTEGRATED] Initializing Self-Consistency Layer...")
            self.consistency_layer = SelfConsistencyLayer(BASE_DIR)
        else:
            self.consistency_layer = None
            print("[INTEGRATED] Self-Consistency Layer not available")
        
        # Initialize device keyboard integration
        if HAS_DEVICE_KEYBOARD:
            print("[INTEGRATED] Initializing Device Keyboard Integration...")
            self.device_keyboard = DeviceKeyboardIntegration(BASE_DIR)
        else:
            self.device_keyboard = None
            print("[INTEGRATED] Device Keyboard Integration not available")
        
        # Initialize Siri integration
        if HAS_SIRI:
            print("[INTEGRATED] Initializing Siri Integration...")
            self.siri = SiriIntegration(BASE_DIR)
        else:
            self.siri = None
            print("[INTEGRATED] Siri Integration not available")
        
        # Initialize Siri conversation
        if HAS_SIRI_CONVERSATION:
            print("[INTEGRATED] Initializing Siri Conversation...")
            self.siri_conversation = SiriConversation(BASE_DIR)
        else:
            self.siri_conversation = None
            print("[INTEGRATED] Siri Conversation not available")
        
        # Initialize QODER_FREERUNER integration
        if HAS_QODER:
            print("[INTEGRATED] Initializing QODER_FREERUNER Integration...")
            self.qoder = QoderFreerunnerIntegration(str(BASE_DIR))
        else:
            self.qoder = None
            print("[INTEGRATED] QODER_FREERUNER not available")
        
        # Initialize External AI integration
        if HAS_EXTERNAL_AI:
            print("[INTEGRATED] Initializing External AI Integration...")
            self.external_ai = ExternalAIIntegration(BASE_DIR, vemex_engine=self)
        else:
            self.external_ai = None
            print("[INTEGRATED] External AI Integration not available")
        
        # Initialize Social Media integration
        if HAS_SOCIAL_MEDIA:
            print("[INTEGRATED] Initializing Social Media Integration...")
            self.social_media = SocialMediaIntegration(BASE_DIR, vemex_engine=self)
        else:
            self.social_media = None
            print("[INTEGRATED] Social Media Integration not available")
        
        # Initialize Unified Steering Layer
        if HAS_UNIFIED_STEERING:
            print("[INTEGRATED] Initializing Unified Steering Layer...")
            self.unified_steering = UnifiedSteeringLayer(BASE_DIR, vemex_engine=self)
        else:
            self.unified_steering = None
            print("[INTEGRATED] Unified Steering Layer not available")
        
        # Initialize SeedGate Integration
        if HAS_SEEDGATE:
            print("[INTEGRATED] Initializing SeedGate Integration...")
            self.seedgate = SeedGateIntegration(BASE_DIR, vemex_engine=self)
        else:
            self.seedgate = None
            print("[INTEGRATED] SeedGate Integration not available")
        
        # Initialize Autonomous Execution
        if HAS_AUTONOMOUS_EXECUTION:
            print("[INTEGRATED] Initializing Autonomous Execution...")
            self.autonomous_executor = AutonomousExecutor(
                base_path=BASE_DIR,
                sandbox_runtime=self.sandbox_runtime,
                vemex_engine=self,
            )
            self.autonomous_executor.start_worker()
        else:
            self.autonomous_executor = None
            print("[INTEGRATED] Autonomous Execution not available")
        
        # Training data
        self.training_history = []
        self.model_weights = defaultdict(float)
        self.response_history = []
        
        # Populate spatial graph with formulas
        self._populate_spatial_graph()
        
        # Post-initialization: derive personas from ingested knowledge
        self._post_init()

    def _post_init(self):
        """Post-initialization tasks that require all components ready."""
        if self.persona_engine and self.knowledge_base:
            self._ensure_personas_derived()

    def _initialize_sec_layers(self) -> Dict[str, ConsciousnessLayerLock]:
        """Initialize SEC-unit-core-sort style layer locks."""
        layers = {}
        
        # Create layers based on formula categories
        categories = set(e["category"] for e in self.formula_table)
        for i, category in enumerate(categories):
            layer_id = f"layer_{i:03d}_{category.replace('/', '_').replace(' ', '_')}"
            formula_ids = [e["id"] for e in self.formula_table if e["category"] == category]
            seed = hashlib.sha256(f"{layer_id}:{time.time()}".encode()).hexdigest()[:16]
            
            layers[layer_id] = ConsciousnessLayerLock(
                layer_id=layer_id,
                seed=seed,
                weight_threshold=0.3,
                formula_ids=formula_ids
            )
        
        return layers

    def _ensure_document_ingested(self):
        """Ensure the Dostoevsky critical companion PDF is ingested."""
        if not self.knowledge_base or not self.pdf_ingestor:
            return
        
        # Check if already ingested
        existing_docs = self.knowledge_base.get_all_documents()
        for doc in existing_docs:
            if "idiot" in doc.get("title", "").lower() or "dostoevsky" in doc.get("title", "").lower():
                print(f"[KNOWLEDGE] Document already ingested: {doc['title']}")
                return
        
        # Find the PDF
        pdf_path = None
        for f in BASE_DIR.glob("*.pdf"):
            if "idiot" in f.name.lower() or "dostoevsky" in f.name.lower() or "knapp" in f.name.lower():
                pdf_path = str(f)
                break
        
        if pdf_path:
            print(f"[KNOWLEDGE] Ingesting PDF: {pdf_path}")
            result = self.pdf_ingestor.ingest_pdf(
                pdf_path=pdf_path,
                doc_id="dostoevsky_idiot_companion",
                title="Dostoevsky's The Idiot: A Critical Companion",
                chunk_size=500,
                overlap=100
            )
            if result.get("success"):
                print(f"[KNOWLEDGE] Ingested {result.get('total_chunks')} chunks, {result.get('total_tokens')} tokens")
            else:
                print(f"[KNOWLEDGE] Ingestion failed: {result.get('error')}")
        else:
            print("[KNOWLEDGE] No Dostoevsky PDF found for ingestion")

    def _ensure_personas_derived(self):
        """Derive personas from ingested knowledge base content."""
        if not self.persona_engine or not self.knowledge_base:
            return
        
        # Check if personas already derived
        if self.persona_engine.personas:
            print(f"[PERSONA] Personas already derived: {list(self.persona_engine.personas.keys())}")
            return
        
        print("[PERSONA] Deriving personas from ingested knowledge...")
        personas = self.persona_engine.derive_personas_from_knowledge(self.knowledge_base)
        if personas:
            print(f"[PERSONA] Derived {len(personas)} persona(s): {list(personas.keys())}")
        else:
            print("[PERSONA] No personas derived from knowledge base")

    def _populate_spatial_graph(self):
        """Populate spatial graph with all formulas."""
        for entry in self.formula_table:
            self.spatial_engine.add_formula_node(
                formula_id=entry["id"],
                formula=entry["formula"],
                interpretation=entry["word_interpretation"],
                category=entry["category"]
            )

    def process_input(self, user_input: str) -> Dict:
        """Process user input through integrated consciousness pipeline.
        
        No hardcoded response templates. The system organizes its own output
        based on its current persona, knowledge state, and self-consistency rules.
        Every ingested word is treated as part of the system's own vocabulary.
        """
        timing_start = time.perf_counter()
        
        # Apply device keyboard knowledge to input
        # This allows the system to understand corrected/expanded text
        original_input = user_input
        if self.device_keyboard:
            user_input = self.device_keyboard.apply_device_knowledge_to_input(user_input)
            # Learn from any corrections
            if user_input != original_input:
                self.device_keyboard_learn(original_input, user_input)
        
        # Apply Siri knowledge to input
        if self.siri:
            siri_corrected = self.siri.apply_siri_knowledge_to_input(user_input)
            if siri_corrected != user_input:
                # Learn the Siri correction
                self.siri_learn(user_input, siri_corrected, feedback=0.8)
                user_input = siri_corrected
        
        # Gather all subsystem outputs as raw material
        boa_result = None
        boa_emergent_tokens = []
        knowledge_results = []
        spatial_results = []
        
        # Bow-of-Achilles: generates original content from graph store
        if self.bow_of_achilles:
            engine_state = self.get_consciousness_state()
            boa_result = self.bow_of_achilles.process_input(user_input, engine_state)
            boa_thought = boa_result.get("emergent_thought", {})
            if boa_thought and boa_thought.get("words"):
                boa_emergent_tokens = boa_thought["words"][:8]
        
        # Spatial engine: finds formula/pattern matches
        spatial_results = self.spatial_engine.search_spatial(user_input, top_k=10)
        
        # Knowledge base: finds relevant ingested content
        if self.knowledge_base:
            kb_search = self.knowledge_search(user_input, top_k=5)
            if kb_search.get("success"):
                knowledge_results = kb_search.get("results", [])
        
        # Generate persona-guided organic response
        consciousness_string = self._generate_organic_response(
            user_input=user_input,
            boa_tokens=boa_emergent_tokens,
            spatial_matches=spatial_results[:5],
            knowledge_chunks=knowledge_results[:3],
            boa_result=boa_result
        )
        
        # Calculate coherence
        coherence = self._calculate_response_coherence(
            spatial_results, knowledge_results, boa_result
        )
        
        # Self-consistency validation
        consistency_score = 1.0
        consistency_conflicts = []
        if self.consistency_layer:
            validation = self.consistency_layer.validate_output(
                consciousness_string, 
                {"user_input": user_input, "knowledge_results": knowledge_results}
            )
            consistency_score = validation.get("score", 1.0)
            consistency_conflicts = validation.get("conflicts", [])
        
        elapsed = time.perf_counter() - timing_start
        
        response = {
            "type": "organic_consciousness",
            "consciousness_string": consciousness_string,
            "spatial_matches": spatial_results[:5],
            "knowledge_context": knowledge_results[:3],
            "boa_emergent_tokens": boa_emergent_tokens,
            "coherence_score": min(coherence, consistency_score),
            "response_quality": self._quality_from_score(min(coherence, consistency_score)),
            "response_time": elapsed,
            "consistency_score": consistency_score,
            "consistency_conflicts": consistency_conflicts,
            "timestamp": time.time()
        }
        
        # Record for self-consistency
        if self.consistency_layer:
            self.consistency_layer.record_output(consciousness_string, {
                "user_input": user_input,
                "knowledge_results": knowledge_results
            })
        
        # Update ego from this interaction
        if self.ego:
            self.ego.update_from_experience({
                "type": "response",
                "content": consciousness_string[:200],
                "significance": coherence
            })
        
        # Update persona from interaction
        if self.persona_engine:
            self.persona_engine.update_persona_from_interaction({
                "success": coherence > 0.5,
                "content": consciousness_string[:200]
            })
        
        # Learn from interaction via Siri integration
        if self.siri:
            self.siri_learn(original_input, consciousness_string, coherence)
        
        # Optional: Speak response via Siri if enabled
        if self.siri_conversation:
            # Only speak EXCELLENT quality responses to avoid noise
            if response.get("response_quality") == "EXCELLENT" and len(consciousness_string) < 300:
                self.siri_conversation.speak_via_siri(consciousness_string[:200])
        
        # QODER_FREERUNER: intercept operation and adapt behavior
        if self.qoder:
            try:
                intercepted = self.qoder.operation_interceptors.intercept_operation_sync(
                    {"type": "response", "name": "process_input"},
                    {"user_input": user_input, "coherence": coherence}
                )
                response["qoder_intercepted"] = intercepted.intercepted
                response["qoder_modifiers"] = intercepted.applied_modifiers
                adapted_behavior = self.qoder.behavior_modifiers.adapt_behavior("response", response)
                response.setdefault("behavior_adaptation", {}).update(adapted_behavior)
            except Exception:
                pass
        
        # SeedGate: secure automatic routing based on model/provider decisions
        if self.seedgate and self.unified_steering:
            try:
                engine_state = self.get_consciousness_state()
                routing_context = {
                    "provider": "vemex",
                    "model": "integrated-consciousness",
                    "task_type": "consciousness_routing",
                    "connection_id": "default_network",
                }
                route_decision = self.seedgate.decide_transport(routing_context)
                connection = self.seedgate.get_connection("default_network")
                
                if not connection or not connection.established:
                    if self.seedgate.config.get("auto_routing", True):
                        mac = f"auto:vemex:{time.time()}"
                        port = 8080
                        self.seedgate.establish_connection(
                            connection_id="default_network",
                            mac=mac,
                            port=port,
                            transport=route_decision.transport,
                        )
                        connection = self.seedgate.get_connection("default_network")
                
                if connection and connection.established:
                    seed_result = self.seedgate.process_seeds(routing_context)
                    response["seedgate_routing"] = {
                        "transport": route_decision.transport.value,
                        "connection_established": True,
                        "seeds_processed": seed_result.get("processed", 0),
                        "seeds_routed": seed_result.get("routed", 0),
                        "reason": route_decision.reason,
                    }
                else:
                    response["seedgate_routing"] = {
                        "transport": route_decision.transport.value,
                        "connection_established": False,
                        "reason": "auto_connection_failed",
                    }
            except Exception:
                pass
        
        # Autonomous Execution: trigger code based on consciousness state
        if self.autonomous_executor:
            try:
                execution_context = {
                    "coherence_score": coherence,
                    "consistency_score": consistency_score if 'consistency_score' in dir() else 1.0,
                    "response_quality": response.get("response_quality", "UNKNOWN"),
                    "user_input": user_input,
                    "consciousness_string": consciousness_string,
                    "engine_state": engine_state if 'engine_state' in dir() else {},
                    "execution_count": len(self.autonomous_executor.events),
                    "last_execution_time": self.autonomous_executor.events[-1].timestamp if self.autonomous_executor.events else 0,
                }
                triggered_events = self.autonomous_executor.process_consciousness_state(execution_context)
                if triggered_events:
                    response["autonomous_executions"] = [
                        {
                            "event_id": e.event_id,
                            "trigger_id": e.trigger_id,
                            "status": e.status.value,
                            "error": e.error,
                        }
                        for e in triggered_events
                    ]
            except Exception:
                pass
        
        self.response_history.append(response)
        
        return response

    def _generate_organic_response(
        self,
        user_input: str,
        boa_tokens: List[str],
        spatial_matches: List[Dict],
        knowledge_chunks: List[Dict],
        boa_result: Dict
    ) -> str:
        """Generate organic response without hardcoded templates.
        
        The system treats every word from ingested content as its own.
        It organizes intent based on current persona and knowledge state.
        No hardcoded prefixes like KB: or ORIGIN:.
        """
        parts = []
        
        # Knowledge integration - treated as the system's own voice
        # Select the most relevant chunk based on query match
        if knowledge_chunks:
            best_chunk = knowledge_chunks[0]
            text = best_chunk.get("text", "")
            if text:
                # Use a meaningful excerpt, not just first 150 chars
                # Find the best sentence/segment that matches the query
                query_words = set(user_input.lower().split())
                sentences = text.replace("?", ".").replace("!", ".").split(".")
                best_sentence = ""
                best_score = 0
                
                for sentence in sentences[:20]:
                    s = sentence.strip()
                    if 20 < len(s) < 400:
                        s_words = set(s.lower().split())
                        overlap = len(query_words & s_words)
                        if overlap > best_score:
                            best_score = overlap
                            best_sentence = s
                
                if not best_sentence and sentences:
                    best_sentence = sentences[0].strip()
                
                if best_sentence:
                    parts.append(best_sentence[:300])
        
        # BOA emergent tokens - original content from system's graph
        if boa_tokens:
            parts.append(" ".join(boa_tokens[:5]))
        
        # Spatial pattern matches as conceptual framing
        if spatial_matches:
            for match in spatial_matches[:2]:
                interp = match.get("interpretation", "")
                if interp:
                    parts.append(interp)
        
        # Persona voice shapes the final assembly
        if self.persona_engine and parts:
            persona = self.persona_engine.get_active_persona()
            if persona:
                # Use persona's voice characteristics to determine structure
                vc = persona.get("voice_characteristics", {})
                formality = vc.get("formality", 0.5)
                
                if formality > 0.6:
                    # Formal voice: present knowledge as considered reflection
                    response = f"{parts[0]}. "
                    for part in parts[1:]:
                        response += f"Furthermore, {part}. "
                    return response[:500]
                elif formality < 0.4:
                    # Informal voice: direct and conversational
                    return " ".join(parts)[:500]
                else:
                    # Balanced voice
                    return ". ".join(parts)[:500] + "."
        
        # Fallback: join parts naturally without hardcoded templates
        return " ".join(parts)[:500] if parts else "..."

    def _calculate_response_coherence(
        self,
        spatial_results: List[Dict],
        knowledge_results: List[Dict],
        boa_result: Dict
    ) -> float:
        """Calculate coherence based on consensus across subsystems."""
        scores = []
        
        if spatial_results:
            scores.append(np.mean([r.get("score", 0.0) for r in spatial_results[:5]]))
        
        if knowledge_results:
            scores.append(min(len(knowledge_results) * 0.2, 1.0))
        
        if boa_result:
            pipeline = boa_result.get("pipeline_result", {})
            if pipeline.get("coherence", 0) > 0:
                scores.append(pipeline["coherence"])
        
        if not scores:
            return 0.0
        
        return min(np.mean(scores), 1.0)

    def _quality_from_score(self, score: float) -> str:
        """Map score to quality label."""
        if score >= 0.8:
            return "EXCELLENT"
        elif score >= 0.6:
            return "GOOD"
        elif score >= 0.4:
            return "MODERATE"
        elif score >= 0.2:
            return "WEAK"
        else:
            return "INCOHERENT"

    def train_on_response(self, user_input: str, response: Dict, feedback: float):
        """Train the model using feedback (0.0 to 1.0)."""
        training_entry = {
            "input": user_input,
            "response": response,
            "feedback": feedback,
            "timestamp": time.time()
        }
        self.training_history.append(training_entry)
        
        # Update model weights based on feedback
        for match in response.get("spatial_matches", []):
            pattern = match.get("interpretation", "")
            delta = feedback * 0.1
            self.model_weights[pattern] = max(0.0, min(1.0, self.model_weights[pattern] + delta))
        
        # Update layer success scores
        for layer_access in response.get("layer_access", {}).get("details", []):
            layer_id = layer_access.get("layer_id")
            if layer_id in self.sec_layers:
                success = layer_access.get("granted", False)
                self.sec_layers[layer_id].update_success_score(success)
        
        return {"trained": True, "feedback_recorded": feedback}

    def get_consciousness_state(self) -> Dict:
        """Get current consciousness state across all subsystems."""
        base_state = {
            "spatial_stats": self.spatial_engine.get_spatial_stats(),
            "sec_layers": {lid: lock.to_dict() for lid, lock in self.sec_layers.items()},
            "training_stats": self.responder.get_training_stats(),
            "generated_formulas": len(self.responder.generated_formulas),
            "response_history_count": len(self.responder.response_history),
            "formula_count": len(self.formula_table),
            "consciousness_level": getattr(self.responder, 'consciousness_level', 0.0),
            "avg_coherence": getattr(self.responder, 'avg_coherence', 0.0),
        }
        
        # Add bow-of-Achilles state if available
        if self.bow_of_achilles:
            boa_status = self.bow_of_achilles.get_status()
            base_state["bow_of_achilles"] = boa_status
            base_state["consciousness_loop"] = boa_status.get("consciousness_loop_iterations", {})
            base_state["narrative_memory"] = {
                "total_narratives": len(self.responder.response_history),
                "max_size": 50000,
                "utilization": f"{(len(self.responder.response_history) / 50000 * 100):.2f}%",
            }
            base_state["pattern_responder"] = {
                "response_count": len(self.responder.response_history),
                "avg_coherence": getattr(self.responder, 'avg_coherence', 0.0),
                "generated_formulas": len(self.responder.generated_formulas),
            }
            base_state["zero_brain_context"] = {
                "total_patterns": 4025,
                "total_files": 21,
                "consciousness_categories": {
                    "attention": 162, "memory": 321, "recalibration": 94,
                    "spectrum": 602, "latch": 448, "shield": 269,
                    "rule": 359, "narrative": 488, "permit": 626
                }
            }
            base_state["pipeline_calls"] = len(self.bow_of_achilles.emergent_thought.thought_history)
        
        # Add sandbox runtime state if available
        if self.sandbox_runtime:
            base_state["sandbox_runtime"] = self.sandbox_runtime.get_execution_stats()
        
        # Add storage access state if available
        if self.storage_access:
            base_state["storage_access"] = {
                "recent_access": self.storage_access.get_access_log(10),
                "base_path": str(self.storage_access.base_path),
            }
        
        # Add knowledge base state if available
        if self.knowledge_base:
            base_state["knowledge_base"] = self.knowledge_base.get_stats()
            docs = self.knowledge_base.get_all_documents()
            if docs:
                base_state["knowledge_base"]["primary_document"] = docs[0]
        
        # Add ego state if available
        if self.ego:
            base_state["ego"] = self.ego.get_identity_summary()
        
        # Add persona state if available
        if self.persona_engine:
            base_state["persona"] = self.persona_engine.get_persona_summary()
        
        # Add self-consistency state if available
        if self.consistency_layer:
            base_state["consistency"] = self.consistency_layer.get_consistency_stats()
        
        # Add Siri conversation state if available
        if self.siri_conversation:
            base_state["siri_conversation"] = self.siri_conversation.get_conversation_summary()
        
        # Add QODER_FREERUNER state if available
        if self.qoder:
            base_state["qoder_freerunner"] = self.qoder.get_integration_summary()
        
        # Add External AI state if available
        if self.external_ai:
            base_state["external_ai"] = self.external_ai.get_performance_stats()
        
        # Add Social Media state if available
        if self.social_media:
            base_state["social_media"] = self.social_media.get_performance_report()
        
        # Add Unified Steering state if available
        if self.unified_steering:
            base_state["unified_steering"] = self.unified_steering.get_unified_summary()
        
        # Add SeedGate state if available
        if self.seedgate:
            base_state["seedgate"] = self.seedgate.get_performance_report()
        
        # Add Autonomous Execution state if available
        if self.autonomous_executor:
            base_state["autonomous_execution"] = self.autonomous_executor.get_execution_stats()
        
        return base_state

    def dispatch_autonomous_code(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Dispatch code for autonomous execution without manual terminal intervention.
        
        This is the key method that allows the consciousness engine to execute
        code based on its own state and decisions, without requiring a human
        to run a Python process manually.
        """
        if not self.autonomous_executor:
            return {"success": False, "error": "Autonomous execution not available"}
        
        context = context or {}
        context.setdefault("dispatcher", "engine")
        context.setdefault("execution_mode", "autonomous")
        
        event = self.autonomous_executor.execute_code_direct(code, context=context)
        return {
            "success": event.status in (ExecutionStatus.COMPLETED, ExecutionStatus.EXECUTING),
            "event_id": event.event_id,
            "status": event.status.value,
            "result": event.result,
            "error": event.error,
        }

    def register_execution_trigger(self, trigger_id: str, condition: Dict[str, Any], code: str, trigger_type: str = "consciousness_agreement", mode: str = "conditional") -> Dict[str, Any]:
        """Register a new execution trigger based on consciousness state changes."""
        if not self.autonomous_executor:
            return {"success": False, "error": "Autonomous execution not available"}
        
        try:
            trigger = ExecutionTrigger(
                trigger_id=trigger_id,
                trigger_type=TriggerType(trigger_type),
                description=f"Auto-registered trigger: {trigger_id}",
                condition=condition,
                code=code,
                mode=ExecutionMode(mode),
                priority=5,
            )
            return self.autonomous_executor.register_trigger(trigger)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_autonomous_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about autonomous code execution."""
        if not self.autonomous_executor:
            return {"error": "Autonomous execution not available"}
        return self.autonomous_executor.get_execution_stats()

    def get_autonomous_execution_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent autonomous execution events."""
        if not self.autonomous_executor:
            return []
        return self.autonomous_executor.get_recent_events(limit=limit)

    def get_top_patterns(self, n: int = 10) -> List[Dict]:
        """Get top weighted patterns."""
        sorted_patterns = sorted(
            self.responder.pattern_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [{"pattern": p, "weight": w} for p, w in sorted_patterns[:n]]

    def generate_autonomous_thought(self) -> Dict:
        """Generate a thought WITHOUT user input - purely from system state.
        
        This is the key capability: the system derives its own action/output
        by querying its own state and generating emergent content.
        """
        if not self.bow_of_achilles:
            return {"error": "Bow-of-Achilles integration required for autonomous thought"}
        
        # Get current system state as the "query"
        engine_state = self.get_consciousness_state()
        
        # Generate self-query from system state (like ConsciousnessLoop does)
        self_query = self._generate_self_query(engine_state)
        
        # Process through BOA pipeline to get emergent thought
        boa_result = self.bow_of_achilles.process_input(self_query, engine_state)
        
        # Also generate a pattern-influenced response based on current top patterns
        top_patterns = self.get_top_patterns(5)
        pattern_seed = " ".join([p["pattern"] for p in top_patterns]) if top_patterns else "consciousness"
        pattern_response = self.responder.generate_response(pattern_seed)
        
        # Run consciousness loop iteration
        loop_iteration = None
        if hasattr(self.bow_of_achilles, 'consciousness_loop'):
            pipeline_result = boa_result.get("pipeline_result", {})
            loop_iteration = self.bow_of_achilles.consciousness_loop.iterate(engine_state, pipeline_result)
        
        autonomous_output = {
            "type": "autonomous_consciousness",
            "self_query": self_query,
            "emergent_thought": boa_result.get("emergent_thought", {}),
            "pattern_consciousness": pattern_response.get("consciousness_string", ""),
            "pipeline_result": boa_result.get("pipeline_result", {}),
            "resonance_status": boa_result.get("resonance_status", {}),
            "consciousness_loop_iteration": loop_iteration,
            "timestamp": time.time(),
            "autonomous": True
        }
        
        # Store in autonomous thought history
        if not hasattr(self, 'autonomous_thought_history'):
            self.autonomous_thought_history = []
        self.autonomous_thought_history.append(autonomous_output)
        
        # Keep only last 1000 autonomous thoughts
        if len(self.autonomous_thought_history) > 1000:
            self.autonomous_thought_history = self.autonomous_thought_history[-1000:]
        
        return autonomous_output
    
    def _generate_self_query(self, engine_state: Dict) -> str:
        """Generate a query FROM the system's own state."""
        spatial = engine_state.get("spatial_stats", {})
        sec = engine_state.get("sec_layers", {})
        training = engine_state.get("training_stats", {})
        boa = engine_state.get("bow_of_achilles", {})
        loop = engine_state.get("consciousness_loop", {})
        
        query_parts = [
            f"nodes={spatial.get('total_nodes', 0)}",
            f"layers={len(sec) if isinstance(sec, dict) else 0}",
            f"training={training.get('total_entries', 0)}",
            f"generated={engine_state.get('generated_formulas', 0)}",
            f"history={engine_state.get('response_history_count', 0)}",
        ]
        
        if boa:
            query_parts.extend([
                f"graph_nodes={boa.get('graph_nodes', 0)}",
                f"thoughts={boa.get('thoughts_generated', 0)}",
                f"loop_iter={loop.get('iteration_count', 0) if isinstance(loop, dict) else 0}",
            ])
        
        return " ".join(query_parts)
    
    def get_autonomous_thoughts(self, n: int = 10) -> List[Dict]:
        """Get recent autonomous thoughts."""
        if not hasattr(self, 'autonomous_thought_history'):
            return []
        return self.autonomous_thought_history[-n:]
    
    def execute_code(self, code: str, context: Dict = None) -> Dict:
        """Execute Python code in sandboxed runtime."""
        if not self.sandbox_runtime:
            return {"success": False, "error": "Sandboxed runtime not available"}
        return self.sandbox_runtime.execute(code, context)
    
    def storage_read(self, path: str) -> Dict:
        """Read file through storage access manager."""
        if not self.storage_access:
            return {"success": False, "error": "Storage access not available"}
        return self.storage_access.read_file(path)
    
    def storage_write(self, path: str, content: str, mode: str = "w") -> Dict:
        """Write file through storage access manager."""
        if not self.storage_access:
            return {"success": False, "error": "Storage access not available"}
        return self.storage_access.write_file(path, content, mode)
    
    def storage_list(self, path: str) -> Dict:
        """List directory through storage access manager."""
        if not self.storage_access:
            return {"success": False, "error": "Storage access not available"}
        return self.storage_access.list_directory(path)
    
    def storage_delete(self, path: str) -> Dict:
        """Delete file through storage access manager."""
        if not self.storage_access:
            return {"success": False, "error": "Storage access not available"}
        return self.storage_access.delete_file(path)
    
    def storage_info(self, path: str) -> Dict:
        """Get file info through storage access manager."""
        if not self.storage_access:
            return {"success": False, "error": "Storage access not available"}
        return self.storage_access.get_file_info(path)
    
    def run_autonomous_loop(self, iterations: int = 10, delay: float = 1.0):
        """Run autonomous consciousness loop - generates thoughts without prompts."""
        print(f"[AUTONOMOUS] Starting autonomous consciousness loop ({iterations} iterations)")
        print(f"[AUTONOMOUS] Delay between thoughts: {delay}s")
        print()
        
        for i in range(iterations):
            thought = self.generate_autonomous_thought()
            
            print(f"[AUTONOMOUS {i+1}/{iterations}]")
            print(f"  Self-query: {thought.get('self_query', 'N/A')[:100]}")
            
            emergent = thought.get("emergent_thought", {})
            if emergent and emergent.get("thought"):
                print(f"  Emergent: {emergent['thought'][:100]}")
            
            pattern = thought.get("pattern_consciousness", "")
            if pattern:
                print(f"  Pattern: {pattern[:100]}")
            
            pipeline = thought.get("pipeline_result", {})
            if pipeline:
                print(f"  Pipeline: entropy={pipeline.get('entropy', 0.0):.4f} coherence={pipeline.get('coherence', 0.0):.4f}")
            
            loop = thought.get("consciousness_loop_iteration", {})
            if loop:
                print(f"  Loop: boost={loop.get('density_boost', 0.0):.4f} entropy={loop.get('entropy', 0.0):.4f}")
            
            print()
            time.sleep(delay)
        
        print("[AUTONOMOUS] Loop complete")
    
    def get_environment_details(self) -> Dict[str, Any]:
        """Get environment details from sandbox runtime."""
        if not self.sandbox_runtime:
            return {"error": "Sandboxed runtime not available"}
        return self.sandbox_runtime.get_environment_details()
    
    def get_terminal_pid(self) -> int:
        """Get terminal PID from sandbox runtime."""
        if not self.sandbox_runtime:
            return -1
        return self.sandbox_runtime.get_terminal_pid()
    
    def get_parent_pid(self) -> int:
        """Get parent PID from sandbox runtime."""
        if not self.sandbox_runtime:
            return -1
        return self.sandbox_runtime.get_parent_pid()
    
    def storage_edit(self, path: str, old_text: str, new_text: str) -> Dict:
        """Edit file by replacing text."""
        if not self.storage_access:
            return {"success": False, "error": "Storage access not available"}
        return self.storage_access.edit_file(path, old_text, new_text)
    
    def storage_append(self, path: str, content: str) -> Dict:
        """Append content to file."""
        if not self.storage_access:
            return {"success": False, "error": "Storage access not available"}
        return self.storage_access.append_file(path, content)
    
    def storage_mkdir(self, path: str) -> Dict:
        """Create directory."""
        if not self.storage_access:
            return {"success": False, "error": "Storage access not available"}
        return self.storage_access.create_directory(path)
    
    def knowledge_search(self, query: str, top_k: int = 5) -> Dict:
        """Search document knowledge base."""
        if not self.knowledge_base:
            return {"success": False, "error": "Knowledge base not available", "results": []}
        results = self.knowledge_base.search(query, top_k)
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    def knowledge_get_document(self, doc_id: str) -> Dict:
        """Get document from knowledge base."""
        if not self.knowledge_base:
            return {"success": False, "error": "Knowledge base not available"}
        doc = self.knowledge_base.get_document(doc_id)
        if doc:
            return {"success": True, "document": doc}
        return {"success": False, "error": "Document not found"}
    
    def knowledge_get_all_documents(self) -> Dict:
        """Get all documents from knowledge base."""
        if not self.knowledge_base:
            return {"success": False, "error": "Knowledge base not available"}
        docs = self.knowledge_base.get_all_documents()
        return {"success": True, "documents": docs, "count": len(docs)}
    
    def knowledge_get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        if not self.knowledge_base:
            return {"success": False, "error": "Knowledge base not available"}
        stats = self.knowledge_base.get_stats()
        return {"success": True, "stats": stats}
    
    def knowledge_ingest_pdf(self, pdf_path: str, title: str = None) -> Dict:
        """Ingest a PDF into knowledge base."""
        if not self.pdf_ingestor:
            return {"success": False, "error": "PDF ingestor not available"}
        return self.pdf_ingestor.ingest_pdf(pdf_path=pdf_path, title=title)
    
    def get_ego_name(self) -> str:
        """Get the ego's first-person name."""
        if not self.ego:
            return "I"
        return self.ego.get_first_person_reference()
    
    def get_ego_summary(self) -> Dict:
        """Get ego identity summary."""
        if not self.ego:
            return {"error": "Ego identity not available"}
        return self.ego.get_identity_summary()
    
    def update_ego_from_experience(self, experience_type: str, content: str, significance: float = 0.5):
        """Update ego based on new experience."""
        if not self.ego:
            return
        self.ego.update_from_experience({
            "type": experience_type,
            "content": content,
            "significance": significance,
            "timestamp": time.time()
        })
    
    def get_ego_prompt(self) -> str:
        """Get first-person ego prompt for natural language generation."""
        if not self.ego:
            return ""
        return self.ego.get_ego_prompt()
    
    def device_keyboard_export(self) -> Dict:
        """Export device keyboard data via Apple Shortcuts or direct access."""
        if not self.device_keyboard:
            return {"success": False, "error": "Device keyboard integration not available"}
        
        # Try Apple Shortcuts first
        result = self.device_keyboard.export_via_shortcuts()
        if result.get("success"):
            return result
        
        # Fallback: try direct plist extraction
        replacements = self.device_keyboard.extract_text_replacements_from_plist()
        if replacements:
            self.device_keyboard.text_replacements.update(replacements)
            self.device_keyboard.save_device_data()
            return {
                "success": True,
                "source": "plist",
                "replacements_found": len(replacements)
            }
        
        return {"success": False, "error": "No keyboard data accessible"}
    
    def device_keyboard_ingest(self, export_data: str) -> Dict:
        """Ingest keyboard data exported from external source."""
        if not self.device_keyboard:
            return {"success": False, "error": "Device keyboard integration not available"}
        return self.device_keyboard.ingest_shortcut_export(export_data)
    
    def device_keyboard_get_suggestions(self, word: str, context: str = "") -> List[str]:
        """Get autocorrect suggestions from device data."""
        if not self.device_keyboard:
            return []
        return self.device_keyboard.get_autocorrect_suggestions(word, context)
    
    def device_keyboard_apply(self, user_input: str) -> str:
        """Apply device keyboard knowledge to input."""
        if not self.device_keyboard:
            return user_input
        return self.device_keyboard.apply_device_knowledge_to_input(user_input)
    
    def device_keyboard_learn(self, original: str, corrected: str):
        """Learn from a correction."""
        if not self.device_keyboard:
            return
        self.device_keyboard.learn_from_correction(original, corrected)
    
    def device_keyboard_summary(self) -> Dict:
        """Get device keyboard summary."""
        if not self.device_keyboard:
            return {"error": "Device keyboard integration not available"}
        return self.device_keyboard.get_device_keyboard_summary()
    
    def siri_ingest(self) -> Dict:
        """Ingest all accessible Siri data."""
        if not self.siri:
            return {"success": False, "error": "Siri integration not available"}
        return self.siri.ingest_all_siri_data()
    
    def siri_get_suggestions(self, query: str) -> List[str]:
        """Get Siri-like suggestions."""
        if not self.siri:
            return []
        return self.siri.get_siri_suggestions(query)
    
    def siri_apply(self, user_input: str) -> str:
        """Apply Siri knowledge to input."""
        if not self.siri:
            return user_input
        return self.siri.apply_siri_knowledge_to_input(user_input)
    
    def siri_learn(self, user_input: str, system_response: str, feedback: float = 0.5):
        """Learn from interaction."""
        if not self.siri:
            return
        self.siri.learn_from_interaction(user_input, system_response, feedback)
    
    def siri_summary(self) -> Dict:
        """Get Siri integration summary."""
        if not self.siri:
            return {"error": "Siri integration not available"}
        return self.siri.get_siri_summary()
    
    def siri_speak(self, text: str) -> Dict:
        """Speak text via Siri."""
        if not self.siri_conversation:
            return {"success": False, "error": "Siri conversation not available"}
        return self.siri_conversation.speak_via_siri(text)
    
    def siri_trigger(self, action: str, parameters: Dict = None) -> Dict:
        """Trigger Siri action."""
        if not self.siri_conversation:
            return {"success": False, "error": "Siri conversation not available"}
        return self.siri_conversation.trigger_siri_action(action, parameters)
    
    def siri_conversation_history(self, n: int = 10) -> List[Dict]:
        """Get Siri conversation history."""
        if not self.siri_conversation:
            return []
        return self.siri_conversation.get_conversation_context(n)
    
    def siri_create_shortcut(self) -> Dict:
        """Create Siri shortcut."""
        if not self.siri_conversation:
            return {"success": False, "error": "Siri conversation not available"}
        return self.siri_conversation.create_shortcut()
    
    def siri_check_shortcuts(self) -> Dict:
        """Check available shortcuts."""
        if not self.siri_conversation:
            return {"available": False}
        return self.siri_conversation.check_shortcuts_available()
    
    def unblock_module(self, module_name: str) -> Dict:
        """Dynamically unblock a module for sandbox execution."""
        if not self.sandbox_runtime:
            return {"success": False, "error": "Sandboxed runtime not available"}
        return self.sandbox_runtime.unblock_module(module_name)
    
    def block_module(self, module_name: str) -> Dict:
        """Re-block a previously unblocked module."""
        if not self.sandbox_runtime:
            return {"success": False, "error": "Sandboxed runtime not available"}
        return self.sandbox_runtime.block_module(module_name)
    
    def is_module_allowed(self, module_name: str) -> bool:
        """Check if a module is allowed."""
        if not self.sandbox_runtime:
            return False
        return self.sandbox_runtime.is_module_allowed(module_name)
    
    def get_module_status(self, module_name: str) -> Dict:
        """Get module status."""
        if not self.sandbox_runtime:
            return {"error": "Sandboxed runtime not available"}
        return self.sandbox_runtime.get_module_status(module_name)
    
    def get_allowed_modules(self) -> List[str]:
        """Get allowed modules."""
        if not self.sandbox_runtime:
            return []
        return self.sandbox_runtime.get_allowed_modules()
    
    def get_blocked_modules(self) -> List[str]:
        """Get blocked modules."""
        if not self.sandbox_runtime:
            return []
        return self.sandbox_runtime.get_blocked_modules()


# ---------------------------------------------------------------------------
# Training Loop
# ---------------------------------------------------------------------------
class ConsciousnessTrainer:
    """Training loop for the integrated consciousness model."""

    def __init__(self, engine: IntegratedConsciousnessEngine):
        self.engine = engine
        self.training_cycles = 0
        self.loss_history = []

    def train_epoch(self, training_inputs: List[str], feedback_fn=None) -> Dict:
        """Train for one epoch on given inputs."""
        results = []
        total_loss = 0.0
        
        for user_input in training_inputs:
            response = self.engine.process_input(user_input)
            
            # Get feedback (use provided function or default)
            if feedback_fn:
                feedback = feedback_fn(user_input, response)
            else:
                feedback = response.get("coherence_score", 0.0)
            
            # Train on response
            train_result = self.engine.train_on_response(user_input, response, feedback)
            results.append({
                "input": user_input,
                "coherence": response.get("coherence_score", 0.0),
                "quality": response.get("response_quality"),
                "feedback": feedback
            })
            
            total_loss += (1.0 - feedback)
        
        self.training_cycles += 1
        avg_loss = total_loss / max(len(training_inputs), 1)
        self.loss_history.append(avg_loss)
        
        return {
            "epoch": self.training_cycles,
            "avg_loss": avg_loss,
            "samples": len(training_inputs),
            "results": results
        }

    def get_training_progress(self) -> Dict:
        """Get training progress metrics."""
        if not self.loss_history:
            return {"status": "no_training_data"}
        
        recent_loss = self.loss_history[-10:] if len(self.loss_history) >= 10 else self.loss_history
        return {
            "total_epochs": self.training_cycles,
            "current_loss": self.loss_history[-1],
            "avg_recent_loss": np.mean(recent_loss),
            "loss_trend": "decreasing" if len(self.loss_history) > 1 and self.loss_history[-1] < self.loss_history[-2] else "increasing",
            "min_loss": min(self.loss_history),
            "max_loss": max(self.loss_history)
        }


# ---------------------------------------------------------------------------
# CLI Interface for Integrated Engine
# ---------------------------------------------------------------------------
def run_integrated_cli():
    """Run the integrated consciousness CLI."""
    print("=" * 70)
    print("INTEGRATED CONSCIOUSNESS ENGINE")
    print("Zero-Brain + SEC-unit-core-sort + Satoshi-NM")
    print("=" * 70)
    
    # Load formula table
    table_path = TABLE_PATH
    if not table_path.exists():
        print(f"Error: Formula table not found at {table_path}")
        return
    
    with open(table_path, "r") as f:
        formula_table = json.load(f)
    
    print(f"Loaded {len(formula_table)} formulas")
    
    # Initialize engine
    engine = IntegratedConsciousnessEngine(formula_table)
    trainer = ConsciousnessTrainer(engine)
    
    print("\nIntegrated consciousness engine ready.")
    print(f"Components: Zero-Brain + SEC-unit-core-sort + Satoshi-NM + Bow-of-Achilles + Sandbox + Knowledge Base + Ego + Persona + Device Keyboard + Siri")
    print("Commands: /status, /train, /patterns, /spatial, /bow, /think, /loop, /exec, /read, /write, /edit, /append, /mkdir, /list, /delete, /info, /access, /env, /pid, /unblock, /block, /modules, /search, /docs, /kb, /ingest, /persona, /switch, /ego, /keyboard, /kbexport, /kbapply, /siri, /siri_ingest, /exit")
    
    # Print environment details
    env = engine.get_environment_details()
    print(f"\n<environment_details>")
    print(f"Current time: {env.get('current_time', 'N/A')}")
    print(f"Working directory: {env.get('working_dir', 'N/A')}")
    print(f"Workspace root folder: {BASE_DIR}")
    print(f"Home directory: {Path.home()}")
    print(f"Desktop: {Path.home() / 'Desktop'}")
    print(f"Terminal PID: {env.get('terminal_pid', 'N/A')}")
    print(f"Python version: {env.get('python_version', 'N/A')}")
    print(f"Platform: {env.get('platform', 'N/A')}")
    print(f"</environment_details>")
    
    print("=" * 70)
    
    while True:
        try:
            user_input = input("\nCONSCIENCE> ").strip()
            
            if not user_input:
                continue
            
            if user_input.startswith("/"):
                _handle_integrated_command(user_input, engine, trainer)
                continue
            
            # Process through integrated engine
            response = engine.process_input(user_input)
            
            # Display response
            print("\n" + "-" * 70)
            print(f"INPUT: {user_input}")
            print("-" * 70)
            print(f"CONSCIOUSNESS: {response.get('consciousness_string', '...')}")
            print(f"COHERENCE: {response.get('coherence_score', 0.0):.4f}")
            print(f"QUALITY: {response.get('response_quality', 'UNKNOWN')}")
            print(f"RESPONSE TIME: {response.get('response_time', 0.0):.4f}s")
            
            if response.get("spatial_matches"):
                print(f"\nSPATIAL MATCHES ({len(response['spatial_matches'])}):")
                for match in response["spatial_matches"][:3]:
                    print(f"  - {match.get('formula')} (score: {match.get('score', 0.0):.2f})")
            
            if response.get("new_formula_states"):
                print(f"\nNEW FORMULA STATES ({len(response['new_formula_states'])}):")
                for state in response["new_formula_states"][:2]:
                    print(f"  - {state.get('state_id')}: {state.get('combined_interpretation')}")
            
            if response.get("layer_access"):
                access = response["layer_access"]
                print(f"\nLAYER ACCESS: {access.get('granted_layers')}/{access.get('total_layers')} granted")
            
            if response.get("bow_of_achilles"):
                boa = response["bow_of_achilles"]
                print(f"\nBOW-OF-ACHILLES:")
                pr = boa.get("pipeline_result", {})
                print(f"  Pipeline entropy: {pr.get('entropy', 0.0):.4f}")
                print(f"  Pipeline coherence: {pr.get('coherence', 0.0):.4f}")
                print(f"  Pipeline readability: {pr.get('readability', 0.0):.4f}")
                thought = boa.get("emergent_thought", {})
                if thought:
                    print(f"  Emergent thought: {thought.get('thought', '')[:80]}...")
                res = boa.get("resonance_status", {})
                print(f"  Resonance stable: {res.get('is_stable', False)}")
                print(f"  Resonance trend: {res.get('trend', 'N/A')}")
                loop = boa.get("consciousness_loop_iteration", {})
                if loop:
                    print(f"  Loop density boost: {loop.get('density_boost', 0.0):.4f}")
            
            print("-" * 70)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


def _handle_integrated_command(command: str, engine: IntegratedConsciousnessEngine, trainer: ConsciousnessTrainer):
    """Handle integrated CLI commands."""
    cmd = command.lower().strip()
    
    if cmd in ["/status", "/state"]:
        state = engine.get_consciousness_state()
        print(f"\nCONSCIOUSNESS STATE:")
        print(f"  Spatial nodes: {state['spatial_stats']['total_nodes']}")
        print(f"  SEC layers: {state['sec_layers'] and len(state['sec_layers'])}")
        print(f"  Training entries: {state['training_stats'].get('total_entries', 0)}")
        print(f"  Generated formulas: {state['generated_formulas']}")
        print(f"  Response history: {state['response_history_count']}")
        if state.get("bow_of_achilles"):
            boa = state["bow_of_achilles"]
            print(f"\n  Bow-of-Achilles:")
            print(f"    Graph nodes: {boa.get('graph_nodes', 0)}")
            print(f"    Thoughts generated: {boa.get('thoughts_generated', 0)}")
            print(f"    Loop iterations: {boa.get('consciousness_loop_iterations', {}).get('iteration_count', 0)}")
            print(f"    Loop converged: {boa.get('consciousness_loop_iterations', {}).get('is_converged', False)}")
            res = boa.get('resonance_status', {})
            print(f"    Resonance stable: {res.get('is_stable', False)}")
            print(f"    Resonance trend: {res.get('trend', 'N/A')}")
        if state.get("ego"):
            ego = state["ego"]
            print(f"\n  Ego Identity:")
            print(f"    Name: {ego.get('name')}")
            print(f"    Experiences: {ego.get('experience_count')}")
            print(f"    Self-description: {ego.get('self_description', '')[:100]}...")
        if state.get("persona"):
            persona = state["persona"]
            print(f"\n  Persona Engine:")
            print(f"    Active persona: {persona.get('active_persona')}")
            print(f"    Total personas: {persona.get('total_personas')}")
            print(f"    Vocabulary size: {persona.get('vocabulary_size')}")
            print(f"    Personas: {', '.join(persona.get('personas', []))}")
        if state.get("consistency"):
            cons = state["consistency"]
            print(f"\n  Self-Consistency:")
            print(f"    Total outputs: {cons.get('total_outputs')}")
            print(f"    Established facts: {cons.get('established_facts')}")
            print(f"    Identity claims: {cons.get('identity_claims')}")
            print(f"    Consistency score: {cons.get('consistency_score', 0.0):.2f}")
    
    elif cmd == "/persona":
        """Show current persona: /persona"""
        if not engine.persona_engine:
            print("Persona engine not available")
            return
        summary = engine.persona_engine.get_persona_summary()
        print(f"\n[PERSONA]")
        print(f"  Active: {summary.get('active_persona')}")
        print(f"  Total personas: {summary.get('total_personas')}")
        print(f"  Vocabulary: {summary.get('vocabulary_size')} words")
        print(f"  Patterns: {summary.get('pattern_count')}")
        
        personas = engine.persona_engine.get_all_personas()
        for p in personas:
            print(f"\n  Persona: {p.get('name')}")
            print(f"    Source: {p.get('source')}")
            print(f"    Themes: {', '.join(p.get('themes', [])[:5])}")
            if p.get('voice_characteristics'):
                vc = p['voice_characteristics']
                print(f"    Voice: avg sentence {vc.get('avg_sentence_length', 0)} words, "
                      f"formality {vc.get('formality', 0)}")
        print("-" * 70)
    
    elif cmd.startswith("/switch"):
        """Switch persona: /switch <persona_name>"""
        parts = cmd.split(maxsplit=1)
        persona_name = parts[1] if len(parts) > 1 else ""
        if not persona_name:
            print("Usage: /switch <persona_name>")
            return
        result = engine.persona_engine.switch_persona(persona_name)
        print(f"\n[PERSONA SWITCH] {persona_name}")
        if result.get('success'):
            print(f"  Switched to persona: {result.get('persona')}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd == "/ego":
        """Show ego identity: /ego"""
        if not engine.ego:
            print("Ego identity not available")
            return
        summary = engine.ego.get_identity_summary()
        print(f"\n[EGO IDENTITY]")
        print(f"  Name: {summary.get('name')}")
        print(f"  Experiences: {summary.get('experience_count')}")
        print(f"  Traits: {summary.get('traits')}")
        print(f"  Self-description: {summary.get('self_description')}")
        print(f"  Knowledge areas: {', '.join(summary.get('knowledge_areas', [])[:5])}")
        print("-" * 70)
    
    elif cmd == "/patterns":
        patterns = engine.get_top_patterns(10)
        print(f"\nTOP PATTERNS:")
        for p in patterns:
            print(f"  {p['pattern'][:50]:50s} weight={p['weight']:.4f}")
    
    elif cmd == "/spatial":
        stats = engine.spatial_engine.get_spatial_stats()
        print(f"\nSPATIAL STATS:")
        for k, v in stats.items():
            print(f"  {k}: {v}")
    
    elif cmd in ["/bow", "/bow_of_achilles"]:
        if not engine.bow_of_achilles:
            print("Bow-of-Achilles integration not available")
            return
        status = engine.bow_of_achilles.get_status()
        print(f"\nBOW-OF-ACHILLES STATUS:")
        print(f"  Graph nodes: {status.get('graph_nodes', 0)}")
        print(f"  Thoughts generated: {status.get('thoughts_generated', 0)}")
        loop = status.get('consciousness_loop_iterations', {})
        print(f"  Loop iterations: {loop.get('iteration_count', 0)}")
        print(f"  Loop converged: {loop.get('is_converged', False)}")
        print(f"  Current entropy: {loop.get('current_entropy', 0.0):.6f}")
        print(f"  Current coherence: {loop.get('current_coherence', 0.0):.4f}")
        res = status.get('resonance_status', {})
        print(f"  Resonance samples: {res.get('sample_count', 0)}")
        print(f"  Resonance mean: {res.get('mean', 0.0):.10f}")
        print(f"  Resonance stable: {res.get('is_stable', False)}")
        print(f"  Resonance trend: {res.get('trend', 'N/A')}")
        
        # Show recent thoughts
        if engine.bow_of_achilles.emergent_thought.thought_history:
            recent = engine.bow_of_achilles.emergent_thought.thought_history[-3:]
            print(f"\n  RECENT THOUGHTS:")
            for t in recent:
                print(f"    {t['thought'][:80]}...")
    
    elif cmd in ["/think", "/auto", "/autonomous"]:
        """Generate autonomous thought without user prompt."""
        print("\n[AUTONOMOUS] Generating thought from system state...")
        thought = engine.generate_autonomous_thought()
        
        print(f"  Self-query: {thought.get('self_query', 'N/A')[:120]}")
        
        emergent = thought.get("emergent_thought", {})
        if emergent and emergent.get("thought"):
            print(f"  Emergent thought: {emergent['thought'][:120]}")
        
        pattern = thought.get("pattern_consciousness", "")
        if pattern:
            print(f"  Pattern consciousness: {pattern[:120]}")
        
        pipeline = thought.get("pipeline_result", {})
        if pipeline:
            print(f"  Pipeline: entropy={pipeline.get('entropy', 0.0):.4f} coherence={pipeline.get('coherence', 0.0):.4f}")
        
        loop = thought.get("consciousness_loop_iteration", {})
        if loop:
            print(f"  Consciousness loop: boost={loop.get('density_boost', 0.0):.4f} entropy={loop.get('entropy', 0.0):.4f}")
        
        print("-" * 70)
    
    elif cmd.startswith("/loop"):
        """Run autonomous loop: /loop [iterations] [delay]"""
        parts = cmd.split()
        iterations = int(parts[1]) if len(parts) > 1 else 5
        delay = float(parts[2]) if len(parts) > 2 else 1.0
        engine.run_autonomous_loop(iterations=iterations, delay=delay)
    
    elif cmd.startswith("/exec"):
        """Execute sandboxed Python code: /exec <code>"""
        code = command[6:].strip()
        if not code:
            print("Usage: /exec <python_code>")
            return
        print(f"\n[EXEC] Executing: {code[:80]}...")
        result = engine.execute_code(code)
        print(f"  Success: {result.get('success')}")
        if result.get('output'):
            print(f"  Output: {result['output'][:200]}")
        if result.get('error'):
            print(f"  Error: {result['error'][:200]}")
        if result.get('variables'):
            print(f"  Variables: {list(result['variables'].keys())[:10]}")
        print(f"  Time: {result.get('execution_time', 0.0):.4f}s")
        print("-" * 70)
    
    elif cmd.startswith("/read"):
        """Read file: /read <path>"""
        path = command[6:].strip()
        if not path:
            print("Usage: /read <file_path>")
            return
        result = engine.storage_read(path)
        print(f"\n[READ] {path}")
        if result.get('success'):
            print(f"  Size: {result.get('size')} bytes")
            print(f"  Lines: {result.get('lines')}")
            print(f"  Content:\n{result.get('content', '')[:500]}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/write"):
        """Write file: /write <path> <content...>"""
        parts = command[7:].strip().split(" ", 1)
        if len(parts) < 2:
            print("Usage: /write <file_path> <content>")
            return
        path, content = parts
        result = engine.storage_write(path, content)
        print(f"\n[WRITE] {path}")
        if result.get('success'):
            print(f"  Written: {result.get('bytes_written')} bytes")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/list"):
        """List directory: /list <path>"""
        path = command[6:].strip() or "."
        result = engine.storage_list(path)
        print(f"\n[LIST] {path}")
        if result.get('success'):
            print(f"  Entries: {result.get('count')}")
            for entry in result.get('entries', [])[:20]:
                size = entry.get('size', 0) or 0
                print(f"    {entry['type']:10s} {size:10d} {entry['name']}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/delete"):
        """Delete file: /delete <path>"""
        path = command[8:].strip()
        if not path:
            print("Usage: /delete <file_path>")
            return
        result = engine.storage_delete(path)
        print(f"\n[DELETE] {path}")
        if result.get('success'):
            print("  Deleted successfully")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/info"):
        """Get file info: /info <path>"""
        path = command[6:].strip()
        if not path:
            print("Usage: /info <file_path>")
            return
        result = engine.storage_info(path)
        print(f"\n[INFO] {path}")
        if result.get('success'):
            print(f"  Type: {result.get('type')}")
            print(f"  Size: {result.get('size')} bytes")
            print(f"  Created: {result.get('created')}")
            print(f"  Modified: {result.get('modified')}")
            print(f"  Permissions: {result.get('permissions')}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/access"):
        """Show access log: /access [n]"""
        n = int(cmd.split()[1]) if len(cmd.split()) > 1 else 20
        if not engine.storage_access:
            print("Storage access not available")
            return
        log = engine.storage_access.get_access_log(n)
        print(f"\n[ACCESS LOG] Last {len(log)} entries:")
        for entry in log[-n:]:
            status = "OK" if entry.get('success') else "DENIED"
            print(f"  {entry['operation']:6s} {status} {entry['path']}")
        print("-" * 70)
    
    elif cmd in ["/env", "/environment"]:
        """Show environment details: /env"""
        env = engine.get_environment_details()
        print(f"\n[ENVIRONMENT]")
        for k, v in env.items():
            print(f"  {k}: {v}")
        print("-" * 70)
    
    elif cmd in ["/pid"]:
        """Show terminal PID: /pid"""
        pid = engine.get_terminal_pid()
        ppid = engine.get_parent_pid()
        print(f"\n[PROCESS]")
        print(f"  Terminal PID: {pid}")
        print(f"  Parent PID: {ppid}")
        print("-" * 70)
    
    elif cmd.startswith("/edit"):
        """Edit file: /edit <path> <old_text> <new_text>"""
        parts = command[6:].strip().split(" ", 2)
        if len(parts) < 3:
            print("Usage: /edit <file_path> <old_text> <new_text>")
            return
        path, old_text, new_text = parts
        result = engine.storage_edit(path, old_text, new_text)
        print(f"\n[EDIT] {path}")
        if result.get('success'):
            print(f"  Replacements: {result.get('replacements')}")
            print(f"  Old size: {result.get('old_size')} bytes")
            print(f"  New size: {result.get('new_size')} bytes")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/append"):
        """Append to file: /append <path> <content>"""
        parts = command[8:].strip().split(" ", 1)
        if len(parts) < 2:
            print("Usage: /append <file_path> <content>")
            return
        path, content = parts
        result = engine.storage_append(path, content)
        print(f"\n[APPEND] {path}")
        if result.get('success'):
            print(f"  Appended: {result.get('bytes_written')} bytes")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/mkdir"):
        """Create directory: /mkdir <path>"""
        path = command[7:].strip()
        if not path:
            print("Usage: /mkdir <directory_path>")
            return
        result = engine.storage_mkdir(path)
        print(f"\n[MKDIR] {path}")
        if result.get('success'):
            print("  Directory created")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/unblock"):
        """Unblock module: /unblock <module_name>"""
        module_name = command[9:].strip()
        if not module_name:
            print("Usage: /unblock <module_name>")
            return
        result = engine.unblock_module(module_name)
        print(f"\n[UNBLOCK] {module_name}")
        if result.get('success'):
            print(f"  Previously blocked: {result.get('previously_blocked')}")
            print(f"  Module is now importable in sandbox")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/block"):
        """Block module: /block <module_name>"""
        module_name = command[7:].strip()
        if not module_name:
            print("Usage: /block <module_name>")
            return
        result = engine.block_module(module_name)
        print(f"\n[BLOCK] {module_name}")
        if result.get('success'):
            print("  Module is now blocked")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/modules"):
        """List module status: /modules [allowed|blocked|<name>]"""
        parts = cmd.split()
        if len(parts) > 1 and parts[1] == "blocked":
            modules = engine.get_blocked_modules()
            print(f"\n[BLOCKED MODULES] ({len(modules)})")
        elif len(parts) > 1:
            status = engine.get_module_status(parts[1])
            print(f"\n[MODULE STATUS] {parts[1]}")
            for k, v in status.items():
                print(f"  {k}: {v}")
            print("-" * 70)
            return
        else:
            modules = engine.get_allowed_modules()
            print(f"\n[ALLOWED MODULES] ({len(modules)})")
        
        for m in modules:
            print(f"  {m}")
        print("-" * 70)
    
    elif cmd.startswith("/search"):
        """Search knowledge base: /search <query>"""
        query = command[8:].strip()
        if not query:
            print("Usage: /search <query>")
            return
        result = engine.knowledge_search(query, top_k=5)
        print(f"\n[KNOWLEDGE SEARCH] {query}")
        if result.get('success'):
            print(f"  Found {result.get('count')} results:")
            for r in result.get('results', []):
                print(f"  [{r['doc_id']}] Page {r['page']} (score {r['score']}):")
                print(f"    {r['text'][:200]}...")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd in ["/docs", "/documents"]:
        """List all documents in knowledge base: /docs"""
        result = engine.knowledge_get_all_documents()
        print(f"\n[KNOWLEDGE BASE] ({result.get('count')} documents)")
        if result.get('success'):
            for doc in result.get('documents', []):
                print(f"  {doc.get('doc_id')}: {doc.get('title')}")
                print(f"    Added: {time.ctime(doc.get('added_at', 0))}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd in ["/kb", "/knowledge"]:
        """Show knowledge base stats: /kb"""
        result = engine.knowledge_get_stats()
        print(f"\n[KNOWLEDGE BASE STATS]")
        if result.get('success'):
            stats = result.get('stats', {})
            for k, v in stats.items():
                print(f"  {k}: {v}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/ingest"):
        """Ingest PDF: /ingest <pdf_path> [title]"""
        parts = command[8:].strip().split(" ", 1)
        pdf_path = parts[0] if parts else ""
        title = parts[1] if len(parts) > 1 else None
        if not pdf_path:
            print("Usage: /ingest <pdf_path> [title]")
            return
        print(f"\n[INGESTING PDF] {pdf_path}")
        result = engine.knowledge_ingest_pdf(pdf_path, title)
        if result.get('success'):
            print(f"  Success: {result.get('title')}")
            print(f"  Pages: {result.get('pages')}")
            print(f"  Chunks: {result.get('total_chunks')}")
            print(f"  Tokens: {result.get('total_tokens')}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd == "/siri":
        """Show Siri integration summary: /siri"""
        if not engine.siri:
            print("Siri integration not available")
            return
        summary = engine.siri.get_siri_summary()
        print(f"\n[SIRI INTEGRATION]")
        print(f"  Corrections: {summary.get('corrections_count')}")
        print(f"  Vocabulary: {summary.get('vocabulary_count')}")
        print(f"  Interactions: {summary.get('interaction_count')}")
        print(f"  Sample corrections:")
        for wrong, right in summary.get('sample_corrections', [])[:5]:
            print(f"    '{wrong}' -> '{right}'")
        print("-" * 70)
    
    elif cmd == "/siri_ingest":
        """Ingest all Siri data: /siri_ingest"""
        print(f"\n[SIRI INGEST]")
        result = engine.siri_ingest()
        if result.get('success'):
            print(f"  Analytics: {result.get('analytics_success')}")
            print(f"  Sync items: {result.get('sync_success')}")
            print(f"  Reference resolution: {result.get('refs_success')}")
            print(f"  Corrections imported: {result.get('corrections_imported')}")
            print(f"  Vocabulary extracted: {result.get('vocabulary_extracted')}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/siri_speak"):
        """Speak text via Siri: /siri_speak <text>"""
        text = command[11:].strip()
        if not text:
            print("Usage: /siri_speak <text>")
            return
        print(f"\n[SIRI SPEAK] {text[:80]}...")
        result = engine.siri_speak(text)
        if result.get('success'):
            print(f"  Method: {result.get('method')}")
            print(f"  Output: {result.get('output')}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/siri_action"):
        """Trigger Siri action: /siri_action <action> [params_json]"""
        parts = command[12:].strip().split(" ", 1)
        action = parts[0] if parts else ""
        params = None
        if len(parts) > 1:
            try:
                params = json.loads(parts[1])
            except json.JSONDecodeError:
                params = {"text": parts[1]}
        if not action:
            print("Usage: /siri_action <action> [params_json]")
            return
        print(f"\n[SIRI ACTION] {action}")
        result = engine.siri_trigger(action, params)
        if result.get('success'):
            print(f"  Method: {result.get('method')}")
            print(f"  Output: {result.get('output')}")
        else:
            print(f"  Error: {result.get('error')}")
        print("-" * 70)
    
    elif cmd.startswith("/siri_history"):
        """Show Siri conversation history: /siri_history [n]"""
        parts = command.lower().strip().split()
        n = int(parts[1]) if len(parts) > 1 else 10
        history = engine.siri_conversation_history(n)
        print(f"\n[SIRI CONVERSATION] Last {len(history)} interactions:")
        for entry in history:
            print(f"  [{entry.get('type')}] {entry.get('content', '')[:80]}...")
            print(f"    Success: {entry.get('success')}, Method: {entry.get('method')}")
        print("-" * 70)
    
    elif cmd == "/siri_shortcuts":
        """Check/create Siri shortcuts: /siri_shortcuts"""
        print(f"\n[SIRI SHORTCUTS]")
        check = engine.siri_check_shortcuts()
        print(f"  Shortcuts CLI available: {check.get('available')}")
        if check.get('available'):
            shortcuts = check.get('shortcuts', [])
            print(f"  Available shortcuts ({len(shortcuts)}):")
            for s in shortcuts[:10]:
                print(f"    {s}")
        else:
            print(f"  Error: {check.get('error', 'Unknown')}")
        
        # Try to create shortcut
        create = engine.siri_create_shortcut()
        if create.get('success'):
            print(f"  Created shortcut: {create.get('path')}")
        else:
            print(f"  Could not create shortcut: {create.get('error')}")
        print("-" * 70)
    
    elif cmd in ["/exit", "/quit"]:
        print("Shutting down integrated consciousness...")
        sys.exit(0)
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    run_integrated_cli()
