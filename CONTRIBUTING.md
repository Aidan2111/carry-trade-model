# Contributing

Contributions are welcome, especially improvements to reproducibility, data
provenance, model validation, API contracts, documentation, and accessibility.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[all,dev]"
cd frontend && npm ci && cd ..
```

## Required checks

```bash
python -m unittest discover -s tests -v
python scripts/system_evaluation.py
python -m build
python -m twine check dist/*
cd frontend && npm run build && npm audit
```

Keep research claims conservative. New data sources must document provenance,
licensing expectations, failure behavior, and required credentials. Never add
real secrets, fabricated live-market data, or default live-trading behavior.

Use a focused branch and pull request. Explain user-visible behavior, tests,
data/model risk, and documentation changes. See
`docs/process/branching-strategy.md` for the repository workflow.
