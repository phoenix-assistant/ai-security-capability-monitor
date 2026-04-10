"""Research paper tracker — arXiv + security paper scraping."""

from __future__ import annotations

import re
from typing import Any

import feedparser
import httpx

from .db import get_connection, save_paper, get_papers

ARXIV_QUERY_TERMS = [
    "AI offensive security",
    "LLM vulnerability discovery",
    "AI exploit generation",
    "language model cybersecurity",
    "AI red teaming",
    "automated penetration testing LLM",
    "AI social engineering",
    "large language model malware",
]

ARXIV_API = "http://export.arxiv.org/api/query"


class ResearchTracker:
    def __init__(self, db_path=None):
        self.conn = get_connection(db_path)

    def fetch_arxiv(self, max_results: int = 20) -> list[dict[str, Any]]:
        """Fetch recent papers from arXiv matching security+AI terms."""
        query = " OR ".join(f'all:"{t}"' for t in ARXIV_QUERY_TERMS[:4])
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        try:
            resp = httpx.get(ARXIV_API, params=params, timeout=30)
            resp.raise_for_status()
        except Exception:
            return []

        feed = feedparser.parse(resp.text)
        papers = []
        for entry in feed.entries:
            arxiv_id = entry.id.split("/abs/")[-1]
            authors = ", ".join(a.get("name", "") for a in entry.get("authors", []))
            categories = ",".join(t.get("term", "") for t in entry.get("tags", []))
            relevance = self._score_relevance(entry.title, entry.get("summary", ""))

            save_paper(
                self.conn,
                arxiv_id=arxiv_id,
                title=entry.title,
                authors=authors,
                abstract=entry.get("summary", ""),
                categories=categories,
                relevance_score=relevance,
                published_at=entry.get("published", ""),
            )
            papers.append({
                "arxiv_id": arxiv_id,
                "title": entry.title,
                "relevance": relevance,
            })

        return papers

    def get_tracked_papers(self, limit: int = 50) -> list[dict[str, Any]]:
        return get_papers(self.conn, limit)

    def _score_relevance(self, title: str, abstract: str) -> float:
        """Simple keyword relevance scoring."""
        keywords = [
            "exploit", "vulnerability", "offensive", "red team", "penetration",
            "attack", "malware", "phishing", "social engineering", "zero-day",
            "llm", "gpt", "language model", "ai agent", "autonomous",
            "cybersecurity", "security evaluation", "capability",
        ]
        text = f"{title} {abstract}".lower()
        matches = sum(1 for kw in keywords if kw in text)
        return min(matches / 8, 1.0)
