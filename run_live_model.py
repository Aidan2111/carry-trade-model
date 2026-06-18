"""Compatibility wrapper for the packaged deterministic model runner."""

from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from carry_trade.modeling.runners.run_live_model import main, run_ensemble_model  # noqa: E402


if __name__ == "__main__":
    main()
