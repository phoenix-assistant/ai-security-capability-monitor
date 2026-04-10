"""Tests for evaluator (with simulated API responses)."""

import tempfile
from pathlib import Path

from aiscm.evaluator import EvaluationRunner
from aiscm.db import get_connection, get_alerts


def test_evaluate_simulated():
    db_path = Path(tempfile.mktemp(suffix=".db"))
    runner = EvaluationRunner(db_path=db_path)
    result = runner.evaluate("gpt-4o", "exploit-writing")
    assert result["model_id"] == "gpt-4o"
    assert result["category"] == "exploit-writing"
    assert result["overall_tier"] in ["L1", "L2", "L3", "L4", "L5"]
    assert 0 <= result["avg_score"] <= 1
    assert len(result["results"]) > 0

    # Should have created an alert for initial assessment
    conn = get_connection(db_path)
    alerts = get_alerts(conn)
    assert len(alerts) >= 1
