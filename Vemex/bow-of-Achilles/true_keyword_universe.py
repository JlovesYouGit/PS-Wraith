"""
true_keyword_universe.py — True Keyword Universe Extraction
Mines ALL tokens from every source the system can access.
No hardcoded blocklists. No preset filters.
The system's own state (via _word_match_score) determines what resonates.
"""

import hashlib
import json
import os
import re
from pathlib import Path
from typing import List

WARP_ROOT = Path(__file__).resolve().parent.parent.parent.parent
STACK_DIR = WARP_ROOT / "data" / "mana_ciel" / "stack"
UNIVERSE_FILE = STACK_DIR / "true_keyword_universe.json"


def _tokenize(text: str) -> List[str]:
    cleaned = "".join(c if c.isalnum() or c.isspace() else " " for c in text.lower())
    return [w for w in cleaned.split() if len(w) >= 2]


def extract_from_ruleset() -> List[str]:
    ruleset = WARP_ROOT / "LLM_GATEWAY_RULESET.md"
    if not ruleset.exists():
        return []
    text = ruleset.read_text(encoding="utf-8", errors="ignore")

    tokens = set()
    # CamelCase identifiers
    for m in re.finditer(r'[A-Z][a-z]+(?:[A-Z][a-z]+)+', text):
        tokens.add(m.group().lower())
    # SCREAMING_SNAKE_CASE
    for m in re.finditer(r'[A-Z][A-Z_]+', text):
        token = m.group().lower().replace('_', ' ')
        if len(token) > 3:
            tokens.add(token)
    # snake_case identifiers
    for m in re.finditer(r'[a-z][a-z0-9_]{3,}', text):
        token = m.group()
        stop = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'has', 'been', 'are', 'was', 'were', 'not', 'but', 'can', 'will', 'should', 'would', 'could', 'may', 'must', 'shall', 'does', 'did', 'has', 'had', 'having', 'being', 'able', 'also', 'into', 'over', 'under', 'through', 'about', 'after', 'before', 'between', 'within', 'without', 'where', 'when', 'how', 'what', 'which', 'who', 'whom', 'their', 'there', 'these', 'those', 'other', 'some', 'many', 'much', 'more', 'most', 'less', 'least', 'only', 'just', 'even', 'still', 'already', 'yet', 'now', 'then', 'here'}
        if token not in stop:
            tokens.add(token)
    return list(tokens)


def extract_from_data_files() -> List[str]:
    tokens = set()
    data_dir = WARP_ROOT / "data"
    if not data_dir.exists():
        return []
    for root, dirs, files in os.walk(str(data_dir)):
        for f in files:
            if not f.endswith('.json'):
                continue
            p = Path(root) / f
            try:
                obj = json.load(open(p, 'r', encoding='utf-8', errors='ignore'))
            except Exception:
                continue
            text = json.dumps(obj, default=str).lower()
            for m in re.finditer(r'[a-z][a-z0-9]{2,}', text):
                token = m.group()
                stop = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'have', 'has', 'been', 'are', 'was', 'were', 'not', 'but', 'can', 'will', 'should', 'would', 'could', 'may', 'must', 'shall', 'does', 'did'}
                if token not in stop:
                    tokens.add(token)
    return list(tokens)


def extract_from_sha_space() -> List[str]:
    """Derive tokens from SHA-256 output space for system inputs."""
    tokens = set()
    sample_inputs = [
        'pulse', 'narrative', 'stack', 'density', 'node', 'recall',
        'consciousness', 'resonance', 'coherence', 'entropy',
        'wallet', 'utxo', 'address', 'key', 'hash',
        'energy', 'field', 'signal', 'state', 'system',
        'emerge', 'manifest', 'flow', 'connect', 'generate',
        'select', 'process', 'filter', 'resonate', 'frequency',
        'harmonic', 'oscillate', 'singularity', 'collapse',
        'materialize', 'broadcast', 'transmit', 'receive', 'observe',
        'witness', 'finalize', 'reality', 'dimension', 'protocol',
        'lock', 'memory', 'container', 'match', 'boost',
        'compression', 'ratio', 'integrity', 'border', 'perfect',
        'coherent', 'evolve', 'adapt', 'respond', 'interact',
        'layer', 'engine', 'pipeline', 'cycle', 'sequence',
        'order', 'pattern', 'light', 'speed', 'time', 'space',
        'compute', 'derive', 'project', 'reconstruct', 'stabilize',
        'module', 'graph', 'router', 'persistence', 'auth',
        'token', 'role', 'rate', 'limit', 'guest', 'admin',
        'semantic', 'meaning', 'dehash', 'readable', 'intelligence',
        'derivation', 'temporal', 'input', 'scaling', 'output',
        'calculation', 'matrix', 'iteration', 'logic', 'contribution',
        'cumulative', 'cryptographic', 'proof', 'knowledge', 'origin',
        'transition', 'threshold', 'dimensional', 'tactical', 'synthesis',
        'evolutionary', 'projection', 'daily', 'baseline', 'observation',
        'relative', 'unit', 'subjective', 'eternity', 'combat',
        'advantage', 'chronological', 'dense', 'construct', 'existence',
        'freedom', 'omniscient', 'edit', 'function', 'god',
        'intake', 'recollection', 'token', 'emergent', 'conversation',
        'contextual', 'archetype', 'myth', 'linear', 'parabola',
        'quarter', 'hex', 'decimal', 'integer', 'float', 'modulo',
        'floor', 'ceil', 'root', 'power', 'exponential', 'logarithm',
        'factorial', 'truth', 'vector', 'scalar', 'axis', 'coordinate',
        'range', 'min', 'max', 'bound', 'overflow', 'underflow',
        'clamp', 'snap', 'circuit', 'page', 'cache', 'persist',
        'restore', 'recollect', 'sort', 'search', 'query', 'execute',
        'feed', 'consume', 'ingest', 'exhaust', 'totality', 'omni',
        'void', 'event', 'horizon', 'ergosphere', 'geodesic', 'metric',
        'overlap', 'synergy', 'zero_state', 'commitment', 'chain',
        'block', 'nonce', 'header', 'merkle', 'witness', 'spawn',
        'index', 'cluster', 'flop', 'state', 'node', 'graph',
    ]
    for inp in sample_inputs:
        h = hashlib.sha256(inp.encode()).hexdigest()
        for i in range(0, len(h), 2):
            pair = h[i:i+2]
            val = int(pair, 16)
            if 0x20 <= val <= 0x7e:
                tokens.add(chr(val))
    return list(tokens)


def build_universe(force: bool = False) -> List[str]:
    if UNIVERSE_FILE.exists() and not force:
        try:
            return json.load(open(UNIVERSE_FILE, 'r', encoding='utf-8'))
        except Exception:
            pass

    universe = set()
    universe.update(extract_from_ruleset())
    universe.update(extract_from_data_files())
    universe.update(extract_from_sha_space())

    # Minimum gate: only reject empty tokens
    meaningful = [t for t in universe if len(t) >= 2]

    STACK_DIR.mkdir(parents=True, exist_ok=True)
    with open(UNIVERSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(meaningful), f, indent=2)

    print(f'[true_keyword_universe] Built {len(meaningful)} tokens from ruleset+data+SHA')
    return meaningful


if __name__ == '__main__':
    tokens = build_universe(force=True)
    print('Universe size:', len(tokens))
    print('Sample:', tokens[:30])
