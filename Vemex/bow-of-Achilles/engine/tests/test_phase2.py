"""
test_phase2.py — Light-ASI Phase 2 Tests
SemanticMap, feeds (offline mock), enricher, and ingester.
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from engine.world.feeds import FeedItem, _clean
from engine.world.semantic_map import SemanticMap
from engine.world.enricher import QueryEnricher
from engine.world.ingester import WorldIngester
from engine.core.graph import NodeGraph


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_item(source="test", title="Hello World", text="Some body text about AI."):
    return FeedItem(source=source, title=title, text=text, url="https://example.com", tags=["ai"])


# ─── FeedItem ─────────────────────────────────────────────────────────────────

class TestFeedItem:
    def test_full_text(self):
        item = make_item(title="Title", text="Body")
        assert "Title" in item.full_text()
        assert "Body" in item.full_text()

    def test_clean_strips_html(self):
        assert _clean("<b>hello</b>") == "hello"
        assert _clean("<p>foo <br/> bar</p>") == "foo bar"

    def test_clean_normalises_whitespace(self):
        assert _clean("a   b   c") == "a b c"


# ─── SemanticMap ──────────────────────────────────────────────────────────────

class TestSemanticMap:
    def test_ingest_and_retrieve(self):
        sm = SemanticMap()
        item = make_item(title="Neural Language Models", text="Transformers are powerful AI models.")
        mhash = sm.ingest(item)
        assert sm.get(mhash) is not None
        assert sm.size == 1

    def test_duplicate_skipped(self):
        sm = SemanticMap()
        item = make_item()
        sm.ingest(item)
        sm.ingest(item)
        assert sm.size == 1
        assert sm.total_ingested == 1

    def test_search_finds_relevant(self):
        sm = SemanticMap()
        sm.ingest(make_item(title="Deep Learning Research", text="neural networks and backpropagation"))
        sm.ingest(make_item(title="Cooking Recipes", text="pasta sauce tomato olive oil"))
        results = sm.search("neural networks")
        assert len(results) >= 1
        assert any("Deep Learning" in r.title for r in results)

    def test_search_empty_map(self):
        sm = SemanticMap()
        assert sm.search("anything") == []

    def test_meaning_hash_deterministic(self):
        h1 = SemanticMap.meaning_hash("hello world")
        h2 = SemanticMap.meaning_hash("hello world")
        assert h1 == h2

    def test_meaning_hash_length(self):
        h = SemanticMap.meaning_hash("test")
        assert len(h) == 48

    def test_ingest_many(self):
        sm = SemanticMap()
        items = [make_item(title=f"Article {i}", text=f"content about topic {i}") for i in range(5)]
        hashes = sm.ingest_many(items)
        assert len(hashes) == 5
        assert sm.size == 5

    def test_token_index_built(self):
        sm = SemanticMap()
        sm.ingest(make_item(title="quantum computing", text="qubits superposition entanglement"))
        assert "qubits" in sm._token_index or "quantum" in sm._token_index

    def test_source_breakdown(self):
        sm = SemanticMap()
        sm.ingest(make_item(source="hackernews"))
        sm.ingest(make_item(source="wikipedia", title="Different Article", text="different content here for hashing"))
        breakdown = sm.source_breakdown()
        assert "hackernews" in breakdown
        assert "wikipedia" in breakdown

    def test_unique_tokens_grows(self):
        sm = SemanticMap()
        before = sm.unique_tokens
        sm.ingest(make_item(title="unique token alpha beta gamma"))
        assert sm.unique_tokens > before


# ─── QueryEnricher ────────────────────────────────────────────────────────────

class TestQueryEnricher:
    def _base_result(self):
        return {
            "answer": "base answer",
            "source_nodes": [1, 2],
            "resonance_score": 0.5,
            "entropy_delta": 1.2,
            "real_time_data": False,
            "resonance_stable": False,
        }

    def test_enrich_empty_map(self):
        sm = SemanticMap()
        enricher = QueryEnricher(sm)
        result = enricher.enrich("test query", self._base_result())
        assert result["real_time_data"] is False
        assert result["world_context"] == []

    def test_enrich_with_data(self):
        sm = SemanticMap()
        sm.ingest(make_item(title="AI and machine learning", text="deep neural networks language models"))
        enricher = QueryEnricher(sm)
        result = enricher.enrich("machine learning", self._base_result())
        assert result["real_time_data"] is True
        assert len(result["world_context"]) >= 1

    def test_enriched_response_has_timestamp(self):
        sm = SemanticMap()
        sm.ingest(make_item(title="test item", text="some relevant test content here"))
        enricher = QueryEnricher(sm)
        result = enricher.enrich("test content", self._base_result())
        assert "timestamp" in result

    def test_summary(self):
        sm = SemanticMap()
        sm.ingest(make_item())
        enricher = QueryEnricher(sm)
        s = enricher.summary()
        assert "semantic_map_size" in s
        assert s["semantic_map_size"] == 1


# ─── WorldIngester ────────────────────────────────────────────────────────────

class TestWorldIngester:
    def test_run_once_with_mock_fetch(self, tmp_path):
        """run_once() with mocked fetch_all — no real network calls."""
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(5)
        sm = g.semantic_map
        ingester = WorldIngester(sm, g, interval=60)

        mock_items = [
            make_item(source="hackernews", title=f"Story {i}", text=f"tech news content {i}")
            for i in range(5)
        ]
        with patch("engine.world.ingester.fetch_all", return_value=mock_items):
            summary = ingester.run_once()

        assert summary["items_fetched"] == 5
        assert summary["items_indexed"] == 5
        assert summary["errors"] == 0
        assert sm.size == 5

    def test_metrics_updated(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(3)
        ingester = WorldIngester(g.semantic_map, g, interval=60)
        mock_items = [make_item(title=f"T{i}", text=f"body {i}") for i in range(3)]
        with patch("engine.world.ingester.fetch_all", return_value=mock_items):
            ingester.run_once()
        assert ingester.metrics.runs == 1
        assert ingester.metrics.total_fetched == 3

    def test_start_stop(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(3)
        ingester = WorldIngester(g.semantic_map, g, interval=60)
        with patch("engine.world.ingester.fetch_all", return_value=[]):
            ingester.start()
            assert ingester.is_running()
            ingester.stop()
            time.sleep(0.2)

    def test_interval_clamped(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(2)
        ingester = WorldIngester(g.semantic_map, g, interval=5)  # below MIN
        assert ingester.interval >= 30

    def test_status_structure(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(2)
        ingester = WorldIngester(g.semantic_map, g, interval=60)
        s = ingester.status()
        assert "running" in s
        assert "metrics" in s
        assert "semantic_map" in s


# ─── Graph + World Integration ────────────────────────────────────────────────

class TestPhase2GraphIntegration:
    def test_graph_query_enriched(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(10)
        g.semantic_map.ingest(make_item(
            title="language model consciousness",
            text="emergent properties of large neural networks",
        ))
        result = g.query("language consciousness")
        assert "world_context" in result

    def test_real_time_flag_true_after_ingest(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(5)
        g.semantic_map.ingest(make_item(
            title="real time data processing",
            text="streaming data pipelines and indexing systems",
        ))
        result = g.query("real time data")
        assert result["real_time_data"] is True

    def test_world_status(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(5)
        ws = g.world_status()
        assert "semantic_map_size" in ws

    def test_stats_includes_world_net(self, tmp_path):
        g = NodeGraph(backup_dir=tmp_path)
        g.bootstrap(5)
        s = g.stats()
        assert "world_net" in s
        assert "semantic_entries" in s["world_net"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
