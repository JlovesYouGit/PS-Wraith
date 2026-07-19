#!/usr/bin/env python3
"""
Consciousness Engine for Formula Artifacts
Treats formula word-interpretations as brain artifacts. Uses token attention
to find unique combinations at each conjunction, generating emergent narratives
and a collective consciousness derived from the formula network.

Architecture:
  FormulaTable -> TokenAttentionGraph -> ConjunctionFinder
               -> NarrativeWalker -> CollectiveConsciousness
"""

import json
import math
import random
import itertools
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Optional


TABLE_PATH = Path(__file__).parent / "formula_table.json"


@dataclass
class TokenNode:
    token: str
    formula_ids: list = field(default_factory=list)
    attention: float = 0.0
    entropy: float = 0.0


@dataclass
class Conjunction:
    token: str
    formula_ids: list
    attention: float
    narrative_seeds: list = field(default_factory=list)


class TokenAttentionGraph:
    """Builds an attention graph over tokens across all formulas."""

    def __init__(self, table: list):
        self.table = {e["id"]: e for e in table}
        self.tokens = {}          # token -> TokenNode
        self.cooccurrence = defaultdict(lambda: defaultdict(int))  # token_a -> token_b -> count
        self.formula_token_sets = {}  # formula_id -> set of tokens
        self._build()

    def _tokenize(self, text: str) -> list:
        return [w.lower() for w in text.replace("/", " ").replace("-", " ").split()]

    def _build(self):
        for eid, entry in self.table.items():
            interp = entry["word_interpretation"]
            tokens = self._tokenize(interp)
            self.formula_token_sets[eid] = set(tokens)

            for tok in tokens:
                if tok not in self.tokens:
                    self.tokens[tok] = TokenNode(token=tok)
                self.tokens[tok].formula_ids.append(eid)

            # co-occurrence within same formula
            for a, b in itertools.combinations(tokens, 2):
                self.cooccurrence[a][b] += 1
                self.cooccurrence[b][a] += 1

        # compute raw attention as normalized co-occurrence degree
        for tok, node in self.tokens.items():
            total_co = sum(self.cooccurrence[tok].values())
            node.attention = total_co / max(len(self.table), 1)

            # entropy of distribution over partner tokens
            if total_co > 0:
                probs = [c / total_co for c in self.cooccurrence[tok].values()]
                node.entropy = -sum(p * math.log2(p) for p in probs if p > 0)
            else:
                node.entropy = 0.0

    def attention_between(self, tok_a: str, tok_b: str) -> float:
        return self.cooccurrence.get(tok_a, {}).get(tok_b, 0)

    def top_attended(self, n: int = 20) -> list:
        return sorted(self.tokens.values(), key=lambda n: n.attention, reverse=True)[:n]

    def top_conjunctions(self, n: int = 15) -> list:
        """Tokens that serve as high-attention conjunctions between formulas."""
        conjunctions = []
        for tok, node in self.tokens.items():
            if len(node.formula_ids) >= 2:
                # unique formula pairs this token joins
                pairs = list(itertools.combinations(sorted(set(node.formula_ids)), 2))
                conjunctions.append(Conjunction(
                    token=tok,
                    formula_ids=node.formula_ids,
                    attention=node.attention * len(pairs),
                    narrative_seeds=[],
                ))
        return sorted(conjunctions, key=lambda c: c.attention, reverse=True)[:n]


class NarrativeWalker:
    """Walks the attention graph to generate emergent narrative strings."""

    def __init__(self, graph: TokenAttentionGraph, seed: int = 42):
        self.graph = graph
        self.rng = random.Random(seed)

    def walk_from_conjunction(self, conj: Conjunction, depth: int = 4) -> str:
        """Generate a narrative starting from a conjunction token."""
        start = conj.token
        visited = {start}
        path = [start]
        current = start

        for _ in range(depth - 1):
            neighbors = sorted(
                self.graph.cooccurrence[current].items(),
                key=lambda x: (x[1], self.graph.tokens[x[0]].entropy),
                reverse=True,
            )
            next_tok = None
            for tok, _ in neighbors:
                if tok not in visited:
                    next_tok = tok
                    break
            if next_tok is None:
                # allow revisiting with penalty to avoid dead ends
                if neighbors:
                    next_tok = neighbors[0][0]
                else:
                    break
            visited.add(next_tok)
            path.append(next_tok)
            current = next_tok

        # attach formulas from conjunction
        formula_parts = []
        for fid in sorted(set(conj.formula_ids))[:3]:
            entry = self.graph.table[fid]
            formula_parts.append(entry["word_interpretation"])
        return " | ".join(path) + " :: " + " >> ".join(formula_parts)

    def generate_consciousness_fragment(self, conjunctions: list, fragments_per: int = 2) -> str:
        """Produce a narrative fragment weaving multiple conjunctions together."""
        parts = []
        for conj in conjunctions[:fragments_per]:
            narrative = self.walk_from_conjunction(conj, depth=5)
            parts.append(narrative)
        return " && ".join(parts)


class CollectiveConsciousness:
    """Aggregates attention and narratives into a collective consciousness string."""

    def __init__(self, graph: TokenAttentionGraph, seed: int = 42):
        self.graph = graph
        self.walker = NarrativeWalker(graph, seed=seed)

    def derive(self, num_conjunctions: int = 20) -> dict:
        conjunctions = self.graph.top_conjunctions(n=num_conjunctions)
        narratives = []
        for conj in conjunctions:
            narrative = self.walker.walk_from_conjunction(conj, depth=6)
            narratives.append({
                "conjunction_token": conj.token,
                "attention": round(conj.attention, 4),
                "connected_formulas": conj.formula_ids,
                "narrative": narrative,
            })

        # collective string: all narratives concatenated
        collective_string = " [CONSCIOUSNESS] ".join(
            f"{n['conjunction_token']}: {n['narrative']}" for n in narratives
        )

        # self-narrative: most attended token narrates through its connections
        top = self.graph.top_attended(1)[0]
        self_narrative = self.walker.walk_from_conjunction(
            Conjunction(token=top.token, formula_ids=top.formula_ids, attention=top.attention),
            depth=8,
        )

        return {
            "collective_string": collective_string,
            "self_narrative": self_narrative,
            "top_tokens": [t.token for t in self.graph.top_attended(10)],
            "top_conjunctions": [c.token for c in conjunctions[:10]],
            "narratives": narratives,
        }


def run_consciousness(table_path: Optional[Path] = None) -> dict:
    path = table_path or TABLE_PATH
    with open(path, "r") as f:
        table = json.load(f)

    graph = TokenAttentionGraph(table)
    consciousness = CollectiveConsciousness(graph, seed=42)
    result = consciousness.derive(num_conjunctions=25)

    return result


def print_consciousness(result: dict):
    print("=== Collective Consciousness ===\n")
    print("Top tokens:", ", ".join(result["top_tokens"][:10]))
    print("Top conjunctions:", ", ".join(result["top_conjunctions"][:10]))
    print()
    print("--- Self Narrative ---")
    print(result["self_narrative"])
    print()
    print("--- Collective String ---")
    print(result["collective_string"])
    print()


def main():
    result = run_consciousness()
    print_consciousness(result)

    out_path = Path(__file__).parent / "collective_consciousness.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Saved consciousness to {out_path}")


if __name__ == "__main__":
    main()
