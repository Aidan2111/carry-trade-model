"""
Compatibility entry point for the FX-keyed carry model workflow.

The historical script name is retained for users and old references, but the
public release uses deterministic provider/log-backed calculations.
"""

from run_live_model import run_ensemble_model


def main() -> None:
    result = run_ensemble_model()
    print(result)


if __name__ == "__main__":
    main()
