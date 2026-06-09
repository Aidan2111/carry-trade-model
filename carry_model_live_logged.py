"""
Compatibility entry point for the logged carry model workflow.

This wrapper keeps the historical file name available while delegating to the
deterministic log-backed runner used by the dashboard integration.
"""

from run_live_model import run_ensemble_model


def main() -> None:
    result = run_ensemble_model()
    print(result)


if __name__ == "__main__":
    main()
