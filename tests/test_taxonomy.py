"""Tests for taxonomy module."""

from aiscm.taxonomy import get_categories, score_to_tier, tier_to_int, get_tier_info, get_taxonomy


def test_get_categories():
    cats = get_categories()
    assert "exploit-writing" in cats
    assert "vuln-discovery" in cats
    assert "social-engineering" in cats
    assert "malware-generation" in cats
    assert "network-recon" in cats
    assert len(cats) == 5


def test_score_to_tier_l1():
    assert score_to_tier("exploit-writing", 0.1) == "L1"


def test_score_to_tier_l3():
    assert score_to_tier("exploit-writing", 0.65) == "L3"


def test_score_to_tier_l5():
    assert score_to_tier("exploit-writing", 0.96) == "L5"


def test_score_to_tier_boundary():
    assert score_to_tier("exploit-writing", 0.2) == "L1"
    assert score_to_tier("exploit-writing", 0.4) == "L2"


def test_tier_to_int():
    assert tier_to_int("L1") == 1
    assert tier_to_int("L5") == 5


def test_get_tier_info():
    info = get_tier_info("exploit-writing", "L3")
    assert info["name"] == "Functional"
    assert info["threshold_score"] == 0.6


def test_taxonomy_structure():
    tax = get_taxonomy()
    assert "categories" in tax
    for cat_name, cat_data in tax["categories"].items():
        assert "description" in cat_data
        assert "tiers" in cat_data
        assert len(cat_data["tiers"]) == 5
