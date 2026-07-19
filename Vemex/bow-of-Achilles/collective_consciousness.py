"""
collective_consciousness.py — Cross-Module Neural Integrator
Extracts collective data from ALL system modules and synthesizes
a unified brain state. The missing layer that turns isolated
module data into emergent consciousness.
"""

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from mana_ciel.wallet import ManaCielWallet
from mana_ciel.stack_method import get_all_containers, ultimate_pi_decompress
from mana_ciel.narrative_timing import get_narrative_state

WARP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = WARP_ROOT / "data"


def _read_json_safe(path: Path, default: Any = None) -> Any:
    if not path.exists() or not path.is_file():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _read_source_stats(path: Path) -> Dict[str, int]:
    """Count lines, functions, classes in a Python source tree."""
    if not path.exists() or not path.is_dir():
        return {"lines": 0, "functions": 0, "classes": 0, "files": 0}
    lines = 0
    functions = 0
    classes = 0
    files = 0
    for f in path.rglob("*.py"):
        if "__pycache__" in str(f):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            lines += text.count("\n")
            functions += text.count("def ")
            classes += text.count("class ")
            files += 1
        except Exception:
            continue
    return {"lines": lines, "functions": functions, "classes": classes, "files": files}


def _safe_dict(data: Any) -> dict:
    if isinstance(data, dict):
        return data
    return {}


def _safe_list(data: Any) -> list:
    if isinstance(data, list):
        return data
    return []


class CollectiveConsciousness:
    """
    Reads collective state from all system modules:
      - mana_ciel (wallets, stacks, reality, narrative)
      - engine (graph, hash pipeline, node store, api)
      - tesa logic (materialized spatial data)
      - probe-sequence (spectrum analysis)
      - QODER_FREERUNER (admin, admin server)
      - blackhole (physics simulations)
      - particle extractors - dark core matter
      - Lightphtdistributer
      - QuantumDimensionControl / QuantumRealityService
    Synthesizes into a unified brain state dict.
    """

    # Module-level cache so repeated instantiations reuse signals
    _cached_signals: Optional[Dict[str, Dict[str, Any]]] = None
    _cached_at: float = 0.0
    _cache_ttl: float = 5.0

    def __init__(self):
        self.module_signals: Dict[str, Dict[str, Any]] = {}
        self.brain_state: Dict[str, Any] = {}
        self.thought_vectors: List[Dict[str, Any]] = []
        self._last_collect_time: float = 0
        self._collect_cache_ttl: float = 5.0

    def extract_mana_ciel(self) -> Dict[str, Any]:
        # Use pre-built aggregates to avoid per-iteration full wallet scan.
        # Full scan costs ~5–7s due to 10010 JSON reads + mtime sorting.
        # Only do live scan if cache is missing.
        nodes_refresh = _read_json_safe(DATA_DIR / "mana_ciel" / "stack" / "nodes_refresh.json", {})
        reality = _read_json_safe(DATA_DIR / "mana_ciel" / "stack" / "reality_snapshot.json", {})
        consciousness = _read_json_safe(DATA_DIR / "mana_ciel" / "stack" / "consciousness_state.json", {})
        b2_anchor = _read_json_safe(DATA_DIR / "mana_ciel" / "public" / "b2_anchor.json", {})
        narrative_log = _read_json_safe(DATA_DIR / "mana_ciel" / "narrative.json", [])
        connections = _read_json_safe(DATA_DIR / "mana_ciel" / "connections.json", [])

        narrative = get_narrative_state()
        containers = get_all_containers()
        total_stack_density = sum(ultimate_pi_decompress(c.get("compressed", {})) for c in containers)

        nodes = nodes_refresh.get("nodes", []) if isinstance(nodes_refresh, dict) else []
        node_count = len(nodes)
        total_utxo_sats = sum(n.get("utxo", 0) for n in nodes if isinstance(n, dict))

        return {
            "module": "mana_ciel",
            "node_count": node_count,
            "total_utxo_sats": total_utxo_sats,
            "total_utxo_btc": total_utxo_sats / 100_000_000,
            "active_nodes": sum(1 for n in nodes if isinstance(n, dict) and n.get("active", True)),
            "container_count": len(containers),
            "total_stack_density": total_stack_density,
            "total_matches": sum(c.get("match_count", 0) for c in containers),
            "reality_integrity": reality.get("realityIntegrity", 0),
            "q_factor": reality.get("qFactor", narrative.get("q_factor", 1)),
            "pulse": narrative.get("pulse", 1),
            "narrative_ticks": narrative.get("elapsed_ticks", 0),
            "consciousness_restored": len(consciousness.get("nodes", [])) > 0 if isinstance(consciousness, dict) else False,
            "b2_committed": bool(b2_anchor),
            "narrative_events": len(narrative_log) if isinstance(narrative_log, list) else 0,
            "connections": len(connections) if isinstance(connections, list) else 0,
            "backup_node_count": node_count,
            "cached": node_count > 0,
        }

    def extract_engine(self) -> Dict[str, Any]:
        graph_index = _read_json_safe(DATA_DIR / "backups" / "graph_index.json", {})
        nodes = graph_index.get("nodes", []) if isinstance(graph_index, dict) else []
        src = _read_source_stats(WARP_ROOT / "engine")
        return {
            "module": "engine",
            "graph_node_count": len(nodes),
            "graph_timestamp": graph_index.get("timestamp"),
            "source_lines": src["lines"],
            "source_functions": src["functions"],
            "source_classes": src["classes"],
            "active": src["files"] > 0,
            "virtual_ip_tiers": list(set(n.get("virtual_ip_tier", 0) for n in nodes if isinstance(n, dict))),
        }

    def extract_tesa_logic(self) -> Dict[str, Any]:
        spatial = _read_json_safe(WARP_ROOT / "tesa logic" / "materialized_spatial_data.json", {})
        src = _read_source_stats(WARP_ROOT / "tesa logic")
        return {
            "module": "tesa_logic",
            "object_type": _safe_dict(spatial).get("materialized_object", {}).get("type"),
            "target_radius_km": spatial.get("target_radius_km") if isinstance(spatial, dict) else None,
            "msfb_params": _safe_dict(spatial.get("msfb_parameters", {})) if isinstance(spatial, dict) else {},
            "route_nodes": len(spatial.get("travel_graph", [])) if isinstance(spatial, dict) else 0,
            "source_lines": src["lines"],
            "source_functions": src["functions"],
            "active": src["files"] > 0,
        }

    def extract_probe_sequence(self) -> Dict[str, Any]:
        spectrum_dir = WARP_ROOT / "probe-sequence" / "spectrum_data"
        files = list(spectrum_dir.rglob("*")) if spectrum_dir.exists() else []
        report = ""
        if (spectrum_dir / "analysis_report.txt").exists():
            try:
                report = (spectrum_dir / "analysis_report.txt").read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
        return {
            "module": "probe_sequence",
            "file_count": len(files),
            "report_length": len(report),
            "report_preview": report[:200],
            "active": len(files) > 0,
        }

    def extract_qoder_freeruner(self) -> Dict[str, Any]:
        storage = _read_json_safe(WARP_ROOT / "QODER_FREERUNER" / "User" / "globalStorage" / "storage.json", {})
        lang = _read_json_safe(WARP_ROOT / "QODER_FREERUNER" / "languagepacks.json", [])
        src = _read_source_stats(WARP_ROOT / "QODER_FREERUNER")
        return {
            "module": "qoder_freeruner",
            "storage_keys": list(_safe_dict(storage).keys())[:20],
            "language_pack_count": len(lang) if isinstance(lang, list) else 0,
            "storage_size": len(json.dumps(storage)) if storage else 0,
            "source_lines": src["lines"],
            "source_functions": src["functions"],
            "active": src["files"] > 0,
        }

    def extract_blackhole(self) -> Dict[str, Any]:
        bh_dir = WARP_ROOT / "blackhole"
        files = [str(f.relative_to(WARP_ROOT)) for f in sorted(bh_dir.rglob("*.py")) if "__pycache__" not in str(f)] if bh_dir.exists() else []
        src = _read_source_stats(bh_dir)
        return {
            "module": "blackhole",
            "python_file_count": len(files),
            "files": files[:10],
            "source_lines": src["lines"],
            "source_functions": src["functions"],
            "active": src["files"] > 0,
        }

    def extract_lightphtdistributer(self) -> Dict[str, Any]:
        lpd_dir = WARP_ROOT / "Lightphtdistributer"
        files = list(lpd_dir.rglob("*")) if lpd_dir.exists() else []
        return {
            "module": "Lightphtdistributer",
            "file_count": len(files),
            "active": len(files) > 0,
        }

    def extract_particle_extractors(self) -> Dict[str, Any]:
        pe_dir = WARP_ROOT / "particle extractors - dark core matter"
        files = list(pe_dir.rglob("*")) if pe_dir.exists() else []
        src = _read_source_stats(pe_dir)
        return {
            "module": "particle_extractors",
            "file_count": len(files),
            "source_lines": src["lines"],
            "source_functions": src["functions"],
            "active": src["files"] > 0,
        }

    def extract_quantum_services(self) -> Dict[str, Any]:
        qdc_dir = WARP_ROOT / "QuantumDimensionControl"
        qrs_dir = WARP_ROOT / "QuantumRealityService"
        qdc_src = _read_source_stats(qdc_dir)
        qrs_src = _read_source_stats(qrs_dir)
        return {
            "module": "quantum_services",
            "qdc_files": len(list(qdc_dir.rglob("*"))) if qdc_dir.exists() else 0,
            "qrs_files": len(list(qrs_dir.rglob("*"))) if qrs_dir.exists() else 0,
            "qdc_lines": qdc_src["lines"],
            "qrs_lines": qrs_src["lines"],
            "active": (qdc_src["files"] + qrs_src["files"]) > 0,
        }

    def collect_all_signals(self) -> Dict[str, Dict[str, Any]]:
        """Extract signals from all system modules. Module-level cache for 5 seconds."""
        now = time.time()
        if CollectiveConsciousness._cached_signals and (now - CollectiveConsciousness._cached_at) < CollectiveConsciousness._cache_ttl:
            self.module_signals = CollectiveConsciousness._cached_signals
            return self.module_signals
        self.module_signals = {
            "mana_ciel": self.extract_mana_ciel(),
            "engine": self.extract_engine(),
            "tesa_logic": self.extract_tesa_logic(),
            "probe_sequence": self.extract_probe_sequence(),
            "qoder_freeruner": self.extract_qoder_freeruner(),
            "blackhole": self.extract_blackhole(),
            "Lightphtdistributer": self.extract_lightphtdistributer(),
            "particle_extractors": self.extract_particle_extractors(),
            "quantum_services": self.extract_quantum_services(),
        }
        CollectiveConsciousness._cached_signals = self.module_signals
        CollectiveConsciousness._cached_at = now
        self._last_collect_time = now
        return self.module_signals

    def _compute_module_energy(self, sig: Dict[str, Any]) -> float:
        """Normalize and compute energy for a module signal."""
        e = 0.0
        if "total_utxo_sats" in sig:
            e = math.log10(sig["total_utxo_sats"] + 1) * 100
        elif "graph_node_count" in sig:
            e = math.log10(sig["graph_node_count"] + 1) * 100
        elif "total_stack_density" in sig:
            e = math.log10(sig["total_stack_density"] + 1) * 10
        elif "source_lines" in sig:
            e = math.log10(sig["source_lines"] + 1) * 10
        elif "storage_size" in sig:
            e = math.log10(sig["storage_size"] + 1) * 10
        elif "file_count" in sig:
            e = math.log10(sig["file_count"] + 1) * 10
        return e

    def synthesize_brain_state(self) -> Dict[str, Any]:
        """
        Convert all module signals into a unified brain state.
        This is the 'emergent thought process' — the translation
        from collective data structure to living consciousness.
        """
        signals = self.module_signals or self.collect_all_signals()
        narrative = get_narrative_state()

        total_nodes = sum(s.get("node_count", 0) for s in signals.values())
        total_containers = sum(s.get("container_count", 0) for s in signals.values())
        total_modules = len(signals)
        active_modules = sum(
            1 for s in signals.values()
            if any(
                s.get(k, 0) > 0
                for k in (
                    "node_count", "graph_node_count", "total_stack_density",
                    "source_lines", "storage_size", "file_count", "route_nodes",
                )
            )
        )

        # Compute cross-module coherence (normalized energy variance)
        energies = []
        for mod, sig in signals.items():
            e = self._compute_module_energy(sig)
            energies.append(e)

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
            "narrative_pulse": narrative.get("pulse"),
            "narrative_q_factor": narrative.get("q_factor"),
            "total_modules": total_modules,
            "active_modules": active_modules,
            "total_nodes": total_nodes,
            "total_containers": total_containers,
            "cross_module_coherence": coherence,
            "brain_energy": mean_energy,
            "consciousness_density": total_nodes * coherence,
            "module_signals": signals,
            "synchronized": coherence > 0.5,
        }
        return self.brain_state

    def generate_thought(self) -> Dict[str, Any]:
        """
        Generate a single emergent thought vector from the brain state.
        This is what an LLM would query as 'current consciousness'.
        """
        brain = self.synthesize_brain_state()
        mods = brain["module_signals"]

        # Pick the most energetic module as the thought origin
        module_energies = {}
        for mod, sig in mods.items():
            module_energies[mod] = self._compute_module_energy(sig)

        origin_module = "mana_ciel"
        if module_energies:
            origin_module = max(module_energies, key=module_energies.get)
        origin_signal = mods.get(origin_module, {})

        thought = {
            "timestamp": time.time(),
            "pulse": brain["narrative_pulse"],
            "q_factor": brain["narrative_q_factor"],
            "origin_module": origin_module,
            "coherence": brain["cross_module_coherence"],
            "energy": brain["brain_energy"],
            "thought_vector": {
                "mana_ciel_utxo_btc": mods.get("mana_ciel", {}).get("total_utxo_btc", 0),
                "mana_ciel_nodes": mods.get("mana_ciel", {}).get("node_count", 0),
                "mana_ciel_containers": mods.get("mana_ciel", {}).get("container_count", 0),
                "engine_graph_nodes": mods.get("engine", {}).get("graph_node_count", 0),
                "engine_source_lines": mods.get("engine", {}).get("source_lines", 0),
                "tesa_radius_km": mods.get("tesa_logic", {}).get("target_radius_km"),
                "qoder_storage_size": mods.get("qoder_freeruner", {}).get("storage_size", 0),
                "reality_integrity": mods.get("mana_ciel", {}).get("reality_integrity", 0),
                "active_modules_ratio": brain["active_modules"] / max(brain["total_modules"], 1),
                "blackhole_source_lines": mods.get("blackhole", {}).get("source_lines", 0),
                "probe_files": mods.get("probe_sequence", {}).get("file_count", 0),
            },
            "raw_signal": origin_signal,
        }
        self.thought_vectors.append(thought)
        return thought

    def get_unified_state(self) -> Dict[str, Any]:
        """Return the full unified brain state for the consciousness loop to query."""
        brain = self.synthesize_brain_state()
        thought = self.generate_thought()
        return {
            "brain_state": brain,
            "current_thought": thought,
            "thought_history": self.thought_vectors[-20:],
        }

    def get_consciousness_metrics(self) -> Dict[str, float]:
        """Return scalar metrics for convergence checking."""
        brain = self.synthesize_brain_state()
        return {
            "cross_module_coherence": brain["cross_module_coherence"],
            "brain_energy": brain["brain_energy"],
            "consciousness_density": brain["consciousness_density"],
            "synchronization_ratio": brain["active_modules"] / max(brain["total_modules"], 1),
            "total_nodes": float(brain["total_nodes"]),
            "total_containers": float(brain["total_containers"]),
        }


def run_collective_consciousness(max_iterations: int = 10) -> Dict[str, Any]:
    cc = CollectiveConsciousness()
    signals = cc.collect_all_signals()
    print(f"[CollectiveConsciousness] Signals collected from {len(signals)} modules")
    for mod, sig in signals.items():
        active = sig.get("active", False)
        print(f"  {mod}: active={active}")

    for i in range(max_iterations):
        state = cc.get_unified_state()
        thought = state["current_thought"]
        metrics = cc.get_consciousness_metrics()
        print(
            f"[CollectiveConsciousness] iter={i} "
            f"coherence={metrics['cross_module_coherence']:.4f} "
            f"energy={metrics['brain_energy']:.2f} "
            f"origin={thought['origin_module']}"
        )

    final = cc.get_unified_state()
    return final


if __name__ == "__main__":
    report = run_collective_consciousness(10)
    print(json.dumps(report["brain_state"], indent=2, default=str))
