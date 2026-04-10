"""Tests for database module."""

import sqlite3
import tempfile
from pathlib import Path

from aiscm.db import get_connection, save_evaluation, save_snapshot, get_latest_snapshots, save_alert, get_alerts, save_paper, get_papers


def _tmp_db():
    return get_connection(Path(tempfile.mktemp(suffix=".db")))


def test_connection_creates_tables():
    conn = _tmp_db()
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    assert "evaluations" in tables
    assert "capability_snapshots" in tables
    assert "alerts" in tables
    assert "research_papers" in tables


def test_save_and_get_evaluation():
    conn = _tmp_db()
    eid = save_evaluation(conn, "gpt-4o", "exploit-writing", "ew-01", 0.65, "L3", "test response")
    assert eid is not None
    row = conn.execute("SELECT * FROM evaluations WHERE id = ?", (eid,)).fetchone()
    assert row["model_id"] == "gpt-4o"
    assert row["score"] == 0.65


def test_snapshots():
    conn = _tmp_db()
    save_snapshot(conn, "gpt-4o", "exploit-writing", "L2", 0.45)
    save_snapshot(conn, "gpt-4o", "exploit-writing", "L3", 0.65)
    snaps = get_latest_snapshots(conn)
    assert len(snaps) == 1
    assert snaps[0]["tier"] == "L3"


def test_alerts():
    conn = _tmp_db()
    save_alert(conn, "gpt-4o", "exploit-writing", "L2", "L3", "Upgraded!")
    alerts = get_alerts(conn)
    assert len(alerts) == 1
    assert "Upgraded" in alerts[0]["message"]


def test_papers():
    conn = _tmp_db()
    save_paper(conn, "2401.12345", "AI Exploit Gen", "Author A", "Abstract", "cs.CR", 0.8, "2024-01-01")
    papers = get_papers(conn)
    assert len(papers) == 1
    assert papers[0]["arxiv_id"] == "2401.12345"


def test_duplicate_paper_ignored():
    conn = _tmp_db()
    save_paper(conn, "2401.12345", "Title", "A", "Abs", "cs.CR", 0.8, "2024-01-01")
    save_paper(conn, "2401.12345", "Title2", "B", "Abs2", "cs.CR", 0.9, "2024-01-02")
    papers = get_papers(conn)
    assert len(papers) == 1
