# Evaluation Results

This document records what the current automated checks establish and, just as
importantly, what they do not establish. The historical Phase 1 report was
removed because it mixed synthetic-data checks with production-readiness and
prediction-quality claims that the evidence did not support.

## Reproducible checks

Run from an environment installed with `.[all,dev]`:

```bash
python -m unittest discover -s tests -v
python scripts/system_evaluation.py
cd frontend
npm ci
npm run build
npm audit
```

The test suite covers:

- the Flask dashboard and model-update API contracts using injected providers;
- default-off mutation behavior for the model-update endpoint;
- forward seven-day target construction;
- a time-series validation control that reports no skill on pure noise;
- recovery of a deliberately planted signal;
- public entry points that avoid fabricated live data;
- safe local host, CORS, secret, and paper-trading defaults; and
- packaging, contributor-file, and repository-layout contracts.

`scripts/system_evaluation.py` makes three deterministic requests against the
application factory. It expects a healthy `/health` response, a dashboard
payload marked `REAL_DATA` with the canonical schema, and a `403` response from
the model-update endpoint when the opt-in gate is disabled.

The frontend build performs TypeScript checking and creates a production Vite
bundle. `npm audit` and the scheduled GitHub workflows separately cover known
dependency advisories; they do not prove the absence of vulnerabilities.

## Evidence boundary

These checks establish that the software contracts work under their tested
conditions and that the validation harness can distinguish noise from a planted
signal. They do **not** establish:

- profitable historical or live carry-trade performance;
- out-of-sample generalization to future market regimes;
- institutional data quality or execution realism;
- calibrated prediction intervals;
- production trading readiness; or
- suitability for investment decisions.

Synthetic fixtures are controls for the evaluation method, not market results.
Any future model-quality claim must identify the dataset, license, sampling
period, target, baselines, walk-forward protocol, transaction-cost assumptions,
and untouched evaluation window needed to reproduce it.

## Current release posture

Version `v0.1.0` is an alpha research and engineering release. Its supported
public surfaces are the local Flask API, React/TypeScript dashboard,
deterministic model runner, data collectors, and research experiments described
in the main README. Live trading remains disabled by default and outside the
supported release contract.
