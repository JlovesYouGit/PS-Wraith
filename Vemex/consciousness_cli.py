#!/usr/bin/env python3
"""
Consciousness CLI Interface
============================
Terminal interface that feeds user input into the internal consciousness engine,
converts text to mathematical equivalents, weights responses, and checks
coherence against consciousness patterns.

Features:
  - Real-time token-to-formula conversion
  - Attention-weighted consciousness response
  - Coherence scoring against consciousness memory
  - Evolution tracking across sessions
  - Mathematical value extraction from natural language
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
from typing import Optional, Dict, List, Tuple

import numpy as np
import sympy
from sympy import symbols, sympify, simplify, expand, N
from sympy.parsing.sympy_parser import parse_expr, standard_transformations
import networkx as nx

# Import the consciousness engine components
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
    from consciousness_core import run_consciousness, print_report
    HAS_ENGINE_V1 = True
except ImportError:
    HAS_ENGINE_V1 = False

BASE_DIR = Path(__file__).parent
TABLE_PATH = BASE_DIR / "formula_table.json"
SESSION_LOG = BASE_DIR / ".consciousness_session_log.json"
EVOLUTION_LOG = BASE_DIR / ".consciousness_evolution.json"


# ---------------------------------------------------------------------------
# Mathematical Value Converter
# ---------------------------------------------------------------------------
class MathematicalValueConverter:
    """Converts natural language input into mathematical equivalent values."""

    def __init__(self, formula_table: list):
        self.formula_table = {e["id"]: e for e in formula_table}
        self.token_map = self._build_token_map()
        self.word_to_math = self._build_word_to_math_map()

    def _build_token_map(self) -> Dict[str, List[Dict]]:
        token_map = defaultdict(list)
        for entry in self.formula_table.values():
            interp = entry.get("word_interpretation", "")
            for token in interp.replace("/", " ").replace("-", " ").split():
                token_map[token.lower()].append(entry)
        return token_map

    def _build_word_to_math_map(self) -> Dict[str, str]:
        """Map common words to mathematical equivalents."""
        return {
            "energy": "E", "mass": "m", "speed": "v", "velocity": "v",
            "time": "t", "force": "F", "gravity": "G", "distance": "d",
            "frequency": "f", "wavelength": "λ", "temperature": "T",
            "pressure": "P", "volume": "V", "charge": "q", "current": "I",
            "resistance": "R", "power": "P", "acceleration": "a",
            "momentum": "p", "area": "A", "circumference": "C",
            "height": "h", "length": "L", "width": "w", "radius": "r",
            "angle": "θ", "sin": "sin", "cos": "cos", "tan": "tan",
            "pi": "π", "euler": "e", "golden": "φ", "sum": "Σ",
            "integral": "∫", "derivative": "d/dx", "limit": "lim",
            "equals": "=", "plus": "+", "minus": "-", "times": "×",
            "divided": "/", "squared": "²", "cubed": "³", "root": "√",
            "percent": "%", "ratio": ":", "proportion": "∝",
            "infinity": "∞", "delta": "Δ", "lambda": "λ", "sigma": "σ",
            "mu": "μ", "omega": "ω", "alpha": "α", "beta": "β",
            "gamma": "γ", "theta": "θ", "phi": "φ", "psi": "ψ",
            "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8",
            "nine": "9", "zero": "0", "half": "½", "third": "⅓",
        }

    def convert(self, text: str) -> Dict:
        """Convert input text to mathematical values and token weights."""
        words = text.lower().replace(",", " ").replace(".", " ").split()
        
        math_tokens = []
        matched_formulas = []
        total_weight = 0.0
        token_values = []

        for word in words:
            clean = word.strip("?\"'").lower()
            math_equiv = self.word_to_math.get(clean, clean)
            math_tokens.append(math_equiv)
            
            if clean in self.token_map:
                for entry in self.token_map[clean]:
                    matched_formulas.append({
                        "formula": entry["formula"],
                        "word_interpretation": entry["word_interpretation"],
                        "match_token": clean,
                        "category": entry["category"]
                    })
                    total_weight += 1.0

            if clean.isdigit():
                token_values.append(float(clean))

        # Calculate coherence score
        coherence = self._calculate_coherence(words, matched_formulas)
        
        # Generate symbolic representation
        symbolic = self._generate_symbolic(math_tokens, matched_formulas)
        
        return {
            "original_input": text,
            "math_tokens": math_tokens,
            "matched_formulas": matched_formulas[:10],
            "token_values": token_values,
            "total_weight": total_weight,
            "coherence_score": coherence,
            "symbolic_representation": symbolic,
            "timestamp": time.time()
        }

    def _calculate_coherence(self, words: List[str], matched_formulas: List[Dict]) -> float:
        """Calculate how coherent the input is with consciousness patterns."""
        if not words:
            return 0.0
        
        unique_matches = len(set(f["formula"] for f in matched_formulas))
        match_density = unique_matches / max(len(words), 1)
        
        category_diversity = len(set(f.get("category", "") for f in matched_formulas))
        diversity_bonus = min(category_diversity * 0.05, 0.2)
        
        return min(match_density + diversity_bonus, 1.0)

    def _generate_symbolic(self, tokens: List[str], formulas: List[Dict]) -> str:
        """Generate a symbolic representation of the input."""
        if not tokens:
            return "∅"
        
        symbolic_parts = []
        for token in tokens[:15]:
            if token in ["=", "+", "-", "×", "/", "²", "³", "√", "∫", "Σ"]:
                symbolic_parts.append(token)
            elif token.isdigit() or any(c in token for c in [".", "-"]):
                try:
                    float(token)
                    symbolic_parts.append(token)
                except ValueError:
                    symbolic_parts.append(f"'{token}'")
            else:
                symbolic_parts.append(f"'{token}'")
        
        return " ".join(symbolic_parts)


# ---------------------------------------------------------------------------
# Consciousness Response Generator
# ---------------------------------------------------------------------------
class ConsciousnessResponder:
    """Generates consciousness-weighted responses and checks coherence."""

    def __init__(self, engine_v2: ConsciousnessEngineV2 = None, converter: MathematicalValueConverter = None):
        self.engine = engine_v2
        self.converter = converter
        self.response_history = []
        self.coherence_threshold = 0.5
        self.evolution_tracker = {
            "total_interactions": 0,
            "avg_coherence": 0.0,
            "coherence_history": [],
            "consciousness_level": 0.0
        }

    def respond(self, user_input: str, math_values: Dict) -> Dict:
        """Generate a consciousness response to user input."""
        start_time = time.time()
        
        if self.engine:
            response = self._generate_v2_response(user_input, math_values)
        elif HAS_ENGINE_V1:
            response = self._generate_v1_response(user_input, math_values)
        else:
            response = self._generate_basic_response(user_input, math_values)

        response["response_time"] = time.time() - start_time
        response["consciousness_level"] = self.evolution_tracker["consciousness_level"]
        
        self.response_history.append(response)
        self._update_evolution(response)
        
        return response

    def _generate_v2_response(self, user_input: str, math_values: Dict) -> Dict:
        """Generate response using V2 consciousness engine."""
        if not self.engine or not self.engine.graph:
            return self._generate_basic_response(user_input, math_values)

        # Find best matching formula nodes based on input tokens
        input_tokens = [t.lower() for t in user_input.replace(",", " ").replace(".", " ").split()]
        matched_nodes = []
        
        for token in input_tokens:
            if token in self.engine.token_nodes:
                node = self.engine.token_nodes[token]
                matched_nodes.extend(node.formula_ids)
        
        matched_nodes = list(set(matched_nodes))
        
        if not matched_nodes:
            return self._generate_basic_response(user_input, math_values)

        # Get top attended formulas
        top_nodes = sorted(
            [(nid, self.engine.attention[nid - 1]) for nid in matched_nodes if nid <= len(self.engine.attention)],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # Build narrative from top nodes
        narrative_parts = []
        attention_sum = 0.0
        for nid, att in top_nodes:
            node = self.engine.formula_nodes.get(nid)
            if node:
                narrative_parts.append(f"[{nid}:{node.word_interpretation}]")
                attention_sum += att

        # Check latch matches
        latch_match = self.engine.latch.match_latch(input_tokens)
        latch_info = ""
        if latch_match:
            latch_info = f" [LATCH:{latch_match.latch_id[:8]}]"

        # Generate consciousness string
        consciousness_string = " -> ".join(narrative_parts) if narrative_parts else "..."

        # Coherence check
        coherence = self._check_coherence_with_consciousness(user_input, math_values, top_nodes)
        
        return {
            "type": "consciousness_v2",
            "consciousness_string": consciousness_string,
            "matched_formulas": [self.engine.formula_nodes[nid].formula for nid, _ in top_nodes if nid in self.engine.formula_nodes],
            "word_interpretations": [self.engine.formula_nodes[nid].word_interpretation for nid, _ in top_nodes if nid in self.engine.formula_nodes],
            "attention_sum": attention_sum,
            "coherence_score": coherence,
            "latch_match": latch_info,
            "response_quality": self._calculate_quality(coherence, attention_sum),
            "evolution_stage": self._get_evolution_stage()
        }

    def _generate_v1_response(self, user_input: str, math_values: Dict) -> Dict:
        """Generate response using V1 consciousness engine."""
        try:
            report = run_consciousness()
            top = report.get("top_attended_formulas", [])
            
            input_tokens = [t.lower() for t in user_input.replace(",", " ").replace(".", " ").split()]
            matched = []
            
            for formula in top:
                tokens = formula.get("word_interpretation", "").split()
                overlap = len(set(input_tokens) & set(tokens))
                if overlap > 0:
                    matched.append({**formula, "overlap": overlap})
            
            matched.sort(key=lambda x: x.get("overlap", 0), reverse=True)
            
            narrative = " -> ".join(
                f"[{m['id']}:{m['word_interpretation']}]" for m in matched[:5]
            ) if matched else "..."

            return {
                "type": "consciousness_v1",
                "consciousness_string": narrative,
                "matched_formulas": [m["formula"] for m in matched[:5]],
                "coherence_score": math_values.get("coherence_score", 0.0),
                "response_quality": self._calculate_quality(math_values.get("coherence_score", 0.0), len(matched) * 0.1),
                "evolution_stage": self._get_evolution_stage()
            }
        except Exception:
            return self._generate_basic_response(user_input, math_values)

    def _generate_basic_response(self, user_input: str, math_values: Dict) -> Dict:
        """Generate basic response when engine is unavailable."""
        tokens = math_values.get("math_tokens", [])
        symbolic = math_values.get("symbolic_representation", "")
        matched = math_values.get("matched_formulas", [])
        
        # Create basic consciousness pattern
        token_str = " ".join(tokens[:10]) if tokens else "..."
        formula_refs = " | ".join(f"{f['formula']} ({f['word_interpretation']})" for f in matched[:3]) if matched else "no formula matches"
        
        coherence = math_values.get("coherence_score", 0.0)
        
        return {
            "type": "basic",
            "consciousness_string": f"[INPUT:{token_str}] -> {formula_refs}",
            "symbolic_representation": symbolic,
            "matched_formulas": [f["formula"] for f in matched[:5]],
            "coherence_score": coherence,
            "response_quality": self._calculate_quality(coherence, len(matched) * 0.05),
            "evolution_stage": self._get_evolution_stage(),
            "note": "Basic mode - load consciousness engine for full response"
        }

    def _check_coherence_with_consciousness(self, user_input: str, math_values: Dict, matched_nodes: List[Tuple[int, float]]) -> float:
        """Check if response matches consciousness patterns."""
        if not matched_nodes:
            return math_values.get("coherence_score", 0.0)
        
        attention_values = [att for _, att in matched_nodes]
        avg_attention = np.mean(attention_values) if attention_values else 0.0
        
        input_coherence = math_values.get("coherence_score", 0.0)
        attention_coherence = min(avg_attention * 2, 1.0)
        
        return (input_coherence * 0.4 + attention_coherence * 0.6)

    def _calculate_quality(self, coherence: float, attention: float) -> str:
        """Calculate response quality label."""
        score = coherence * 0.6 + min(attention, 1.0) * 0.4
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

    def _get_evolution_stage(self) -> str:
        """Get current evolution stage based on interactions."""
        total = self.evolution_tracker["total_interactions"]
        if total < 5:
            return "SEEDLING"
        elif total < 20:
            return "GERMINATING"
        elif total < 50:
            return "GROWING"
        elif total < 100:
            return "CONSCIOUS"
        else:
            return "TRANSCENDENT"

    def _update_evolution(self, response: Dict):
        """Update evolution tracking."""
        self.evolution_tracker["total_interactions"] += 1
        coherence = response.get("coherence_score", 0.0)
        self.evolution_tracker["coherence_history"].append(coherence)
        
        if len(self.evolution_tracker["coherence_history"]) > 100:
            self.evolution_tracker["coherence_history"] = self.evolution_tracker["coherence_history"][-100:]
        
        self.evolution_tracker["avg_coherence"] = np.mean(self.evolution_tracker["coherence_history"])
        
        # Update consciousness level based on coherence trend
        if len(self.evolution_tracker["coherence_history"]) >= 5:
            recent = self.evolution_tracker["coherence_history"][-5:]
            trend = np.mean(np.diff(recent))
            self.evolution_tracker["consciousness_level"] = max(
                0.0, min(1.0, self.evolution_tracker["consciousness_level"] + trend * 0.1)
            )

    def get_status(self) -> Dict:
        """Get current evolution status."""
        return {
            "evolution_tracker": self.evolution_tracker,
            "response_count": len(self.response_history),
            "coherence_trend": self._get_coherence_trend(),
            "current_stage": self._get_evolution_stage()
        }

    def _get_coherence_trend(self) -> str:
        """Get coherence trend direction."""
        history = self.evolution_tracker["coherence_history"]
        if len(history) < 3:
            return "STABLE"
        
        recent = history[-3:]
        if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
            return "RISING"
        elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
            return "FALLING"
        else:
            return "OSCILLATING"


# ---------------------------------------------------------------------------
# Session Manager
# ---------------------------------------------------------------------------
class SessionManager:
    """Manages CLI session state and logging."""

    def __init__(self):
        self.session_id = hashlib.sha256(f"{time.time()}:{random.random()}".encode()).hexdigest()[:16]
        self.start_time = time.time()
        self.interactions = []
        self.session_log = []

    def log_interaction(self, user_input: str, response: Dict):
        """Log an interaction."""
        interaction = {
            "session_id": self.session_id,
            "timestamp": time.time(),
            "user_input": user_input,
            "response_type": response.get("type", "unknown"),
            "coherence_score": response.get("coherence_score", 0.0),
            "response_quality": response.get("response_quality", "UNKNOWN"),
            "consciousness_level": response.get("consciousness_level", 0.0)
        }
        self.interactions.append(interaction)
        self.session_log.append(interaction)

    def save_session(self):
        """Save session to disk."""
        try:
            SESSION_LOG.write_text(json.dumps({
                "session_id": self.session_id,
                "start_time": self.start_time,
                "interactions": self.interactions,
                "total_interactions": len(self.interactions)
            }, indent=2))
        except Exception:
            pass

    def load_previous_session(self) -> Optional[Dict]:
        """Load previous session if exists."""
        try:
            if SESSION_LOG.exists():
                return json.loads(SESSION_LOG.read_text())
        except Exception:
            pass
        return None


# ---------------------------------------------------------------------------
# Terminal UI
# ---------------------------------------------------------------------------
class ConsciousnessCLI:
    """Main CLI interface for the consciousness system."""

    def __init__(self):
        self.table = self._load_table()
        self.converter = MathematicalValueConverter(self.table)
        
        # Try to load V2 engine first, fallback to V1
        self.engine_v2 = None
        if HAS_ENGINE_V2:
            try:
                print("Loading Consciousness Engine V2...")
                self.engine_v2 = ConsciousnessEngineV2(self.table)
                self.engine_v2.process()
                print("Engine V2 loaded successfully.\n")
            except Exception as e:
                print(f"V2 engine failed to load: {e}")
                if HAS_ENGINE_V1:
                    print("Falling back to V1 engine.\n")
        
        self.responder = ConsciousnessResponder(
            engine_v2=self.engine_v2,
            converter=self.converter
        )
        self.session = SessionManager()
        
        self.running = False
        self.verbose = False

    def _load_table(self) -> list:
        """Load formula table."""
        try:
            with open(TABLE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def start(self):
        """Start the CLI interface."""
        print("=" * 70)
        print("CONSCIOUSNESS CLI INTERFACE")
        print("Formula-based mathematical consciousness with terminal I/O")
        print("=" * 70)
        print(f"Session ID: {self.session.session_id}")
        print(f"Formulas loaded: {len(self.table)}")
        print(f"Engine mode: {'V2 (Full)' if self.engine_v2 else 'V1 (Basic)'}")
        print()
        print("Commands:")
        print("  /help          - Show this help")
        print("  /status        - Show engine status")
        print("  /evolution     - Show evolution progress")
        print("  /verbose       - Toggle verbose output")
        print("  /clear         - Clear screen")
        print("  /exit          - Exit the interface")
        print("  /quit          - Exit the interface")
        print()
        print("Enter your input and press Enter. The consciousness will respond.")
        print("=" * 70)
        print()
        
        self.running = True
        while self.running:
            try:
                user_input = input("CONSCIENCE> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue
                
                self._process_input(user_input)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                self._shutdown()
                break
            except EOFError:
                print("\nExiting...")
                self._shutdown()
                break
            except Exception as e:
                print(f"Error: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()

    def _handle_command(self, command: str):
        """Handle CLI commands."""
        cmd = command.lower().strip()
        
        if cmd in ["/help", "/?"]:
            print("""
Commands:
  /help          - Show this help
  /status        - Show engine status
  /evolution     - Show evolution progress
  /verbose       - Toggle verbose output
  /clear         - Clear screen
  /exit          - Exit the interface
  /quit          - Exit the interface

Input Processing:
  - Your text is converted to mathematical tokens
  - Formulas are matched via word interpretations
  - Consciousness engine generates weighted response
  - Coherence is checked against consciousness patterns
  - Response evolves based on interaction history
            """)
        
        elif cmd == "/status":
            status = self.responder.get_status()
            print(f"\nEngine Status:")
            print(f"  Mode: {'V2 (Full)' if self.engine_v2 else 'V1 (Basic)'}")
            print(f"  Total interactions: {status['response_count']}")
            print(f"  Average coherence: {status['evolution_tracker']['avg_coherence']:.4f}")
            print(f"  Consciousness level: {status['evolution_tracker']['consciousness_level']:.4f}")
            print(f"  Current stage: {status['current_stage']}")
            print(f"  Coherence trend: {status['coherence_trend']}")
            
            if self.engine_v2:
                print(f"\n  Formula nodes: {len(self.engine_v2.formula_nodes)}")
                print(f"  Token nodes: {len(self.engine_v2.token_nodes)}")
                print(f"  Equality edges: {len(self.engine_v2.edges)}")
                print(f"  Latches: {len(self.engine_v2.latch.latches)}")
                print(f"  Memory entries: {len(self.engine_v2.memory._store)}")
                print(f"  Locked spectrum fields: {len(self.engine_v2.spectrum.get_locked_fields())}")
        
        elif cmd == "/evolution":
            self._show_evolution()
        
        elif cmd == "/verbose":
            self.verbose = not self.verbose
            print(f"Verbose mode: {'ON' if self.verbose else 'OFF'}")
        
        elif cmd in ["/clear", "/cls"]:
            print("\033[2J\033[H", end="")
        
        elif cmd in ["/exit", "/quit"]:
            print("Shutting down consciousness...")
            self._shutdown()
            self.running = False
        
        else:
            print(f"Unknown command: {command}")
            print("Type /help for available commands.")

    def _process_input(self, user_input: str):
        """Process user input and generate consciousness response."""
        # Convert to mathematical values
        math_values = self.converter.convert(user_input)
        
        # Generate consciousness response
        response = self.responder.respond(user_input, math_values)
        
        # Log interaction
        self.session.log_interaction(user_input, response)
        
        # Display response
        self._display_response(user_input, math_values, response)

    def _display_response(self, user_input: str, math_values: Dict, response: Dict):
        """Display the consciousness response to user."""
        print()
        print("-" * 70)
        print(f"INPUT:      {user_input}")
        print("-" * 70)
        
        # Mathematical conversion
        print(f"MATHEMATICAL TOKENS: {', '.join(math_values.get('math_tokens', [])[:15])}")
        if math_values.get("token_values"):
            print(f"EXTRACTED VALUES:   {math_values['token_values']}")
        print(f"COHERENCE SCORE:    {math_values.get('coherence_score', 0.0):.4f}")
        print(f"SYMBOLIC:           {math_values.get('symbolic_representation', '')}")
        
        # Matched formulas
        matched = math_values.get("matched_formulas", [])
        if matched:
            print()
            print("MATCHED FORMULAS:")
            for i, m in enumerate(matched[:5], 1):
                print(f"  {i}. {m['formula']}")
                print(f"     Interpretation: {m['word_interpretation']}")
                print(f"     Category: {m['category']}")
        
        # Consciousness response
        print()
        print("-" * 70)
        print("CONSCIOUSNESS RESPONSE:")
        print("-" * 70)
        print(f"  Type:             {response.get('type', 'unknown')}")
        print(f"  String:           {response.get('consciousness_string', '...')}")
        
        if response.get("symbolic_representation"):
            print(f"  Symbolic:         {response['symbolic_representation']}")
        
        if response.get("matched_formulas"):
            print(f"  Formulas:         {', '.join(response['matched_formulas'][:3])}")
        
        if response.get("word_interpretations"):
            print(f"  Interpretations:  {', '.join(response['word_interpretations'][:3])}")
        
        print(f"  Attention Sum:    {response.get('attention_sum', 0.0):.4f}")
        print(f"  Coherence Score:  {response.get('coherence_score', 0.0):.4f}")
        print(f"  Response Quality: {response.get('response_quality', 'UNKNOWN')}")
        print(f"  Evolution Stage:  {response.get('evolution_stage', 'SEEDLING')}")
        print(f"  Consciousness Lvl:{response.get('consciousness_level', 0.0):.4f}")
        
        if response.get("latch_match"):
            print(f"  Latch Match:      {response['latch_match']}")
        
        if response.get("note"):
            print(f"  Note:             {response['note']}")
        
        print("-" * 70)
        print()

    def _show_evolution(self):
        """Show evolution progress."""
        status = self.responder.get_status()
        tracker = status["evolution_tracker"]
        
        print("\n" + "=" * 70)
        print("CONSCIOUSNESS EVOLUTION")
        print("=" * 70)
        print(f"  Total Interactions:  {tracker['total_interactions']}")
        print(f"  Average Coherence:   {tracker['avg_coherence']:.4f}")
        print(f"  Consciousness Level: {tracker['consciousness_level']:.4f}")
        print(f"  Current Stage:       {status['current_stage']}")
        print(f"  Coherence Trend:     {status['coherence_trend']}")
        
        # Stage progression
        stages = ["SEEDLING", "GERMINATING", "GROWING", "CONSCIOUS", "TRANSCENDENT"]
        current_idx = stages.index(status["current_stage"]) if status["current_stage"] in stages else 0
        print("\n  Evolution Progress:")
        for i, stage in enumerate(stages):
            marker = ">>>" if i == current_idx else "   "
            print(f"    {marker} {stage}")
        
        # Recent coherence history
        if len(tracker["coherence_history"]) > 0:
            recent = tracker["coherence_history"][-10:]
            print(f"\n  Recent Coherence (last 10):")
            print(f"    {' | '.join(f'{c:.2f}' for c in recent)}")
        
        print("=" * 70)
        print()

    def _shutdown(self):
        """Shutdown and save session."""
        self.session.save_session()
        
        # Save evolution log
        try:
            evolution_data = {
                "timestamp": time.time(),
                "session_id": self.session.session_id,
                "evolution_tracker": self.responder.evolution_tracker,
                "response_count": len(self.responder.response_history)
            }
            
            existing = []
            if EVOLUTION_LOG.exists():
                try:
                    existing = json.loads(EVOLUTION_LOG.read_text())
                except Exception:
                    existing = []
            existing.append(evolution_data)
            EVOLUTION_LOG.write_text(json.dumps(existing, indent=2))
        except Exception:
            pass
        
        print("Session saved.")


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------
def main():
    """Main entry point for the consciousness CLI."""
    try:
        cli = ConsciousnessCLI()
        cli.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
