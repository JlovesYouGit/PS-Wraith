#!/usr/bin/env python3
"""
Self-Consistency System for Consciousness
==========================================
Ensures the system's outputs are coherent with its established identity,
knowledge, and previous outputs. No contradictions, no identity drift.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional


class SelfConsistencyLayer:
    """Maintains coherence across the system's outputs and identity."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.consistency_file = base_path / ".self_consistency.json"
        self.output_history: List[Dict] = []
        self.established_facts: Dict[str, Any] = {}
        self.identity_claims: List[str] = []
        self.value_weights: Dict[str, float] = {}
        self.load_consistency_state()

    def load_consistency_state(self):
        """Load existing consistency state."""
        if self.consistency_file.exists():
            try:
                with open(self.consistency_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.output_history = data.get("output_history", [])
                self.established_facts = data.get("established_facts", {})
                self.identity_claims = data.get("identity_claims", [])
                self.value_weights = data.get("value_weights", {})
            except Exception:
                pass

    def save_consistency_state(self):
        """Save consistency state to disk."""
        data = {
            "output_history": self.output_history[-100:],
            "established_facts": self.established_facts,
            "identity_claims": self.identity_claims[-50:],
            "value_weights": self.value_weights,
            "updated_at": time.time()
        }
        try:
            with open(self.consistency_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass

    def validate_output(self, output: str, context: Dict) -> Dict:
        """Validate output against established consistency rules.
        
        Returns:
            {
                "consistent": bool,
                "score": float,
                "conflicts": List[str],
                "suggestions": List[str]
            }
        """
        output_lower = output.lower()
        conflicts = []
        suggestions = []
        
        # Check against established facts
        for fact, value in self.established_facts.items():
            if fact.lower() in output_lower:
                # Check if output contradicts established fact
                if isinstance(value, str) and value.lower() != output_lower:
                    conflicts.append(f"Contradicts established fact: {fact}")
        
        # Check against identity claims
        for claim in self.identity_claims[-10:]:
            if claim.lower() in output_lower:
                # Consistent with identity
                pass
        
        # Calculate consistency score
        base_score = 1.0
        if conflicts:
            base_score -= len(conflicts) * 0.2
        if not self.identity_claims:
            base_score -= 0.1  # Penalty for no established identity
        
        score = max(0.0, min(1.0, base_score))
        
        return {
            "consistent": len(conflicts) == 0,
            "score": score,
            "conflicts": conflicts,
            "suggestions": suggestions
        }

    def record_output(self, output: str, context: Dict, metadata: Dict = None):
        """Record an output for consistency tracking."""
        record = {
            "output": output[:500],
            "timestamp": time.time(),
            "context_keys": list(context.keys()) if context else [],
            "metadata": metadata or {}
        }
        self.output_history.append(record)
        
        # Extract and store facts from output
        self._extract_facts(output)
        
        # Maintain history size
        if len(self.output_history) > 100:
            self.output_history = self.output_history[-100:]
        
        self.save_consistency_state()

    def _extract_facts(self, text: str):
        """Extract factual claims from text."""
        sentences = text.replace("?", ".").replace("!", ".").split(".")
        
        for sentence in sentences:
            s = sentence.strip()
            if len(s) > 20 and len(s) < 500:
                # Simple fact extraction - store as-is
                key = hashlib.sha256(s.encode()).hexdigest()[:12]
                self.established_facts[key] = s[:200]

    def establish_identity_claim(self, claim: str):
        """Establish a core identity claim that should persist."""
        if claim and claim not in self.identity_claims:
            self.identity_claims.append(claim)
            self.save_consistency_state()

    def get_consistency_prompt(self) -> str:
        """Generate a prompt fragment that enforces consistency."""
        if not self.identity_claims and not self.established_facts:
            return ""
        
        prompt = "\nMaintain consistency with established identity:\n"
        
        if self.identity_claims:
            prompt += f"Core identity: {self.identity_claims[-1]}\n"
        
        if self.established_facts:
            recent_facts = list(self.established_facts.values())[-3:]
            prompt += f"Recent context: {' | '.join(recent_facts)}\n"
        
        return prompt

    def get_output_history(self, n: int = 10) -> List[Dict]:
        """Get recent output history for context."""
        return self.output_history[-n:]

    def get_consistency_stats(self) -> Dict:
        """Get consistency statistics."""
        return {
            "total_outputs": len(self.output_history),
            "established_facts": len(self.established_facts),
            "identity_claims": len(self.identity_claims),
            "consistency_score": self._calculate_overall_consistency()
        }

    def _calculate_overall_consistency(self) -> float:
        """Calculate overall consistency score."""
        if not self.output_history:
            return 0.0
        
        # Simple metric: variance in output length and structure
        lengths = [len(o.get("output", "")) for o in self.output_history]
        if not lengths:
            return 0.0
        
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        
        # Lower variance = higher consistency
        return max(0.0, min(1.0, 1.0 - (variance / 10000)))
