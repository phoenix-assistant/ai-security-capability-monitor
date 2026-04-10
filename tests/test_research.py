"""Tests for research tracker."""

from aiscm.research import ResearchTracker


def test_relevance_scoring():
    tracker = ResearchTracker.__new__(ResearchTracker)
    score = tracker._score_relevance("AI Exploit Generation with LLMs", "Using GPT for vulnerability discovery and red teaming")
    assert score > 0.3

    low_score = tracker._score_relevance("Cooking recipes", "How to make pasta")
    assert low_score < 0.2
