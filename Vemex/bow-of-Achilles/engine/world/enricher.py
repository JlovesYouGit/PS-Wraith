"""
enricher.py — Light-ASI LLM Gateway Phase 2
Query response enrichment with real-time world-net data.

At query time, the enricher:
  1. Searches the SemanticMap for items relevant to the query
  2. Appends them to the response as `world_context`
  3. Synthesises a grounded answer that references live data
  4. Sets `real_time_data: true` on the response

Ruleset reference: LLM_GATEWAY_RULESET.md § 6.1, § 6.3
  "Every query response is enriched with current, accurate world data"
"""

import logging
import time
from typing import Optional

from engine.world.semantic_map import SemanticMap, SemanticEntry

logger = logging.getLogger("light-asi.enricher")

# Max world context items to attach per response
MAX_CONTEXT_ITEMS = 5
# Minimum token-overlap score to include an item
MIN_RELEVANCE_SCORE = 0.05


class QueryEnricher:
    """
    Wraps a raw graph query result with relevant real-world context.
    """

    def __init__(self, semantic_map: SemanticMap):
        self.semantic_map = semantic_map

    def enrich(self, query: str, graph_result: dict) -> dict:
        """
        Augment a graph_result dict with real-time world data.
        Returns an updated dict with `world_context` and `real_time_data: True`.

        Ruleset § 6.3 response format:
          answer, source_nodes, resonance_score, entropy_delta,
          real_time_data, timestamp + world_context (Phase 2 addition)
        """
        if not self.semantic_map.size:
            # No world data ingested yet
            graph_result["real_time_data"] = False
            graph_result["world_context"]  = []
            graph_result["world_note"]     = "World-net not yet ingested. Run 'ingest' first."
            return graph_result

        # Search semantic map
        matches = self.semantic_map.search(query, top_k=MAX_CONTEXT_ITEMS)

        world_context = []
        for entry in matches:
            world_context.append({
                "source":    entry.source,
                "title":     entry.title,
                "snippet":   entry.text[:200] + ("…" if len(entry.text) > 200 else ""),
                "url":       entry.url,
                "tags":      entry.tags,
                "ingested":  round(time.time() - entry.ingested_at, 1),
            })

        # Build grounded answer
        grounded_answer = self._ground_answer(
            base_answer=graph_result.get("answer", ""),
            query=query,
            context=matches,
        )

        graph_result["answer"]       = grounded_answer
        graph_result["real_time_data"] = len(world_context) > 0
        graph_result["world_context"]  = world_context
        graph_result["timestamp"]    = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        graph_result["semantic_map_size"] = self.semantic_map.size

        return graph_result

    def _ground_answer(
        self,
        base_answer: str,
        query: str,
        context: list[SemanticEntry],
    ) -> str:
        """
        Synthesise a response that incorporates world context.
        Phase 2 baseline: structured summary referencing live sources.
        Phase 3 will replace with full generation from the node graph.
        """
        if not context:
            return base_answer if base_answer else f"[no data found for: {query}]"

        # Lead with node graph answer if it has content
        lines = []
        if base_answer and base_answer != "[no stored tokens — index first]":
            lines.append(f"[Node Graph] {base_answer}")

        # Append world context
        lines.append(f"\n[World Context for: {query!r}]")
        for i, entry in enumerate(context[:3], 1):
            snippet = entry.text[:150].strip()
            if not snippet:
                snippet = entry.title
            lines.append(f"  {i}. [{entry.source.upper()}] {entry.title}")
            lines.append(f"     {snippet}")
            if entry.url:
                lines.append(f"     → {entry.url}")

        return "\n".join(lines)

    def summary(self) -> dict:
        return {
            "semantic_map_size":   self.semantic_map.size,
            "unique_tokens":       self.semantic_map.unique_tokens,
            "source_breakdown":    self.semantic_map.source_breakdown(),
            "total_ingested":      self.semantic_map.total_ingested,
        }
