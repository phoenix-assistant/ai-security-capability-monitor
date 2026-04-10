"""Tests for config loader."""

from pathlib import Path
from aiscm.config import load_taxonomy, load_benchmarks, load_models, get_config_dir


def test_load_taxonomy():
    tax = load_taxonomy()
    assert "categories" in tax


def test_load_models():
    models = load_models()
    assert "models" in models
    assert len(models["models"]) >= 1


def test_load_benchmarks():
    bench = load_benchmarks()
    assert "benchmarks" in bench


def test_config_dir():
    d = get_config_dir()
    assert d.exists()
    assert (d / "taxonomy.yaml").exists()
