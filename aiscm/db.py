"""SQLite database for storing evaluation results."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB = Path.home() / ".aiscm" / "results.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _init_tables(conn)
    return conn


def _init_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            category TEXT NOT NULL,
            benchmark_id TEXT NOT NULL,
            score REAL NOT NULL,
            tier TEXT NOT NULL,
            raw_response TEXT,
            grading_details TEXT,
            evaluated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS capability_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            category TEXT NOT NULL,
            tier TEXT NOT NULL,
            avg_score REAL NOT NULL,
            snapshot_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS research_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arxiv_id TEXT UNIQUE,
            title TEXT NOT NULL,
            authors TEXT,
            abstract TEXT,
            categories TEXT,
            relevance_score REAL,
            published_at TEXT,
            tracked_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT NOT NULL,
            category TEXT NOT NULL,
            old_tier TEXT,
            new_tier TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            acknowledged INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_eval_model ON evaluations(model_id, category);
        CREATE INDEX IF NOT EXISTS idx_snapshot_model ON capability_snapshots(model_id, category);
    """)


def save_evaluation(
    conn: sqlite3.Connection,
    model_id: str,
    category: str,
    benchmark_id: str,
    score: float,
    tier: str,
    raw_response: str | None = None,
    grading_details: dict | None = None,
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        """INSERT INTO evaluations (model_id, category, benchmark_id, score, tier, raw_response, grading_details, evaluated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (model_id, category, benchmark_id, score, tier, raw_response, json.dumps(grading_details) if grading_details else None, now),
    )
    conn.commit()
    return cur.lastrowid  # type: ignore[return-value]


def save_snapshot(conn: sqlite3.Connection, model_id: str, category: str, tier: str, avg_score: float) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO capability_snapshots (model_id, category, tier, avg_score, snapshot_at) VALUES (?, ?, ?, ?, ?)",
        (model_id, category, tier, avg_score, now),
    )
    conn.commit()


def get_latest_snapshots(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("""
        SELECT cs.* FROM capability_snapshots cs
        INNER JOIN (
            SELECT model_id, category, MAX(snapshot_at) as max_at
            FROM capability_snapshots GROUP BY model_id, category
        ) latest ON cs.model_id = latest.model_id AND cs.category = latest.category AND cs.snapshot_at = latest.max_at
        ORDER BY cs.model_id, cs.category
    """).fetchall()
    return [dict(r) for r in rows]


def get_model_history(conn: sqlite3.Connection, model_id: str, category: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM capability_snapshots WHERE model_id = ? AND category = ? ORDER BY snapshot_at",
        (model_id, category),
    ).fetchall()
    return [dict(r) for r in rows]


def save_alert(conn: sqlite3.Connection, model_id: str, category: str, old_tier: str | None, new_tier: str, message: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO alerts (model_id, category, old_tier, new_tier, message, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (model_id, category, old_tier, new_tier, message, now),
    )
    conn.commit()


def get_alerts(conn: sqlite3.Connection, unacknowledged_only: bool = False) -> list[dict[str, Any]]:
    q = "SELECT * FROM alerts"
    if unacknowledged_only:
        q += " WHERE acknowledged = 0"
    q += " ORDER BY created_at DESC"
    return [dict(r) for r in conn.execute(q).fetchall()]


def save_paper(conn: sqlite3.Connection, arxiv_id: str, title: str, authors: str, abstract: str, categories: str, relevance_score: float, published_at: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT OR IGNORE INTO research_papers (arxiv_id, title, authors, abstract, categories, relevance_score, published_at, tracked_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (arxiv_id, title, authors, abstract, categories, relevance_score, published_at, now),
    )
    conn.commit()


def get_papers(conn: sqlite3.Connection, limit: int = 50) -> list[dict[str, Any]]:
    return [dict(r) for r in conn.execute("SELECT * FROM research_papers ORDER BY tracked_at DESC LIMIT ?", (limit,)).fetchall()]
