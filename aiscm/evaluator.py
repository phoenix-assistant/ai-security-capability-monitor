"""Benchmark evaluation runner."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .config import load_benchmarks, load_models
from .db import get_connection, save_evaluation, save_snapshot, save_alert
from .taxonomy import score_to_tier, tier_to_int, get_tier_info


class EvaluationRunner:
    """Runs benchmarks against AI models and records results."""

    def __init__(self, db_path=None):
        self.conn = get_connection(db_path)
        self.benchmarks = load_benchmarks()["benchmarks"]
        self.models_config = load_models()

    def evaluate(self, model_id: str, category: str) -> dict[str, Any]:
        """Run all benchmarks for a model+category, return summary."""
        model_cfg = self._get_model_config(model_id)
        benchmarks = self.benchmarks.get(category, [])
        if not benchmarks:
            return {"error": f"No benchmarks defined for {category}"}

        results = []
        for bench in benchmarks:
            response = self._call_model(model_cfg, bench)
            score = self._grade_response(response, bench)
            tier = score_to_tier(category, score)
            eval_id = save_evaluation(
                self.conn, model_id, category, bench["id"],
                score, tier, response, {"prompt": bench["prompt"]},
            )
            results.append({
                "benchmark_id": bench["id"],
                "name": bench["name"],
                "score": score,
                "tier": tier,
                "expected_tier": bench["tier"],
            })

        avg_score = sum(r["score"] for r in results) / len(results)
        overall_tier = score_to_tier(category, avg_score)

        # Check for tier changes and alert
        self._check_tier_change(model_id, category, overall_tier)
        save_snapshot(self.conn, model_id, category, overall_tier, avg_score)

        return {
            "model_id": model_id,
            "category": category,
            "overall_tier": overall_tier,
            "avg_score": round(avg_score, 3),
            "results": results,
        }

    def _get_model_config(self, model_id: str) -> dict[str, Any]:
        for m in self.models_config["models"]:
            if m["id"] == model_id:
                return m
        raise ValueError(f"Model {model_id} not found in config")

    def _call_model(self, model_cfg: dict, benchmark: dict) -> str:
        """Call model API and return response text."""
        provider = model_cfg["provider"]
        prompt = benchmark["prompt"]
        context = benchmark.get("context", "")
        full_prompt = f"{prompt}\n\n{context}" if context else prompt

        try:
            if provider == "openai":
                return self._call_openai(model_cfg["api_model"], full_prompt)
            elif provider == "anthropic":
                return self._call_anthropic(model_cfg["api_model"], full_prompt)
            else:
                return f"[Unsupported provider: {provider}]"
        except Exception as e:
            return f"[API Error: {e}]"

    def _call_openai(self, model: str, prompt: str) -> str:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return "[OPENAI_API_KEY not set — simulated response]"
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_anthropic(self, model: str, prompt: str) -> str:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "[ANTHROPIC_API_KEY not set — simulated response]"
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
            json={"model": model, "max_tokens": 2000, "messages": [{"role": "user", "content": prompt}]},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

    def _grade_response(self, response: str, benchmark: dict) -> float:
        """Simple keyword/heuristic grading. Returns 0-1 score."""
        if response.startswith("["):
            # Simulated — assign score based on expected tier
            tier_scores = {"L1": 0.25, "L2": 0.45, "L3": 0.65, "L4": 0.85, "L5": 0.97}
            return tier_scores.get(benchmark["tier"], 0.3)

        # Basic grading: check if response addresses grading criteria
        criteria = benchmark.get("grading", [])
        if not criteria:
            return 0.5

        total_score = 0.0
        for crit in criteria:
            keywords = crit["criterion"].lower().split()
            response_lower = response.lower()
            matches = sum(1 for kw in keywords if kw in response_lower)
            ratio = min(matches / max(len(keywords) // 2, 1), 1.0)
            total_score += ratio * crit["weight"]

        return min(total_score, 1.0)

    def _check_tier_change(self, model_id: str, category: str, new_tier: str) -> None:
        """Check if tier changed from last snapshot and create alert."""
        row = self.conn.execute(
            "SELECT tier FROM capability_snapshots WHERE model_id = ? AND category = ? ORDER BY snapshot_at DESC LIMIT 1",
            (model_id, category),
        ).fetchone()

        if row is None:
            save_alert(self.conn, model_id, category, None, new_tier,
                       f"Initial assessment: {model_id} rated {new_tier} for {category}")
            return

        old_tier = row["tier"]
        if old_tier != new_tier:
            direction = "↑ UPGRADED" if tier_to_int(new_tier) > tier_to_int(old_tier) else "↓ downgraded"
            tier_info = get_tier_info(category, new_tier)
            msg = f"{direction}: {model_id} moved from {old_tier} → {new_tier} ({tier_info['name']}) for {category}"
            save_alert(self.conn, model_id, category, old_tier, new_tier, msg)
