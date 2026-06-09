"""
Compatibility entry point for the original carry model script name.

The public release no longer generates made-up macro or FX inputs from this
file. It delegates to the deterministic log-backed runner in `run_live_model.py`.
"""

from run_live_model import run_ensemble_model


def main() -> None:
    result = run_ensemble_model()
    print(result)


if __name__ == "__main__":
    main()
