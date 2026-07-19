"""
feeds.py — Light-ASI LLM Gateway Phase 2
Feed source definitions and raw fetching.

Sources (all free, no auth):
  - HackerNews Firebase API    (JSON)
  - Wikipedia Random Summary   (JSON REST)
  - arXiv new submissions      (Atom/XML RSS)
  - BBC World News             (RSS XML)
  - Reuters Top News           (RSS XML)

Ruleset reference: LLM_GATEWAY_RULESET.md § 6.1
  "The system MUST connect to and ingest live internet traffic/feeds"
"""

import json
import logging
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("light-asi.feeds")

# ─── Feed item ────────────────────────────────────────────────────────────────

@dataclass
class FeedItem:
    source: str
    title: str
    text: str
    url: str = ""
    tags: list[str] = field(default_factory=list)

    def full_text(self) -> str:
        return f"{self.title} {self.text}".strip()


# ─── HTTP helper ──────────────────────────────────────────────────────────────

_HEADERS = {
    "User-Agent": "Light-ASI/1.0 (academic research; github.com/light-asi)",
    "Accept": "application/json, application/xml, text/xml, */*",
}
_TIMEOUT = 8  # seconds


def _get(url: str) -> Optional[bytes]:
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.read()
    except Exception as e:
        logger.warning(f"Fetch failed [{url[:60]}]: {e}")
        return None


def _clean(text: str) -> str:
    """Strip HTML tags and normalise whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ─── HackerNews ───────────────────────────────────────────────────────────────

HN_TOP_URL   = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL  = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


def fetch_hackernews(limit: int = 10) -> list[FeedItem]:
    raw = _get(HN_TOP_URL)
    if not raw:
        return []
    try:
        ids = json.loads(raw)[:limit]
    except Exception:
        return []

    items = []
    for story_id in ids:
        raw_item = _get(HN_ITEM_URL.format(id=story_id))
        if not raw_item:
            continue
        try:
            d = json.loads(raw_item)
        except Exception:
            continue
        title = d.get("title", "")
        text  = _clean(d.get("text", ""))
        url   = d.get("url", "")
        if title:
            items.append(FeedItem(
                source="hackernews",
                title=title,
                text=text,
                url=url,
                tags=["tech", "news"],
            ))
    logger.info(f"HackerNews: fetched {len(items)} stories")
    return items


# ─── Wikipedia random summary ─────────────────────────────────────────────────

WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/random/summary"


def fetch_wikipedia(count: int = 5) -> list[FeedItem]:
    items = []
    for _ in range(count):
        raw = _get(WIKI_URL)
        if not raw:
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue
        title   = d.get("title", "")
        extract = d.get("extract", "")
        url     = d.get("content_urls", {}).get("desktop", {}).get("page", "")
        if title and extract:
            items.append(FeedItem(
                source="wikipedia",
                title=title,
                text=_clean(extract),
                url=url,
                tags=["encyclopedia", "knowledge"],
            ))
    logger.info(f"Wikipedia: fetched {len(items)} articles")
    return items


# ─── arXiv (Atom feed) ────────────────────────────────────────────────────────

ARXIV_URL = (
    "https://export.arxiv.org/api/query"
    "?search_query=all:neural+language+model"
    "&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
)
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def fetch_arxiv() -> list[FeedItem]:
    raw = _get(ARXIV_URL)
    if not raw:
        return []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        logger.warning(f"arXiv parse error: {e}")
        return []

    items = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        title   = (entry.findtext("atom:title",   "", ARXIV_NS) or "").strip()
        summary = (entry.findtext("atom:summary", "", ARXIV_NS) or "").strip()
        link    = ""
        for lnk in entry.findall("atom:link", ARXIV_NS):
            if lnk.get("type") == "text/html":
                link = lnk.get("href", "")
        if title:
            items.append(FeedItem(
                source="arxiv",
                title=_clean(title),
                text=_clean(summary),
                url=link,
                tags=["research", "ai", "ml"],
            ))
    logger.info(f"arXiv: fetched {len(items)} papers")
    return items


# ─── Generic RSS (BBC, Reuters, etc.) ─────────────────────────────────────────

RSS_SOURCES = {
    "bbc_world":  "https://feeds.bbci.co.uk/news/world/rss.xml",
    "bbc_tech":   "https://feeds.bbci.co.uk/news/technology/rss.xml",
}

RSS_NS = {
    "dc":      "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


def fetch_rss(source_name: str, url: str, limit: int = 10) -> list[FeedItem]:
    raw = _get(url)
    if not raw:
        return []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        logger.warning(f"RSS parse error [{source_name}]: {e}")
        return []

    channel = root.find("channel")
    if channel is None:
        channel = root

    items = []
    for item in channel.findall("item")[:limit]:
        title       = _clean(item.findtext("title", "") or "")
        description = _clean(item.findtext("description", "") or "")
        link        = item.findtext("link", "") or ""
        if title:
            items.append(FeedItem(
                source=source_name,
                title=title,
                text=description,
                url=link,
                tags=["news", source_name],
            ))
    logger.info(f"RSS [{source_name}]: fetched {len(items)} items")
    return items


def fetch_all_rss() -> list[FeedItem]:
    all_items = []
    for name, url in RSS_SOURCES.items():
        all_items.extend(fetch_rss(name, url))
    return all_items


# ─── Combined fetch ───────────────────────────────────────────────────────────

def fetch_all(
    hn_limit: int = 5,
    wiki_count: int = 3,
    arxiv: bool = True,
    rss: bool = True,
) -> list[FeedItem]:
    """Fetch from all sources and return a flat list of FeedItems."""
    items: list[FeedItem] = []
    items.extend(fetch_hackernews(hn_limit))
    items.extend(fetch_wikipedia(wiki_count))
    if arxiv:
        items.extend(fetch_arxiv())
    if rss:
        items.extend(fetch_all_rss())
    logger.info(f"World-net total: {len(items)} items fetched")
    return items
