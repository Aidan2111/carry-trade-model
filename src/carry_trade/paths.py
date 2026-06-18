"""Shared repository paths for package modules."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = PROJECT_ROOT / "logs"

