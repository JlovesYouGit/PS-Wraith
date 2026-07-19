"""
semantic_map.py — Light-ASI LLM Gateway Phase 2
In-memory semantic map: meaning_hash → FeedItem metadata.

The semantic map stores every ingested world-net item hashed into the
10^48 string search space. At query time, tokens are matched against
stored items using token-overlap scoring (Phase 2 baseline).
Phase 3 will upgrade to embedding-based similarity.

Ruleset reference: LLM_GATEWAY_RULESET.md § 5.2, § 6.1
  "Build and continuously update a global semantic map"
  "Hash incoming data into the 10^48 string search space"
  "Index by meaning, not just token position"
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from engine.world.feeds import FeedItem
from engine.core.constants import ANCHOR_CONST

logger = logging.getLogger("light-asi.semantic_map")


# ─── Semantic Entry ───────────────────────────────────────────────────────────

@dataclass
class SemanticEntry:
    meaning_hash: str
    source: str
    title: str
    text: str
    url: str
    tags: list[str]
    ingested_at: float = field(default_factory=time.time)
    token_set: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self):
        if not self.token_set:
            self.token_set = frozenset(
                t.lower().strip(".,;:!?\"'()[]") 
                for t in (self.title + " " + self.text).split()
                if len(t) > 2
            )


# ─── Semantic Map ─────────────────────────────────────────────────────────────

class SemanticMap:
    """
    Global meaning-hash → SemanticEntry store.

    Indexing: uses 10^48 string search space via SHA3-512 projected to
    a 48-digit decimal index (approximation of 10^48).

    Ruleset § 5.2 — 'hash incoming data into the 10^48 string search space'
    """

    def __init__(self):
        # meaning_hash → SemanticEntry
        self._map: dict[str, SemanticEntry] = {}
        # inverted index: token → set of meaning_hashes
        self._token_index: dict[str, set[str]] = {}
        self._total_ingested: int = 0

    # ── Hashing ────────────────────────────────────────────────────────────

    @staticmethod
    def meaning_hash(text: str) -> str:
        """
        Project text into 10^48 space via SHA3-512 → 48-decimal index.
        Ruleset § 5.2.
        """
        raw = f"{ANCHOR_CONST}:{text}"
        full = hashlib.sha3_512(raw.encode("utf-8")).hexdigest()
        # Take first 48 hex chars → 48 decimal proxy (192 bits >> 10^48 ≈ 2^159)
        return full[:48]

    # ── Ingestion ──────────────────────────────────────────────────────────

    def ingest(self, item: FeedItem) -> str:
        """
        Hash item into semantic map. Returns the meaning_hash.
        Ruleset § 6.1 pipeline step 2: 'hash → node_select → semantic_index'
        """
        combined = item.full_text()
        mhash = self.meaning_hash(combined)

        if mhash in self._map:
            logger.debug(f"Duplicate item skipped: {mhash[:12]}…")
            return mhash

        entry = SemanticEntry(
            meaning_hash=mhash,
            source=item.source,
            title=item.title,
            text=item.text,
            url=item.url,
            tags=item.tags,
        )
        self._map[mhash] = entry

        # Update inverted index
        for token in entry.token_set:
            if token not in self._token_index:
                self._token_index[token] = set()
            self._token_index[token].add(mhash)

        self._total_ingested += 1
        logger.debug(f"Ingested: [{item.source}] {item.title[:50]}…")
        return mhash

    def ingest_many(self, items: list[FeedItem]) -> list[str]:
        return [self.ingest(item) for item in items]

    # ── Search ─────────────────────────────────────────────────────────────

    def search(self, query: str, top_k: int = 5) -> list[SemanticEntry]:
        """
        Token-overlap based search (Phase 2 baseline).
        Scores each entry by |query_tokens ∩ entry_tokens| / |query_tokens|.
        Phase 3 will replace with embedding cosine similarity.
        """
        query_tokens = frozenset(
            t.lower().strip(".,;:!?\"'()[]")
            for t in query.split()
            if len(t) > 2
        )
        if not query_tokens:
            return []

        # Candidate gathering via inverted index (fast path)
        candidate_hashes: dict[str, int] = {}
        for token in query_tokens:
            for mhash in self._token_index.get(token, set()):
                candidate_hashes[mhash] = candidate_hashes.get(mhash, 0) + 1

        if not candidate_hashes:
            return []

        # Score and rank
        scored = []
        for mhash, overlap_count in candidate_hashes.items():
            entry = self._map.get(mhash)
            if entry:
                score = overlap_count / max(len(query_tokens), 1)
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]

    def get(self, meaning_hash: str) -> Optional[SemanticEntry]:
        return self._map.get(meaning_hash)

    # ── Stats ──────────────────────────────────────────────────────────────

    @property
    def size(self) -> int:
        return len(self._map)

    @property
    def total_ingested(self) -> int:
        return self._total_ingested

    @property
    def unique_tokens(self) -> int:
        return len(self._token_index)

    def source_breakdown(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self._map.values():
            counts[entry.source] = counts.get(entry.source, 0) + 1
        return counts

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return (
            f"SemanticMap(entries={self.size}, "
            f"tokens={self.unique_tokens}, "
            f"ingested={self.total_ingested})"
        )
