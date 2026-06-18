"""Compatibility wrapper for the packaged improved ensemble model."""

from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from carry_trade.modeling.experiments.improved_ensemble_model import *  # noqa: E402,F401,F403
