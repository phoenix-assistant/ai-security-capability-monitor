"""Configuration loader for AISCM."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).parent.parent / "config"


def _load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def load_taxonomy() -> dict[str, Any]:
    return _load_yaml("taxonomy.yaml")


def load_models() -> dict[str, Any]:
    return _load_yaml("models.yaml")


def load_benchmarks() -> dict[str, Any]:
    return _load_yaml("benchmarks.yaml")


def get_config_dir() -> Path:
    return CONFIG_DIR
